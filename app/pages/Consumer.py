import streamlit as st
import pandas as pd
from helper.data import getVegetableData, getMarketData, forecast, useNewData
from helper.forecastTab import forecastTab
from helper.historicalTab import historicalTab
import json

# Configure the page settings for the Farmer's dashboard view
st.set_page_config(
    page_title='Vegetable Price Forecast System for Consumers',
    page_icon='🥦',
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load HTML styling for the main view
st.html('./styles/View.html')

# Set the default language in session state if not already set
if 'language' not in st.session_state:
    st.session_state['language'] = 'English'

# Initialize language dictionary based on session state selection
language = {}
if st.session_state['language'] == 'සිංහල':
    with open('./languages/sinhala.json', 'r', encoding='utf-8') as file:
        language = json.load(file)
elif st.session_state['language'] == 'தமிழ்':
    with open('./languages/tamil.json', 'r', encoding='utf-8') as file:
        language = json.load(file)

# Sidebar options for toggling inverse view and selecting language
inverse = st.sidebar.toggle(language.get('Inverse View', 'Inverse View'), False)

# Language selection box in the sidebar with the previous selection as the default
newlang = st.sidebar.selectbox(
    language.get('Select the Language', 'Select the Language'),
    ['English', 'සිංහල', 'தமிழ்'],
    index=['English', 'සිංහල', 'தமிழ்'].index(st.session_state['language'])  # Maintain the previous selection
)

# Update language if a new one is selected and rerun the app
if newlang != st.session_state['language']:
    st.session_state['language'] = newlang
    st.rerun()

# Get the current date for the data configuration
today = pd.Timestamp.now()

# Fetch vegetable data with a loading spinner message
with st.spinner(language.get('Fetching data...', 'Fetching data...')):
    vegetables, vegetableDataframes = getVegetableData()

# Extract available markets and convert the date column to only include dates (no time)
markets = vegetableDataframes[vegetables[0]].columns[1:-1]
vegetableDataframes[vegetables[0]]['Date'] = pd.to_datetime(vegetableDataframes[vegetables[0]]['Date']).dt.date
maxDate = vegetableDataframes[vegetables[0]]['Date'].max()

# Check if data is current; if not, fetch new data
if maxDate != today.date():
    with st.spinner(language.get('Fetching new data...', 'Fetching new data...')):
        vegetables, vegetableDataframes = useNewData(maxDate.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'), vegetables, markets.to_list())

# Perform forecasting for each vegetable with a loading spinner message
for vegetable in vegetables:
    with st.spinner(f"{language.get('Vegetable prices forecasting', 'Vegetable prices forecasting')} {vegetables.index(vegetable)+1}/{len(vegetables)}..."):
        vegetableDataframes[vegetable] = forecast(vegetable, vegetableDataframes[vegetable])

# Fetch market data based on updated vegetable data
markets, marketDataframes = getMarketData(vegetableDataframes)

# Set up tabs for Forecasts and Historical Data views
tabs = st.tabs([language.get('Forecasts', 'Forecasts'), language.get('Historical Data', 'Historical Data')])

# Forecast tab setup with inverse view toggle support
with tabs[0]:
    if inverse:
        forecastTab(vegetableDataframes, vegetables, marketDataframes, markets, 'Vegetable', 'Market', today, language, inverse, False)
    else:
        forecastTab(marketDataframes, markets, vegetableDataframes, vegetables, 'Market', 'Vegetable', today, language, inverse, False)

# Historical Data tab setup with inverse view toggle support
with tabs[1]:
    if inverse:
        historicalTab(marketDataframes, markets, 'Market', 'Vegetable', today, language, inverse)
    else:
        historicalTab(vegetableDataframes, vegetables, 'Vegetable', 'Market', today, language, inverse)
