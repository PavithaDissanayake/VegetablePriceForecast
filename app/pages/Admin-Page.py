import streamlit as st
from helper.data import getVegetableData, useNewData, forecast
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

if 'admin' not in st.session_state:
    st.session_state['admin'] = False
if 'forecast' not in st.session_state:
    st.session_state['forecast'] = False
if 'transfer' not in st.session_state:
    st.session_state['transfer'] = False

if st.session_state['admin'] == False:
    width = 'centered'
    icon = '🔒'
else:
    width = 'wide'
    icon = '🔓'

st.set_page_config(
    page_title='Admin Page',
    page_icon=icon,
    layout=width,
    initial_sidebar_state="collapsed"
)

st.html('./styles/Admin-Page.html')

if st.session_state['admin'] == False:
    with st.container():
        st.html('<span class="admin-password-container"></span>')
        st.title("Admin Login")
        password = st.text_input('Please enter the password to access the admin panel', type='password')
        if password == st.secrets['admin']['password']:
            st.session_state['admin'] = True
            st.rerun()
        elif password:
            st.warning('Incorrect password! Please try again.')
else:
    tabs = st.tabs(['Current Data', 'App Management'])
    with tabs[0]:
        today = pd.Timestamp.now()
        with st.spinner('Fetching data...'):
            vegetables, vegetableDataframes = getVegetableData()

        markets = vegetableDataframes[vegetables[0]].columns[1:-1]
        vegetableDataframes[vegetables[0]]['Date'] = pd.to_datetime(vegetableDataframes[vegetables[0]]['Date']).dt.date
        maxDate = vegetableDataframes[vegetables[0]]['Date'].max()

        if maxDate != today.date():
            with st.spinner('Fetching new data...'):
                vegetables, vegetableDataframes = useNewData(maxDate.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'), vegetables, markets.to_list())

        for vegetable in vegetables:
            with st.spinner(f"Vegetable prices forecasting {vegetables.index(vegetable)+1}/{len(vegetables)}..."):
                vegetableDataframes[vegetable] = forecast(vegetable, vegetableDataframes[vegetable])

        beforeData = {}
        afterData = {}
        for veg, df in vegetableDataframes.items():
            beforeData[veg] = df[df['Date'] < today.date()].reset_index(drop=True)
            afterData[veg] = df[df['Date'] >= today.date()].reset_index(drop=True)

        columns = st.columns(2)
        for i, vegetable in enumerate(vegetables):
            with columns[i//2].container():
                st.html('<span class="admin-data-container"></span>')
                st.title(vegetable)
                before, after = st.columns(2)
                with before.container():
                    st.html('<span class="individual-data-container"></span>')
                    st.write('Latest available data')
                    st.dataframe(beforeData[vegetable], use_container_width=True, hide_index=True)
                with after.container():
                    st.html('<span class="individual-data-container"></span>')
                    st.write('90 days forecasted data')
                    st.dataframe(afterData[vegetable], use_container_width=True, hide_index=True)
                
    with tabs[1]:
        st.title('App Management')
        forecast, trasnfer = st.columns(2)
        with forecast.container():
            st.html('<span class="admin-forecast-container"></span>')
            with st.container():
                st.html('<span class="admin-forecast-button-container"></span>')
                if st.button('Trigger new forecast'):
                    st.session_state['forecast'] = True
            if st.session_state['forecast']:
                csv, code = st.columns([2, 3])
                with csv.container():
                    st.html('<span class="admin-forecast-csv-container"></span>')
                    for veg, df in beforeData.items():
                        dfCSV = df.to_csv(index=False).encode('utf-8')                    
                        st.download_button(f'Download {veg} dataframe', dfCSV, f'{veg}.csv', 'csv', key=f'{veg}_pickle')
                csv.markdown("""
                            <a href="https://github.com/PavithaDissanayake/VegetablePriceForecast/tree/main/Models" class="pickle-button" target="_blank">Click here to save the new models</a>
                             """, unsafe_allow_html=True)

                with code.container(height=500):
                    st.html('<span class="admin-forecast-code-container"></span>')
                    st.write("Use this code for forecasting")
                    code = """
                            def train_bilstm_model(dataframe, seq_length=30, tuner_directory='my_dir/bilstm_hyperparameter_tuning', save_path='best_model.pkl'):
                            # Convert 'Date' to datetime format
                            dataframe['Date'] = pd.to_datetime(dataframe['Date'])
                            dataframe.set_index('Date', inplace=True)

                            # Create lagged feature for 'Buy Rate' with a lag of 7 days
                            dataframe['Buy Rate Lagged'] = dataframe['Exchange Rate'].shift(7)
                            
                            # Drop the rows with NaN values due to lagging
                            dataframe = dataframe.dropna().reset_index(drop=True)

                            # Normalize the data
                            scaler = MinMaxScaler()
                            scaled_data = scaler.fit_transform(dataframe[['Kandy', 'Dambulla', 'Buy Rate Lagged']])
                            
                            # Function to create sequences for LSTM
                            def create_sequences(data, seq_length):
                                X, y = [], []
                                for i in range(len(data) - seq_length):
                                    X.append(data[i:i+seq_length])
                                    y.append(data[i+seq_length][:2])  # Target sequence (next step)
                                return np.array(X), np.array(y)

                            # Create sequences
                            X, y = create_sequences(scaled_data, seq_length)

                            # Split the data into training, validation, and test sets
                            train_ratio = 0.9
                            val_ratio = 0.05

                            train_index = int(len(X) * train_ratio)
                            val_index = int(len(X) * (train_ratio + val_ratio))

                            X_train, X_val, X_test = X[:train_index], X[train_index:val_index], X[val_index:]
                            y_train, y_val, y_test = y[:train_index], y[train_index:val_index], y[val_index:]

                            # Enable mixed precision training
                            mixed_precision.set_global_policy('mixed_float16')

                            # Define a function that builds the Bi-LSTM model with hyperparameters
                            def build_model(hp):
                                model = Sequential()
                                
                                # First Bidirectional LSTM layer
                                model.add(Bidirectional(LSTM(units=hp.Int('units1', min_value=16, max_value=64, step=16),
                                                            return_sequences=True), input_shape=(seq_length, 3)))
                                model.add(Dropout(hp.Float('dropout_rate1', 0.1, 0.5, step=0.1)))
                                
                                # Second Bidirectional LSTM layer
                                model.add(Bidirectional(LSTM(units=hp.Int('units2', min_value=16, max_value=64, step=16),
                                                            return_sequences=True)))
                                model.add(Dropout(hp.Float('dropout_rate2', 0.1, 0.5, step=0.1)))
                                
                                # Third Bidirectional LSTM layer
                                model.add(Bidirectional(LSTM(units=hp.Int('units3', min_value=16, max_value=64, step=16),
                                                            return_sequences=False)))
                                model.add(Dropout(hp.Float('dropout_rate3', 0.1, 0.5, step=0.1)))
                                
                                # First Dense layer
                                model.add(Dense(
                                    units=hp.Int('dense_units1', min_value=16, max_value=64, step=16),
                                    activation=hp.Choice('dense_activation1', values=['relu', 'tanh', 'sigmoid', 'elu', 'selu'])
                                ))
                                
                                # Second Dense layer
                                model.add(Dense(
                                    units=hp.Int('dense_units2', min_value=16, max_value=64, step=16),
                                    activation=hp.Choice('dense_activation2', values=['relu', 'tanh', 'sigmoid', 'elu', 'selu'])
                                ))

                                # Output layer
                                model.add(Dense(2, dtype='float32'))  # Output layer with 2 outputs

                                # Compile the model
                                learning_rate = hp.Choice('learning_rate', values=[1e-4, 1e-3, 1e-2, 1e-1])
                                model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate), loss='mean_squared_error')
                                
                                return model

                            # Clean previous tuner results if any
                            if os.path.exists(tuner_directory):
                                shutil.rmtree(tuner_directory)

                            # Define a tuner using RandomSearch
                            tuner = kt.RandomSearch(
                                build_model,
                                objective='val_loss',
                                max_trials=20,
                                executions_per_trial=5,
                                directory=tuner_directory,
                                project_name='bilstm_hyperparameter_tuning'
                            )

                            # Convert data to tf.data pipelines
                            train_dataset = tf.data.Dataset.from_tensor_slices((X_train, y_train)).batch(32).prefetch(tf.data.AUTOTUNE)
                            val_dataset = tf.data.Dataset.from_tensor_slices((X_val, y_val)).batch(32).prefetch(tf.data.AUTOTUNE)

                            # Run the hyperparameter search
                            tuner.search(train_dataset, epochs=200, validation_data=val_dataset, callbacks=[EarlyStopping(monitor='val_loss', patience=3)])

                            # Retrieve the best model
                            best_model = tuner.get_best_models(num_models=1)[0]

                            # Save the model to a pickle file
                            with open(save_path, 'wb') as file:
                                pickle.dump(best_model, file)
                            
                            print(f"Model training completed and saved to {save_path}")
                            """
                    st.code(code, language='python')
                    
        with trasnfer.container():
            st.html('<span class="admin-transfer-container"></span>')
            with st.container():
                st.html('<span class="admin-transfer-button-container"></span>')
                if st.button('Trigger data transfer'):
                    st.session_state['transfer'] = True
            if st.session_state['transfer']:
                lastYear = {}
                thisYear = {}
                splitDate1 = pd.Timestamp(today.year-1, 1, 1).date()
                splitDate2 = pd.Timestamp(today.year, 1, 1).date()
                for veg, df in vegetableDataframes.items():
                    lastYear[veg] = df[df['Date'] < splitDate2].reset_index(drop=True)

                github, firebase = st.columns([2, 3])

                with github.container():
                    st.html('<span class="admin-transfer-github-container"></span>')
                    for veg, df in lastYear.items():
                        dfCSV = df.to_csv(index=False).encode('utf-8')                    
                        st.download_button(f'Download old {veg} dataframe', dfCSV, f'{veg}.csv', 'csv', key=f'{veg}_github')
                
                github.markdown("""
                                <a href="https://github.com/PavithaDissanayake/VegetablePriceForecast/tree/main/Data" class="data-button" target="_blank">Click here to transfer data to GitHub</a>
                                """, unsafe_allow_html=True)
                
                with firebase.container():
                    st.html('<span class="admin-transfer-firebase-container"></span>')
                    st.warning("Pressing this button will delete all the data in the Firestore database and transfer this year's data. Please proceed with caution.")
                    if st.button("Transfer this year's data into firestore"):
                        for veg, df in lastYear.items():
                            df = df[df['Date'] >= splitDate1].reset_index(drop=True)
                            df.set_index('Date', inplace=True)
                            for col in df.columns:
                                df.rename(columns={col: f'{col}_{veg}'}, inplace=True)
                                thisYear[veg] = df
                            
                        combined_df = pd.concat(thisYear.values(), axis=1)
                        combined_df.reset_index(inplace=True)
                        combined_df['Date'] = pd.to_datetime(combined_df['Date'])
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

                        for _, row in combined_df.iterrows():
                            doc_id = str(row['Date'].date())
                            db.collection('Data').document(doc_id).delete()
