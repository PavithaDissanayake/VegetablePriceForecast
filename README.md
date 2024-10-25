# VageCast - Real-Time Vegetable Price Forecasting System

## Project Overview
VageCast is a comprehensive, real-time vegetable price forecasting system designed to support decision-making for both farmers and consumers. Our goal is to provide accurate and timely vegetable price predictions, enabling stakeholders to make informed decisions in a dynamic market environment.

## System Architecture

### 1. Data Extraction
- **Automated Data Gathering**: We have implemented a fully automated real-time data extraction system that continuously gathers up-to-date vegetable prices from various web sources.
  - **Vegetable Prices**: [Hector Kobbekaduwa Agrarian Research and Training Institute](https://www.harti.gov.lk/index.php/en/market-information/data-food-commodities-bulletin)
  - **Dollar Buy Rate**: [Central Bank of Sri Lanka](https://www.cbsl.gov.lk/en/rates-and-indicators/exchange-rates/daily-buy-and-sell-exchange-rates)
- **Data Freshness**: This ensures our forecasting models receive fresh and accurate data, enabling precise predictions.

### 2. Data Cleaning & Processing
- **Data Refinement**: The raw data collected is meticulously cleaned and processed to eliminate inconsistencies or missing information.
- **Pipeline Efficiency**: Our advanced data pipeline ensures that only refined and reliable data is fed into the models, enhancing overall forecasting accuracy.

### 3. Forecasting Models
- **Advanced Techniques**: Our sophisticated forecasting models utilize historical data to predict future price trends.
- **Machine Learning Approaches**: We employ techniques such as ARIMA, LSTM, and ensemble models to deliver precise and timely forecasts, customized for different vegetable markets.
  - **Notebooks**: [Kaggle](https://www.kaggle.com/datasets/nisith210144g/vegi-price/code)

### 4. Web Application
- **User-Friendly Interface**: The system is deployed on a user-friendly web application built using Streamlit, accessible via Streamlit Community Cloud.
- **Separate User Views**: The app features distinct views for two user groups: Farmers and Consumers, allowing for tailored insights.
- **Intuitive Exploration**: Users can easily explore data, view forecasts, and gain insights into market trends through the intuitive interface.
  - **Access the Web Dashboard**: [Web Dashboard](https://vegetablepriceforecast.streamlit.app/)

### 5. Data Storage & Management
- **Efficient Data Handling**: The system utilizes both GitHub's local storage and Firestore Database for effective data management.
- **Synchronization**: Admin users can initiate data transfers between Firebase and GitHub, ensuring synchronization of datasets.

### 6. Admin Panel & Capabilities
- **Advanced Admin Functionality**: The web app includes an admin panel with enhanced functionalities:
  - **Model Management**: Admins can create and train new forecasting models as needed, ensuring the system remains up-to-date with the latest market behaviors.
  - **Data Access**: Only admins are authorized to download raw data for further analysis or auditing.
  - **Data Transfer Control**: The admin panel enables seamless triggering of data transfers from Firebase to GitHub, ensuring that data is always synchronized.

## To Run Locally
1. Clone the repository: `git clone https://github.com/PavithaDissanayake/VegetablePriceForecast`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `streamlit run app.py`
