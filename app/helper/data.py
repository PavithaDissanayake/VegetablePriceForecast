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
import pdfplumber
import requests
from io import BytesIO
import re
from statistics import mean
import pandas as pd
from bs4 import BeautifulSoup

# data folder
folder = './Data'
vegetables = sorted([f.split('.')[0] for f in os.listdir(folder) if f.endswith('.csv')])

# fetch data from firestore and local storage, combine and return
@st.cache_data(show_spinner=False)
def getVegetableData():
    # Check if Firebase is already initialized
    if not firebase_admin._apps:
        # Retrieve Firebase credentials from Streamlit secrets
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

        # Initialize Firebase app with the provided credentials
        cred = credentials.Certificate(firebase_credentials)
        firebase_admin.initialize_app(cred)

    # Create a Firestore client
    db = firestore.client()

    # Fetch all documents from the 'Data' collection in Firestore
    docs = db.collection('Data').stream()
    # Convert Firestore documents to a DataFrame
    firebaseData = pd.DataFrame([doc.to_dict() for doc in docs]) # data stored in firebase

    vegetableDataframes = {}
    # Iterate over each vegetable to extract and process data
    for vegetable in vegetables:
        # Identify market columns associated with the current vegetable
        markets = [column for column in firebaseData.columns if vegetable in column]
        # Create a temporary DataFrame with relevant market data
        firebaseTempData = firebaseData[['Date'] + markets].copy()
        # Convert 'Date' column to datetime format
        firebaseTempData['Date'] = pd.to_datetime(firebaseTempData['Date'], format='%d %B %Y at %H:%M:%S %Z%z', errors='coerce', utc=True).dt.date
        for market in markets:
            firebaseTempData.rename(columns={market: market.split('_')[0]}, inplace=True)

        # Load local CSV data for the current vegetable
        githubData = pd.read_csv(f'{folder}/{vegetable}.csv') # data stored local
        githubData['Date'] = pd.to_datetime(githubData['Date']).dt.date

        # Concatenate GitHub and Firebase data for the current vegetable
        vegetableDataframes[vegetable] = pd.concat([githubData, firebaseTempData], axis=0) # concatenate
        vegetableDataframes[vegetable]['Date'] = pd.to_datetime(vegetableDataframes[vegetable]['Date']).dt.date
    
    return list(vegetableDataframes.keys()), vegetableDataframes

def getNewVegData(date_range, vegetables, markets):
    # Create a default DataFrame with dates and initialize market columns
    defaultDf = pd.DataFrame(date_range, columns=['Date'])
    newDataframes = {}
    # Create a default DataFrame with dates and initialize market columns
    for market in markets:
        defaultDf[market] = 0

    # Prepare a new DataFrame for each vegetable
    for vegetable in vegetables:
        newDataframes[vegetable] = defaultDf.copy()

    # Iterate through each date in the specified date range
    for i, date in enumerate(date_range):
        try:
            year = date.strftime('%Y')
            month = date.strftime('%B')
            dateStr = date.strftime('%d-%m-%Y')
            url = f'https://www.harti.gov.lk/images/download/market_information/{year}/{month.lower()}/daily_{dateStr}.pdf'
            response = requests.get(url)

            if response.status_code != 200:
                print(f'failed to fetch data from {url}')
                url = f'https://www.harti.gov.lk/images/download/market_information/{year}/{month}/daily_{dateStr}.pdf'
                response = requests.get(url)

            if response.status_code != 200:
                print(f'failed to fetch data from {url}')
                url = f'https://www.harti.gov.lk/images/download/market_information/{year}/daily/daily_{dateStr}.pdf'
                response = requests.get(url)

            if response.status_code != 200:
                print(f'failed to fetch data from {url}')
                url = f'https://www.harti.gov.lk/images/download/market_information/{year}/daily/{month}/daily_{dateStr}.pdf'
                response = requests.get(url)

            if response.status_code != 200:
                print(f'failed to fetch data from {url}')
                url = f'https://www.harti.gov.lk/images/download/market_information/{year}/daily/{month.lower()}/daily_{dateStr}.pdf'
                response = requests.get(url)
            
            if response.status_code != 200:
                print(f'failed to fetch data from {url}')
                newDate = date.replace(year=date.year-1)
                dateStr = newDate.strftime('%d-%m-%Y')
                url = f'https://www.harti.gov.lk/images/download/market_information/{year}/daily/{month.lower()}/daily_{dateStr}.pdf'
                response = requests.get(url)

            # If the response is successful, process the PDF
            if response.status_code == 200:
                print(f'Successfully fetched data from {url}')
                pdf_data = BytesIO(response.content)
                with pdfplumber.open(pdf_data) as pdf:
                    # Select the appropriate page from the PDF
                    if len(pdf.pages) == 2:
                        page = pdf.pages[0]
                    elif len(pdf.pages) >= 2:
                        page = pdf.pages[1]
                    
                    # Extract tables from the selected page
                    tables = page.extract_tables()
                    
                    if tables:
                        table = tables[0]
                        df = pd.DataFrame(table)

                        # Map market names to their respective column indices
                        marketColumns = {}
                        for col in range(len(df.columns)):
                            for market in markets:
                                if df.iloc[1, col] == f'{market}':
                                    marketColumns[market] = col
                                elif df.iloc[1, col] == f'{market}\nMarket':
                                    marketColumns[market] = col

                        # Populate the newDataframes with extracted values
                        for row in range(len(df)):
                            for vegetable in vegetables:
                                if df.iloc[row, 0] == vegetable:
                                    for j, market in enumerate(markets):
                                        value = df.iloc[row, marketColumns[market]]
                                        value = round(mean([float(value) for value in re.findall(r'\d+\.?\d*', value)]), 2)
                                        newDataframes[vegetable].iloc[i, j+1] = value
                    else:
                        continue
            else:
                print(f'failed to fetch data from {url}')
                continue

        except Exception as e:
            print(f"An error occurred: {e}")
            continue  # Continue the loop even after an error

    return newDataframes

