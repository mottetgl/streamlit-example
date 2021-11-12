import pandas as pd
import numpy as np
import streamlit as st

pr = pd.read_csv('pr_2018_anomaly_details.csv')
pr['provider_key'] = pr['npi'].astype(str) + pr['first_name'] + pr['last_name']

# select the state and chache results
states = np.unique(pr.state)
sel_states = st.multiselect('Select states', states)
@st.cache
def filter_state(pr, states):
  return(pr[pr.state.isin(states)])

pr_state = filter_state(pr, states)
st.write(pr_state)

# select an npi and cache results
provider_keys = np.unique(pr_state.provider_key)
sel_provider_key = st.selectbox('Select provider', provider_keys)
@st.cache
def filter_npi(pr, provider_key):
  return(pr[pr.provider_key == provider_key])

pr_npi = filter_npi(pr_state, sel_provider_key)
st.write(pr_npi)
