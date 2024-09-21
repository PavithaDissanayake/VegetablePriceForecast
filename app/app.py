import streamlit as st
import pandas as pd
import altair as alt
from wholeView import show_whole_view
from filterView import show_filter_view

# Initialization
st.set_page_config(layout="wide")
today = pd.Timestamp('2023-01-23')

st.sidebar.title('Vegetable Market Price')
st.sidebar.write('---')
view_selection = st.sidebar.radio("Select View", ["Whole View", "Filter View"])

# Define vegetables and dataframes
vegetables = ['Beans', 'BeetRoot', 'Brinjals', 'Cabbage', 'Capsicum', 'Carrot', 'Cucumber', 'Knolkhol', 'LadiesFingers', 'Leaks', 'Lime', 'Manioc', 'Pumpkin', 'Raddish', 'Tomato']
dataframes = {veg: pd.read_csv(f'./Data/{veg}.csv') for veg in vegetables}
for veg in vegetables:
    dataframes[veg]['Date'] = pd.to_datetime(dataframes[veg]['Date'])
    dataframes[veg]['Date'] = dataframes[veg]['Date'].dt.date

if st.sidebar.button('change'):
    dataframes['Beans'].loc[0, 'Bandarawela'] += 10
    dataframes['Beans'].to_csv('./Data/Beans.csv', index=False)

markets = dataframes['Beans'].columns[1:]

# Initialize session state for selected vegetable and market
if "selected_vegetable" not in st.session_state:
    st.session_state.selected_vegetable = vegetables[0]  # Default to the first vegetable in the list

if "selected_market" not in st.session_state:
    st.session_state.selected_market = markets[0]  # Default to the first market in the list

# Show the selected view
if view_selection == "Filter View":
    show_filter_view(today, dataframes, vegetables)
else:
    show_whole_view(today, dataframes, vegetables, markets)
