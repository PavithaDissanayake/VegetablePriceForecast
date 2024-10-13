import streamlit as st
import pandas as pd
from helper.data import getVegetableData, getMarketData, forecast
from helper.forecastTab import forecastTab
from helper.historicalTab import historicalTab

# page configuration
st.set_page_config(
    page_title='Vegetable Price Forecast System for Consumers',
    page_icon='🥦',
    layout="wide",
    initial_sidebar_state="collapsed"
)
st.html('./styles/View.html')
inverse = st.sidebar.toggle('Inverse View', False)

# date configuration
today = pd.Timestamp('2023-12-29')

# collecting data
with st.spinner("Fetching data..."):
    vegetables, vegetableDataframes = getVegetableData()

for vegetable in vegetables:
    with st.spinner(f"Forecasting {vegetables.index(vegetable)+1}/{len(vegetables)} vegetable prices..."):
        vegetableDataframes[vegetable] = forecast(vegetable, vegetableDataframes[vegetable])

markets, marketDataframes = getMarketData(vegetableDataframes)

tabs = st.tabs(['Forecasts', 'Historical Data', 'Insights'])

with tabs[0]:
    if inverse:
        forecastTab(vegetableDataframes, vegetables, marketDataframes, markets, 'Vegetable', 'Market', today, inverse, False)
    else:
        forecastTab(marketDataframes, markets, vegetableDataframes, vegetables, 'Market', 'Vegetable', today, inverse, False)

with tabs[1]:
    if inverse:
        historicalTab(marketDataframes, markets, 'Market', 'Vegetable', today, inverse)
    else:
        historicalTab(vegetableDataframes, vegetables, 'Vegetable', 'Market', today, inverse)