import pandas as pd
import numpy as np
import streamlit as st

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
  return(df)
pr_phys = filter_state(pr_phys_infile, sel_states)
st.write(pr_phys)

# select an npi and cache results
provider_keys = pr_phys.groupby(['provider_key', 'total_allowed']).size().reset_index().sort_values(by = 'npi_allowed', ascending = False)['provider_key'] 
sel_provider_key = st.selectbox('Select provider', provider_keys)
@st.cache
def filter_npi(df, provider_key):
  return(df[df.provider_key == provider_key])
pr_phys_one = filter_npi(pr_phys, sel_provider_key)

st.write(pr_phys_one)
