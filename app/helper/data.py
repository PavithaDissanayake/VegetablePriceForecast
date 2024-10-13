import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras import models # type: ignore
import pickle
import numpy as np
import os

# data folder
folder = './Data/NewData'
vegetables = sorted([f.split('.')[0] for f in os.listdir(folder) if f.endswith('.csv')])

# fetch data from firestore and local storage, combine and return
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
    firebaseData = pd.DataFrame([doc.to_dict() for doc in docs]) # data stored in firebase

    vegetableDataframes = {}
    for vegetable in vegetables:
        markets = [column for column in firebaseData.columns if vegetable in column]
        firebaseTempData = firebaseData[['Date'] + markets].copy()
        firebaseTempData['Date'] = pd.to_datetime(firebaseTempData['Date'], format='%d %B %Y at %H:%M:%S %Z%z', errors='coerce', utc=True).dt.date
        for market in markets:
            firebaseTempData.rename(columns={market: market.split('_')[0]}, inplace=True)

        githubData = pd.read_csv(f'{folder}/{vegetable}.csv') # data stored local
        githubData['Date'] = pd.to_datetime(githubData['Date']).dt.date

        vegetableDataframes[vegetable] = pd.concat([githubData, firebaseTempData], axis=0) # concatenate
        vegetableDataframes[vegetable]['Date'] = pd.to_datetime(vegetableDataframes[vegetable]['Date']).dt.date
    
    return list(vegetableDataframes.keys()), vegetableDataframes

# convert data into market wise dataframes
@st.cache_data(show_spinner=False)
def getMarketData(vegetableData):
    marketDataframes = {}
    for vegetable in vegetables:
        dataframe = vegetableData[vegetable]
        for market in dataframe.columns[1:]:
            if market not in marketDataframes:
                marketDataframes[market] = pd.DataFrame()
                marketDataframes[market]['Date'] = dataframe['Date']
            marketDataframes[market][vegetable] = dataframe[market]
    return list(marketDataframes.keys()), marketDataframes

# forecast the future prices
@st.cache_data(show_spinner=False)
def forecast(vegetable, df):
    
    shift = 100 # how far we are looking into
    df['Buy Rate Lagged'] = df['Buy Rate'].shift(shift)
    future_buy_rate_lagged = df['Buy Rate'].tail(shift).values.reshape(-1, 1)
    df.fillna(method='bfill', inplace=True)
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df[df.drop(columns=['Date', 'Buy Rate']).columns])
    scaler2 = MinMaxScaler()
    scaled_future_buy_rate_lagged = scaler2.fit_transform(future_buy_rate_lagged).tolist()
    last_7_days = scaled_data[-7:]
    future_predictions = []

    # get the model
    pickle_path = f'./Models/{vegetable}.pkl'
    with open(pickle_path, 'rb') as f:
        model = pickle.load(f)

    # forecast in a loop
    for i in range(shift):
        X = last_7_days[np.newaxis, :, :]
        prediction = model.predict(X)
        future_predictions.append(prediction[0])
        last_7_days = np.vstack([last_7_days[1:], np.append(prediction, scaled_future_buy_rate_lagged[i])])

    # combine with historical data
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