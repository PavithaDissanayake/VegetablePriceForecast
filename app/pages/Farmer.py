import streamlit as st
import pandas as pd
from helper.data import getVegetableData, getMarketData, forecast, useNewData
from helper.forecastTab import forecastTab
from helper.historicalTab import historicalTab
import json

# Configure the page for the Consumer's dashboard view
st.set_page_config(
    page_title='Vegetable Price Forecast System for Farmers',
    page_icon='🥦',
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load HTML styles for the main view
st.html('./styles/View.html')

# Set the default language if not already in session state
if 'language' not in st.session_state:
    st.session_state['language'] = 'English'

# Load language data based on current session language
language = {}
if st.session_state['language'] == 'සිංහල':
    with open('./languages/sinhala.json', 'r', encoding='utf-8') as file:
        language = json.load(file)
elif st.session_state['language'] == 'தமிழ்':
    with open('./languages/tamil.json', 'r', encoding='utf-8') as file:
        language = json.load(file)

# Toggle option for inverse view in the sidebar
inverse = st.sidebar.toggle(language.get('Inverse View', 'Inverse View'), False)

# Sidebar language selection dropdown
newlang = st.sidebar.selectbox(
    language.get('Select the Language', 'Select the Language'),
    ['English', 'සිංහල', 'தமிழ்'],
    index=['English', 'සිංහල', 'தமிழ்'].index(st.session_state['language'])  # Maintain the previous selection
)

# Update session language if a new one is selected, and rerun the app
if newlang != st.session_state['language']:
    st.session_state['language'] = newlang
    st.rerun()

# Current date for data management
today = pd.Timestamp.now()

# Data fetching with loading message
with st.spinner(language.get('Fetching data...', 'Fetching data...')):
    vegetables, vegetableDataframes = getVegetableData()

# Identify available markets and format the date column to only include dates
markets = vegetableDataframes[vegetables[0]].columns[1:-1]
vegetableDataframes[vegetables[0]]['Date'] = pd.to_datetime(vegetableDataframes[vegetables[0]]['Date']).dt.date
maxDate = vegetableDataframes[vegetables[0]]['Date'].max()

# If the latest data is outdated, fetch new data to bring it up to date
if maxDate != today.date():
    with st.spinner(language.get('Fetching new data...', 'Fetching new data...')):
        vegetables, vegetableDataframes = useNewData(maxDate.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'), vegetables, markets.to_list())

# Run forecasting for each vegetable with a loading spinner message
for vegetable in vegetables:
    with st.spinner(f"{language.get('Vegetable prices forecasting', 'Vegetable prices forecasting')} {vegetables.index(vegetable)+1}/{len(vegetables)}..."):
        vegetableDataframes[vegetable] = forecast(vegetable, vegetableDataframes[vegetable])

# Collect updated market data
markets, marketDataframes = getMarketData(vegetableDataframes)

# Create tabs for Forecasts and Historical Data views
tabs = st.tabs([language.get('Forecasts', 'Forecasts'), language.get('Historical Data', 'Historical Data')])

# Set up the Forecast tab with inverse view toggle support
with tabs[0]:
    if inverse:
        forecastTab(vegetableDataframes, vegetables, marketDataframes, markets, 'Vegetable', 'Market', today, language, inverse, True)
    else:
        forecastTab(marketDataframes, markets, vegetableDataframes, vegetables, 'Market', 'Vegetable', today, language, inverse, True)

# Set up the Historical Data tab with inverse view toggle support
with tabs[1]:
    if inverse:
        historicalTab(marketDataframes, markets, 'Market', 'Vegetable', today, language, inverse)
    else:
        historicalTab(vegetableDataframes, vegetables, 'Vegetable', 'Market', today, language, inverse)