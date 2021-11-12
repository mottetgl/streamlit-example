import pandas as pd
import numpy as np
import streamlit as st

pr = pd.read_csv('pr_2018_anomaly_details.csv')
pr['key'] = pr['npi'].astype(str) + pr['first_name'] + pr['last_name']
states = np.unique(pr.state)

# select the state
sel_states = st.multiselect('Select States', states)
st.write(sel_states)

# limit to state and cache results
@st.cache
def filter_state(pr, states):
  return(pr[pr.state.isin(states)])

pr_states = filter_state(pr, states)
st.write(pr_states)

@st.cache
def filter_npi(pr, provider_key):
  return(pr[pr.provider_key == provider_key])
