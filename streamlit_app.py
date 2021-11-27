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
  df.index = [""] * len(df)
  return(df)
pr_detail = pull_pr_detail(pr_detail_infile)

sel_states = st.multiselect('Select states', states)

# ---------------------------------------------------------------------------------------------------------------------------
# filter the physician table ------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------
# filter on state
@st.cache
def pull_pr_phys_state(filename, states):
  df = pd.read_csv(fs.open(filename))
  df = df.loc[df.state.isin(states), :]
  df['provider_key'] = df['npi'].astype(str) + '  /  ' + df['first_name'] + ' ' + df['last_name'] + '  /  ' + df['specialty']
  df = df[-df.zip.isna()] # REMINDER!!! EXCLUDING ROWS WITHOUT A ZIP CODE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  df.index = [""] * len(df)
  return(df)
pr_phys = pull_pr_phys_state(pr_phys_infile, sel_states)

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

# ---------------------------------------------------------------------------------------------------------------------------
# plot scatter mapbox -------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------
px.set_mapbox_access_token(st.secrets["MAPBOX_TOKEN"])
st.write(st.secrets["MAPBOX_TOKEN"])
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
        '<br>',
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
st.write(pr_phys_one.loc[:, ['first_name', 'last_name', 'specialty', 'state', 'total_billed', 'total_allowed']].style.set_precision(0))

@st.cache
def pull_pr_detail_npi(df, provider_key):
  df = df[df.provider_key == provider_key]
  df.index = [""] * len(df)
  return(df)
pr_detail_one = pull_pr_detail_npi(pr_detail, sel_provider_key)
st.write(pr_detail_one)