def getNewBuyRate(date_range):
    # Create a default DataFrame with dates and a default buy rate
    defaultDf = pd.DataFrame(date_range, columns=['Date'])
    defaultDf['Buy Rate'] = 288.00

    # URL of the page containing exchange rates
    url = 'https://www.cbsl.gov.lk/en/rates-and-indicators/exchange-rates/daily-buy-and-sell-exchange-rates'
    
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Locate the "United States Dollar" section by its <h2> tag
        h2_usd = soup.find('h2', text=' United States Dollar ')
        
        # Find the table following the <h2> tag
        usd_table_element = h2_usd.find_next_sibling('div', class_='table-responsive').find('table')

        # Extract the table rows
        rows = usd_table_element.find_all('tr')

        # Prepare a list to hold the data
        data = []

        # Loop through the rows and extract data
        for row in rows[1:]:  # Skip header
            cols = row.find_all('td')
            date = cols[0].text.strip()
            buy_rate = cols[1].text.strip().replace(',', '')  # Remove commas for conversion
            data.append({'Date': date, 'Buy Rate': float(buy_rate)})

        # Create a DataFrame from the scraped data
        usd_table = pd.DataFrame(data)
        usd_table['Date'] = pd.to_datetime(usd_table['Date']).dt.date

        # Filter the DataFrame based on the date_range
        usd_table = usd_table[(usd_table['Date'] >= date_range[0].date()) & 
                              (usd_table['Date'] <= date_range[-1].date())]

        # Reindex the DataFrame to include all dates in the date_range
        usd_table = usd_table.set_index('Date').reindex(date_range).reset_index()
        usd_table.rename(columns={'index': 'Date'}, inplace=True)
        usd_table['Buy Rate'] = usd_table['Buy Rate'].fillna(288)

        return usd_table  # Return the scraped DataFrame

    except Exception as e:  # Catch any exception that occurs
        print(f"An error occurred: {e}")  # Optionally log the error
        return defaultDf  # Return the default DataFrame on error

def getNewData(_date_range, vegetables, markets):
    # Fetch new vegetable data and the latest buy rate
    newVegData = getNewVegData(_date_range, vegetables, markets)
    newBuyRate = getNewBuyRate(_date_range)
    newData = {}

    # Merge vegetable data with buy rates and handle missing values
    for veg, df in newVegData.items():
        newData[veg] = pd.merge(df, newBuyRate, on='Date', how='left')
        newData[veg] = newData[veg].replace(0, np.nan)
        newData[veg] = newData[veg].interpolate(method='linear', limit_direction='both')
    
    return newData    

def writeNewData(newData):
    # Rename columns for each vegetable dataframe and set 'Date' as index
    for veg, df in newData.items():
        df.set_index('Date', inplace=True)
        for col in df.columns:
            df.rename(columns={col: f'{col}_{veg}'}, inplace=True)
            newData[veg] = df
        
    # Combine all vegetable dataframes into a single dataframe
    combined_df = pd.concat(newData.values(), axis=1)
    combined_df.reset_index(inplace=True)
    combined_df['Date'] = pd.to_datetime(combined_df['Date'])

    # Initialize Firebase if not already done
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

    # Write each row of the combined dataframe to Firebase
    for _, row in combined_df.iterrows():
        doc_id = str(row['Date'].date())
        row_dict = row.to_dict()
        db.collection('Data').document(doc_id).set(row_dict)

@st.cache_data(show_spinner=False)
def useNewData(start_date, end_date, vegetables, markets):
    # Convert start and end dates to datetime and create a date range
    start_date = pd.to_datetime(start_date) + pd.Timedelta(days=1)
    end_date = pd.to_datetime(end_date)
    date_range = pd.date_range(start=start_date.date(), end=end_date.date())
    
    # Fetch new data for the specified date range, vegetables, and markets
    newData = getNewData(date_range, vegetables, markets)
    nullflag = False

    # Check for any null values in the new data
    for veg, df in newData.items():
        if df.isnull().values.any():
            nullflag = True
    
    # If no null values, write new data to Firebase
    if not nullflag:
        writeNewData(newData)

    # Retrieve existing vegetable data
    vegetables, vegetableDataframes = getVegetableData()
    return vegetables, vegetableDataframes

# convert data into market wise dataframes
@st.cache_data(show_spinner=False)
def getMarketData(vegetableData):
    marketDataframes = {}
    # Loop through each vegetable to organize data by market
    for vegetable in vegetables:
        dataframe = vegetableData[vegetable]
        for market in dataframe.columns[1:]:
            if market not in marketDataframes:
                marketDataframes[market] = pd.DataFrame()
                marketDataframes[market]['Date'] = dataframe['Date']
            marketDataframes[market][vegetable] = dataframe[market]
            
    # Return the list of markets and their dataframes
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