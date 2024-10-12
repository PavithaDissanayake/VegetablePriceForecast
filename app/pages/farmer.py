import streamlit as st
from streamlit_extras.mandatory_date_range import date_range_picker
from streamlit_extras.grid import grid
import pandas as pd
import altair as alt
from Apex import apex_chart
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, firestore
import os
import pickle
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras import models # type: ignore

# page configuration
st.set_page_config(
    page_title='Vegetable Price Forecast System for Farmers',
    page_icon='🥦',
    layout="wide",
    initial_sidebar_state="collapsed"
)
st.html('./styles/View.html')

# date configuration
today = pd.Timestamp('2023-12-29')

# data collection
folder = './Data/NewData'
vegetables = [f.split('.')[0] for f in os.listdir(folder) if f.endswith('.csv')]

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

    docs = db.collection('NewData').stream()
    firebaseData = pd.DataFrame([doc.to_dict() for doc in docs])

    vegetableDataframes = {}
    for vegetable in vegetables:
        markets = [column for column in firebaseData.columns if vegetable in column]
        firebaseTempData = firebaseData[['Date'] + markets].copy()
        firebaseTempData['Date'] = pd.to_datetime(firebaseTempData['Date'], format='%d %B %Y at %H:%M:%S %Z%z', errors='coerce', utc=True).dt.date
        for market in markets:
            firebaseTempData.rename(columns={market: market.split('_')[0]}, inplace=True)

        githubData = pd.read_csv(f'{folder}/{vegetable}.csv')
        githubData['Date'] = pd.to_datetime(githubData['Date']).dt.date

        vegetableDataframes[vegetable] = pd.concat([githubData, firebaseTempData], axis=0)
        vegetableDataframes[vegetable]['Date'] = pd.to_datetime(vegetableDataframes[vegetable]['Date']).dt.date
    
    return vegetableDataframes

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

@st.cache_data(show_spinner=False)
def forecast(vegetable, df):
    
    shift = 30
    df['Buy Rate Lagged'] = df['Buy Rate'].shift(shift)
    future_buy_rate_lagged = df['Buy Rate'].tail(shift).values.reshape(-1, 1)
    df.fillna(method='bfill', inplace=True)
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df[df.drop(columns=['Date', 'Buy Rate']).columns])
    scaler2 = MinMaxScaler()
    scaled_future_buy_rate_lagged = scaler2.fit_transform(future_buy_rate_lagged).tolist()
    last_7_days = scaled_data[-7:]
    future_predictions = []
    pickle_path = f'./Models/{vegetable}.pkl'
    with open(pickle_path, 'rb') as f:
        model = pickle.load(f)

    for i in range(shift):
        X = last_7_days[np.newaxis, :, :]
        prediction = model.predict(X)
        future_predictions.append(prediction[0])
        last_7_days = np.vstack([last_7_days[1:], np.append(prediction, scaled_future_buy_rate_lagged[i])])

    future_predictions_df = pd.DataFrame(future_predictions, columns=df.drop(columns=['Date', 'Buy Rate', 'Buy Rate Lagged']).columns)
    scaled_future_buy_rate_lagged_flat = [value[0] for value in scaled_future_buy_rate_lagged]
    future_predictions_df['Buy Rate'] = scaled_future_buy_rate_lagged_flat
    predictions_rescaled = scaler.inverse_transform(np.array(future_predictions_df))
    future_dates = pd.date_range(df['Date'].max() + pd.Timedelta(days=1), periods=shift)
    future_dates = [date.date() for date in future_dates]
    predictions_df = pd.DataFrame(predictions_rescaled, columns=df.drop(columns=['Date', 'Buy Rate']).columns)
    predictions_df['Date'] = future_dates
    predictions_df.drop(columns=['Buy Rate Lagged'], inplace=True)
    predictions_df = predictions_df.round(2)
    predictions_df['Date'] = pd.to_datetime(predictions_df['Date']).dt.date
    df.drop(columns=['Buy Rate', 'Buy Rate Lagged'], inplace=True)
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    df = pd.concat([df, predictions_df], ignore_index=True)
    return df

