import streamlit as st
import pandas as pd
from helper.data import getVegetableData, getMarketData, forecast, useNewData
from helper.forecastTab import forecastTab
from helper.historicalTab import historicalTab
import json

# page configuration
st.set_page_config(
    page_title='Vegetable Price Forecast System for Consumers',
    page_icon='🥦',
    layout="wide",
    initial_sidebar_state="collapsed"
)
st.html('./styles/View.html')

if 'language' not in st.session_state:
    st.session_state['language'] = 'English'

language = {}
if st.session_state['language'] == 'සිංහල':
    with open('./languages/sinhala.json', 'r', encoding='utf-8') as file:
        language = json.load(file)
elif st.session_state['language'] == 'தமிழ்':
    with open('./languages/tamil.json', 'r', encoding='utf-8') as file:
        language = json.load(file)

inverse = st.sidebar.toggle(language.get('Inverse View', 'Inverse View'), False)

newlang = st.sidebar.selectbox(
    language.get('Select the Language', 'Select the Language'),
    ['English', 'සිංහල', 'தமிழ்'],
    index=['English', 'සිංහල', 'தமிழ்'].index(st.session_state['language'])  # Maintain the previous selection
)

if newlang != st.session_state['language']:
    st.session_state['language'] = newlang
    st.rerun()

# date configuration
today = pd.Timestamp.now()

# collecting data
with st.spinner(language.get('Fetching data...', 'Fetching data...')):
    vegetables, vegetableDataframes = getVegetableData()

markets = vegetableDataframes[vegetables[0]].columns[1:-1]
vegetableDataframes[vegetables[0]]['Date'] = pd.to_datetime(vegetableDataframes[vegetables[0]]['Date']).dt.date
maxDate = vegetableDataframes[vegetables[0]]['Date'].max()

if maxDate != today.date():
    with st.spinner(language.get('Fetching new data...', 'Fetching new data...')):
        vegetables, vegetableDataframes = useNewData(maxDate.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'), vegetables, markets.to_list())

for vegetable in vegetables:
    with st.spinner(f"{language.get('Vegetable prices forecasting', 'Vegetable prices forecasting')} {vegetables.index(vegetable)+1}/{len(vegetables)}..."):
        vegetableDataframes[vegetable] = forecast(vegetable, vegetableDataframes[vegetable])

markets, marketDataframes = getMarketData(vegetableDataframes)

tabs = st.tabs([language.get('Forecasts', 'Forecasts'), language.get('Historical Data', 'Historical Data')])

with tabs[0]:
    if inverse:
        forecastTab(vegetableDataframes, vegetables, marketDataframes, markets, 'Vegetable', 'Market', today, language, inverse, False)
    else:
        forecastTab(marketDataframes, markets, vegetableDataframes, vegetables, 'Market', 'Vegetable', today, language, inverse, False)

with tabs[1]:
    if inverse:
        historicalTab(marketDataframes, markets, 'Market', 'Vegetable', today, language, inverse)
    else:
        historicalTab(vegetableDataframes, vegetables, 'Vegetable', 'Market', today, language, inverse)
