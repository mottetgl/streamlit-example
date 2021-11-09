import pandas as pd
import numpy as np
import streamlit as st

pr = pd.read_csv('pr_2018_anomaly_details.csv')
states = np.unique(pr.state)

sel_states = st.multiselect('Select', states)

pr = pr[pr.state.isin(sel_states)]

st.selectbox('Pick one', ['cats', 'dogs', 'foxes', 'hounds', 'ants', 'polar bears', '123456', '44444 john doe'])