with st.spinner("Fetching data..."):
    vegetableDataframes = getVegetableData()

for vegetable in vegetables:
    with st.spinner(f"Forecasting {vegetables.index(vegetable)+1}/{len(vegetables)} vegetable prices..."):
        vegetableDataframes[vegetable] = forecast(vegetable, vegetableDataframes[vegetable])

marketDataframes = getMarketData(vegetableDataframes)
markets = list(marketDataframes.keys())

tabs = st.tabs(['Forecasts', 'Historical Data'])

with tabs[0]:
    forecastGrid = grid([1, 1, 1, 2, 0.7], 1, [1, 0.5, 2], vertical_align='center')

    market = forecastGrid.selectbox('Select the Market', markets, key='forecastMarket')
    df = marketDataframes[market]
    defaultStart = max(today.date() - pd.Timedelta(days=7), df['Date'].min())
    defaultEnd = min(today.date() + pd.Timedelta(days=30), df['Date'].max())
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    with forecastGrid.container():
        date_range = date_range_picker('Select the Date Range', max_date=df['Date'].max(), min_date=df['Date'].min(), default_start=defaultStart, default_end=defaultEnd)
    chartTypes = ['Area', 'Bar', 'Line']
    chartType = forecastGrid.selectbox('Select the Chart Type', chartTypes, key='chartType', index=2)
    vegetable_columns = [col for col in df.columns if col != 'Date']
    vegetables = forecastGrid.multiselect('Select the Vegetables', vegetable_columns, vegetable_columns, key='forecastVegetables')
    vegetableSwtich = forecastGrid.toggle('Select all vegetables', False, key='forecastVegetableSwitch')
    if vegetableSwtich:
        vegetables = vegetable_columns

    filtered_df = df[(df['Date'] >= date_range[0]) & (df['Date'] <= date_range[1])]
    xaxis = [str(date) for date in filtered_df['Date']]
    lines = {}
    for vegetable in vegetables:
        lines[vegetable] = list(filtered_df[vegetable])
    
    forecastChart = apex_chart(f'{market} price forecast', chartType.lower(), 'smooth', xaxis, lines, 400, highlightPoint=str(today.date()))

    with forecastGrid.container():
        components.html(forecastChart, height=400)

    next_df = df[(df['Date'] >= today.date()) & (df['Date'] <= today.date() + pd.Timedelta(days=30))]

    minValues = next_df[vegetable_columns].min()
    minValue = minValues.min()
    minVegetable = minValues.idxmin()
    min_date = next_df[next_df[minVegetable] == minValue]['Date'].values[0]
    maxValues = next_df[vegetable_columns].max()
    maxValue = maxValues.max()
    maxVegetable = maxValues.idxmax()
    max_date = next_df[next_df[maxVegetable] == maxValue]['Date'].values[0]

    xaxis = [str(date) for date in next_df['Date']]
    lines = {}
    for market in vegetable_columns:
        lines[market] = list(next_df[market])
    
    nextChart = apex_chart(f'{vegetable} price forecast for next week', 'scatter', 'smooth', xaxis, lines, 400, minValue=[str(min_date), next_df.columns.get_loc(minVegetable)-1], maxValue=[str(max_date), next_df.columns.get_loc(maxVegetable)-1])
    with forecastGrid.container():
        components.html(nextChart, height=400)

    with forecastGrid.container():
        means = next_df[vegetable_columns].mean()
        highest_mean_vegetable = means.idxmax()
        lowest_mean_vegetable = means.idxmin()
        message = f"""
        In the coming 3 month, {highest_mean_vegetable} is expected to have the highest average selling price.\n
        While {lowest_mean_vegetable} is expected to have the lowest average selling price.\n
        {highest_mean_vegetable} would be a profitable choice to farm in for the next 3 months.
        """
        st.html(f'<p class="insight-message">{message}</p>')

    def getMetrics(dataframes):
        metrics = {}
        for vegetable, dataframe in dataframes.items():
            for market in dataframe.columns[1:]:
                today_data = dataframe.loc[dataframe['Date'] == today.date()]
                today_value = today_data[market].values[0] if not today_data.empty else 0.00

                yesterday_data = dataframe.loc[dataframe['Date'] == today.date() - pd.Timedelta(days=1)]
                yesterday_value = yesterday_data[market].values[0] if not yesterday_data.empty else 0.00

                change_from_yesterday = today_value - yesterday_value
                metrics[vegetable, market] = (today_value, change_from_yesterday)
        
        return metrics
    
    metrics = getMetrics(vegetableDataframes)
    metric = forecastGrid.columns(4)
    
    colors = colors = ['#008ffb', '#00e396', '#feb019', '#ff4560', '#775dd0', '#546E7A', '#26a69a', '#D10CE8', '#FFD700', '#FF6347']

    for i, m in enumerate(markets):
        for j, v in enumerate(vegetables):
            with metric[j % 4].container():
                st.html('<span class="metric-div"></span>')
                st.html(f'<span class="color-{colors[j][1:]}"></span>')
                st.metric(label=f'{v} in {m}', label_visibility='visible', value='Rs.'+' {:.2f}'.format(metrics[v, m][0]), delta=round(metrics[v, m][1], 2), delta_color='normal' if metrics[v, m][1] != 0 else 'off')

