import streamlit as st
from streamlit_theme import st_theme
import pandas as pd
import altair as alt
import firebase_admin
from firebase_admin import credentials, firestore
import os
from streamlit_extras.bottom_container import bottom
from ultimate import vegetableVsMarket
from ultimate2 import marketVsVegetable
import json

# page configuration
st.set_page_config(
    page_title='Vegetable Price Forecast System',
    page_icon='🥦',
    layout="wide",
    initial_sidebar_state="collapsed"
)

today = pd.Timestamp.today().replace(year=2023)
defaultStart = today.date() - pd.Timedelta(days=7)
defaultEnd = today.date() + pd.Timedelta(days=7)
st.html('./styles/ultimate.html')

# theme configuration
theme = st_theme()

base, primaryColor, div_color = 'dark', '#02ad39', '#262730'

if theme is not None:
    base = theme['base']
    primaryColor = theme['primaryColor']
    div_color = theme['secondaryBackgroundColor']

with open('./styles/ultimate.html', 'r') as f:
    css = f.read()

if base == 'light':
    maxColor = '#ffd5d4'
    minColor = '#bde7bd'
    maxText = '#460000'
    minText = '#013220'
elif base == 'dark':
    maxColor = '#460000'
    minColor = '#013220'
    maxText = '#ffd5d4'
    minText = '#bde7bd'

css = css.replace('maxColor', maxColor)
css = css.replace('minColor', minColor)

css = css.replace('divColor', div_color)
st.markdown(css, unsafe_allow_html=True)

# data loading
folder = './Data'
vegetables = sorted([f.split('.')[0] for f in [f for f in os.listdir(folder) if f.endswith('.csv')]][:-1])

# cached function to gather data from firebase and merge with existing data to get a series of dataframes
@st.cache_data(show_spinner=False)
def getVegetableData():
    if not firebase_admin._apps:

        firebase_credentials = {
            "type": st.secrets["firebase"]["type"],
            "project_id": st.secrets["firebase"]["project_id"],
            "private_key_id": st.secrets["firebase"]["private_key_id"],
            "private_key": st.secrets["firebase"]["private_key"],
            "client_email": st.secrets["firebase"]["client_email"],
            "client_id": st.secrets["firebase"]["client_id"],
            "auth_uri": st.secrets["firebase"]["auth_uri"],
            "token_uri": st.secrets["firebase"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
            "universe_domain": st.secrets["firebase"]["universe_domain"]
        }

        cred = credentials.Certificate(firebase_credentials)
        firebase_admin.initialize_app(cred)
    db = firestore.client()

    docs = db.collection('Data').stream()
    firebaseData = pd.DataFrame([doc.to_dict() for doc in docs])

    dataframes = {}
    for vegetable in vegetables:
        markets = [column for column in firebaseData.columns if vegetable in column]
        firebaseTempData = firebaseData[['Date'] + markets].copy()
        firebaseTempData['Date'] = pd.to_datetime(firebaseTempData['Date'], format='%d %B %Y at %H:%M:%S %Z%z', errors='coerce', utc=True).dt.date
        for market in markets:
            firebaseTempData.rename(columns={market: market.split('_')[0]}, inplace=True)

        githubData = pd.read_csv(f'{folder}/{vegetable}.csv')
        githubData['Date'] = pd.to_datetime(githubData['Date']).dt.date

        dataframes[vegetable] = pd.concat([githubData, firebaseTempData], axis=0)
    
    return dataframes

# cached function to convert vegetable data to market data
@st.cache_data(show_spinner=False)
def getMarketData(vegetableData):
    marketData = {}
    for vegetable in vegetables:
        dataframe = vegetableData[vegetable]
        for market in dataframe.columns[1:]:
            if market not in marketData:
                marketData[market] = pd.DataFrame()
                marketData[market]['Date'] = dataframe['Date']
            marketData[market][vegetable] = dataframe[market]
    return marketData

with st.sidebar:
    st.title('Vegetable Price Forecast System')
    st.markdown('---')
    view = st.radio('Select View', ['Market Prices of Vegetables', 'Vegetable Prices in Markets'])
    st.markdown('---')
    language = st.selectbox('Select Language', ['English', 'Sinhala', 'Tamil'])

with st.spinner("You are the first customer of the day!\nPlease wait until we set things up for you"):
    vegetableDataframes = getVegetableData()
    marketDataframes = getMarketData(vegetableDataframes)
    markets = list(marketDataframes.keys())

# Load translations based on selected language
if language == 'Sinhala':
    with open('./languages/sinhala.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)
elif language == 'Tamil':
    with open('./languages/tamil.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)
else:
    translations = {}

# Translate vegetables and markets
translatedVegetables = [translations.get(vegetable, vegetable) for vegetable in vegetables]
translatedMarkets = [translations.get(market, market) for market in markets]

# Update the vegetable and market dataframes with translated names
translated_vegetableDataframes = {}
for veg, df in vegetableDataframes.items():
    # Rename the columns using the translations
    new_columns = {col: translations.get(col, col) for col in df.columns[1:]}
    df.rename(columns=new_columns, inplace=True)
    translated_vegetableDataframes[translations.get(veg, veg)] = df

translated_marketDataframes = {}
for market, df in marketDataframes.items():
    # Rename the columns using the translations
    new_columns = {col: translations.get(col, col) for col in df.columns[1:]}
    df.rename(columns=new_columns, inplace=True)
    translated_marketDataframes[translations.get(market, market)] = df

if view == 'Market Prices of Vegetables':
    vegetableVsMarket(today, defaultStart, defaultEnd, translatedVegetables, translated_vegetableDataframes, primaryColor, translations)
elif view == 'Vegetable Prices in Markets':
    marketVsVegetable(today, defaultStart, defaultEnd, translatedMarkets, translated_marketDataframes, primaryColor, translations)

with bottom():
    st.markdown('---')
    message = 'Prices from today onward (including today) are forecasted based on historical data and may not reflect real-time market values. We advise caution in placing excessive reliance on these data'
    message = translations.get(message, message)
    st.write(message)