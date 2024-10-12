import streamlit as st

st.set_page_config(
    page_title='Vegetable Price Forecast System for Farmers',
    page_icon='🥦',
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.tabs(['Historical Data', 'Forecast', 'Insights'])

