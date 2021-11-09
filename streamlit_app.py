import pandas as pd
import numpy as np
import streamlit as st

pr = pd.read_csv('pr_2018_anomaly_details.csv')
states = np.unique(pr.state)

sel_states = st.multiselect('Select', states)

pr = pr[pr.state.isin(sel_states)]
pr['provider_key'] = pr['npi'] + pr['first_name'] + pr['last_name'] + pr['specialty']
keys = np.unique(pr.provider_Key)

sel_provider_key = st.selectbox('Pick one', keys)

pr = pr[pr.provider_key == sel_provider_key]
