import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import s3fs
import os

# Create connection object.
fs = s3fs.S3FileSystem(anon=False)

# Retrieve file contents.
@st.cache
def read_file(filename):
    with fs.open(filename) as f:
        return f.read().decode("utf-8")

content = read_file("streamlit-anomalis/myfile.csv")

pr_detail_infile = 'pr_2018_anomaly_details.csv'
pr_phys_infile = 'pr_2018_anomaly_physicians.csv'
rx_detail_infile = 'rx_2018_anomaly_details.csv'
rx_phys_infile = 'rx_2018_anomaly_physicians.csv'

states = ['AK', 'AL', 'AP', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL',
       'GA', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
       'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
       'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
       'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
sel_states = st.multiselect('Select states', states)

# load the data for selected states only
@st.cache
def filter_state(infile, states):
  df = pd.read_csv(infile)
  df = df.loc[df.state.isin(states), :]
  df['provider_key'] = df['npi'].astype(str) + '  /  ' + df['first_name'] + ' ' + df['last_name'] + '  /  ' + df['specialty']
  df.rename(columns = {'centroid_lat': 'lat', 'centroid_long': 'lon'}, inplace = True)
  df.index = [""] * len(df)
  return(df)
pr_phys = filter_state(pr_phys_infile, sel_states)

# filter down to selected specialties
@st.cache
def filter_specialty(df, specialties):
  df = df.loc[df.specialty.isin(specialties), :]
  return(df)
all = st.checkbox("Enable specialty filter")
if all:
  active_specialties = pr_phys.specialty.unique()
  sel_specialties = st.multiselect('Select specialties', active_specialties)
  pr_phys = filter_specialty(pr_phys, sel_specialties)

#px.set_mapbox_access_token(open(".mapbox_token").read())
fig = px.scatter_mapbox(pr_phys, lat="lat", lon="lon")
#, color="specialty", size="total_allowed", color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10
st.plotly_chart(fig)

# select an npi and cache results
provider_keys = pr_phys.groupby(['provider_key', 'total_allowed']).size().reset_index().sort_values(by = 'total_allowed', ascending = False)['provider_key'] 
sel_provider_key = st.selectbox('Select provider', provider_keys)
@st.cache
def filter_npi(df, provider_key):
  return(df[df.provider_key == provider_key])
pr_phys_one = filter_npi(pr_phys, sel_provider_key)

# display aggregate provider info
st.write(pr_phys_one.loc[:, ['first_name', 'last_name', 'specialty', 'state', 'total_billed', 'total_allowed']].style.set_precision(0))
