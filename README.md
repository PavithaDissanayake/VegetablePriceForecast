## Price and Demand Forecasting of Vegetables in Sri Lanka

This project forecasts vegetable prices across various markets in Sri Lanka using historical data from the Hector Kobbekaduwa Agrarian Research and Training Institute (HARTI). The data, spanning from 2015 onwards, is extracted and processed using the `pdfplumber` library.

### Key Progress:
- **Data Extraction**: Historical prices are extracted from PDFs, with each vegetable and market structured in a table format.
  [Data source](https://www.harti.gov.lk/index.php/en/market-information/data-food-commodities-bulletin)
- **Model Development**: Implemented and compared several forecasting models:
  - *ARIMA* and *SARIMA* for linear data with seasonal components.
  - *LSTM* for non-linear patterns, showing the best accuracy for forecasting multiple time series simultaneously.
  - *Prophet* for quick and automatic forecasting with uncertainty intervals.
    As of right now, LSTM has yielded the best results
- **Web Dashboard**: Built using Streamlit, offering:
  - *Whole View*: Summary of forecasted prices for all vegetables across all markets.
  - *Filter View*: Allows filtering by specific markets, vegetables, or time periods.
    <p><a href=https://vegetablepriceforecast-zhyq2hywjsa5s5z7gsfcz5.streamlit.app>View Dashboard</a></p>
<p>For more details <a href=https://docs.google.com/presentation/d/1LEZe7c2trm3sAbfX1-pSIuCskcK1j9M7oUNRn2sRos8/edit?usp=sharing>view</a></p>

### Upcoming Milestones:
1. Expand the LSTM model to forecast prices for all vegetables across all markets.
2. Integrate the forecasted data into the dashboard and refine its quality.
3. Implement an automated process for daily updates.