with tabs[1]:
    historicalGrid = grid([1, 5], 1, vertical_align='center')
    defaultStart = today.date() - pd.Timedelta(days=31)
    defaultEnd = today.date() - pd.Timedelta(days=1)

    with historicalGrid.container():
        vegetable = st.selectbox('Select the Vegetable', vegetables, key='historicalVegetable')
        df = vegetableDataframes[vegetable]
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        date_range = date_range_picker('Select the Date Range', max_date=defaultEnd, min_date=df['Date'].min(), default_start=defaultStart, default_end=defaultEnd)
        market_columns = [col for col in df.columns if col != 'Date']
        markets = st.multiselect('Select the Markets', market_columns, market_columns, key='historicalMarkets')
        marketSwtich = st.toggle('Select all markets', False, key='historicalMarketSwitch')
        if marketSwtich:
            markets = market_columns
        timeSwich = st.toggle('Select all time', False, key='historicalTimeSwitch')
        if timeSwich:
            date_range = [df['Date'].min(), df['Date'].max()]

    filtered_df = df[(df['Date'] >= date_range[0]) & (df['Date'] <= date_range[1])]

    melted_df = filtered_df.melt(id_vars=['Date'], value_vars=markets, var_name='Market', value_name='Price')

    def markets_list(markets):
        if len(markets) > 1:
            return f'{vegetable} price change in {', '.join(markets[:-1]) + ' and ' + markets[-1]}'
        elif markets:
            return f'{vegetable} price change in {markets[0]}'
        else:
            return ''

    xaxis = [str(date) for date in filtered_df['Date']]
    lines = {}
    for market in markets:
        lines[market] = list(filtered_df[market])
        
    historicalChart = apex_chart(markets_list(markets), 'bar', 'stepline', xaxis, lines, 400)
    
    with historicalGrid.container():
        components.html(historicalChart, height=400)

    rolling_means = filtered_df[market_columns].rolling(window=7, min_periods=1).mean()
    filtered_df['Rolling Mean'] = rolling_means.mean(axis=1)
    filtered_df = filtered_df.round(2)

    xaxis = [str(date) for date in filtered_df['Date']]
    lines = {'Rolling Mean': list(filtered_df['Rolling Mean'])}

    trendChart = apex_chart(f'Trend of {vegetable} prices', 'area', 'smooth', xaxis, lines, 400)

    with historicalGrid.container():
        components.html(trendChart, height=400)
