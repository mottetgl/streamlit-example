import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import s3fs
import os

# Create connection object.
fs = s3fs.S3FileSystem(anon=False)

pr_detail_infile = 'streamlit-anomalis/streamlit_pr_2018_anomaly_details.csv'
pr_phys_infile = 'streamlit-anomalis/streamlit_pr_2018_anomaly_physicians.csv'
rx_detail_infile = 'streamlit-anomalis/streamlit_rx_2018_anomaly_details.csv'
rx_phys_infile = 'streamlit-anomalis/streamlit_rx_2018_anomaly_physicians.csv'

states = ['AK', 'AL', 'AP', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL',
       'GA', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
       'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
       'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
       'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']

# ---------------------------------------------------------------------------------------------------------------------------
# load the full physician detail file ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------
@st.cache
def pull_pr_detail(filename):
  df = pd.read_csv(fs.open(filename))
  df['provider_key'] = df['npi'].astype(str) + '  /  ' + df['first_name'] + ' ' + df['last_name'] + '  /  ' + df['specialty']
  df['hcpcs_key'] = df['hcpcs_code'].astype(str) + ':  ' + df['hcpcs_desc']
  df['trunc_hcpcs_key'] = df['hcpcs_key'].apply(lambda x: x if len(x) < 35 else x[:35] + '...')
  df.index = [""] * len(df)
  return(df)
pr_detail = pull_pr_detail(pr_detail_infile)

@st.cache
def pull_pr_phys(filename):
  df = pd.read_csv(fs.open(filename))
  df['provider_key'] = df['npi'].astype(str) + '  /  ' + df['first_name'] + ' ' + df['last_name'] + '  /  ' + df['specialty']
  df.index = [""] * len(df)
  return(df)
pr_phys = pull_pr_phys(pr_phys_infile)

# ---------------------------------------------------------------------------------------------------------------------------
# filter the physician table ------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------
# filter on state
sel_states = st.multiselect('Select states', states)
@st.cache
def pr_filter_state(df, states):
  df = df.loc[df.state.isin(states), :]
  df = df[-df.zip.isna()] # REMINDER!!! EXCLUDING ROWS WITHOUT A ZIP CODE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  return(df)
pr_phys = pr_filter_state(pr_phys, sel_states)

# filter on specialty
@st.cache
def filter_specialty(df, specialties):
  df = df.loc[df.specialty.isin(specialties), :]
  return(df)
checked = st.checkbox("Enable specialty filter")
if checked:
  active_specialties = pr_phys.specialty.unique()
  sel_specialties = st.multiselect('Select specialties', active_specialties)
  pr_phys = filter_specialty(pr_phys, sel_specialties)

st.write(pr_phys)

# add option to download the data
st.download_button(
    label="Download selected anomalies as CSV",
    data=pr_phys.to_csv().encode('utf-8'),
    file_name='selected_anomalous_providers.csv',
    mime='text/csv',
)
# ---------------------------------------------------------------------------------------------------------------------------
# plot scatter mapbox -------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------
px.set_mapbox_access_token(st.secrets["MAPBOX_TOKEN"])
fig = px.scatter_mapbox(pr_phys,
                        lat = pr_phys.centroid_lat,
                        lon = pr_phys.centroid_lon,
                        size = 'total_allowed',
                        custom_data = ['first_name', 'last_name', 'specialty', 'provider_city', 'state', 'provider_zip', 'provider_street1', 'total_billed', 'total_allowed'],
                        zoom=1)
fig.update_traces(
    hovertemplate='<br>'.join([
        'Name:      %{customdata[0]} %{customdata[1]}',
        'Specialty: %{customdata[2]}',
        'Location:  %{customdata[3]}, %{customdata[4]} %{customdata[5]}',
        'Street:      %{customdata[6]}',
        '',
        'Total Billed:  $%{customdata[7]:,.0f}',
        'Total Allowed: $%{customdata[8]:,.0f}',
    ])
)
st.plotly_chart(fig, use_container_width = True)

# ---------------------------------------------------------------------------------------------------------------------------
# show detail for one npi ---------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------
# select an npi
provider_keys = pr_phys.groupby(['provider_key', 'total_allowed']).size().reset_index().sort_values(by = 'total_allowed', ascending = False)['provider_key'] 
sel_provider_key = st.selectbox('Select provider', provider_keys)
@st.cache
def pull_pr_phys_npi(df, provider_key):
  return(df[df.provider_key == provider_key])
pr_phys_one = pull_pr_phys_npi(pr_phys, sel_provider_key)

# display aggregate provider info
st.write(pr_phys_one.loc[:, ['first_name', 'last_name', 'specialty', 'state', 'total_billed', 'total_allowed']].style.format(precision=0))

@st.cache
def pull_pr_detail_npi(df, provider_key):
  df = df[df.provider_key == provider_key]
  df.sort_values(by = 'total_allowed', inplace = True)
  df.index = [""] * len(df)
  return(df)
pr_detail_one = pull_pr_detail_npi(pr_detail, sel_provider_key)
st.write(pr_detail_one)

# ---------------------------------------------------------------------------------------------------------------------------
# create anomaly details barchart -------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------
fig = px.bar(pr_detail_one,
             x='total_allowed',
             y='trunc_hcpcs_key',
             color='spec_quantile',
             color_continuous_scale='turbo',
             custom_data = ['hcpcs_code', 'hcpcs_desc', 'total_billed', 'total_allowed', 'norm_allowed'],
             range_color=[0, 1]
             )
fig.update_traces(
    hovertemplate='<br>'.join([
        'HCPCS Code: %{customdata[0]}',
        'HCPCS Desc: %{customdata[1]}',
        '',
        'Total Billed:  $%{customdata[2]:,.0f}',
        'Total Allowed: $%{customdata[3]:,.0f}',
        'Specialty Average Allowed: $%{customdata[4]:,.0f}',
    ])
)
st.plotly_chart(fig)

