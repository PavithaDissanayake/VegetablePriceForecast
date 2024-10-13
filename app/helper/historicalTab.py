import streamlit as st
from streamlit_extras.mandatory_date_range import date_range_picker
from streamlit_extras.grid import grid
from helper.plot import historicalPlot, trendPlot
import pandas as pd
import streamlit.components.v1 as components

def historicalTab(primaryDataframes, primary, prime, second, today, inverse=False):
    historicalGrid = grid([1, 5], 1, vertical_align='center')
    defaultStart = today.date() - pd.Timedelta(days=31)
    defaultEnd = today.date() - pd.Timedelta(days=1)

    with historicalGrid.container():
        select1 = st.selectbox(f'Select the {prime}', primary, key='historicalPrime')
        df = primaryDataframes[select1]
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        date_range = date_range_picker('Select the Date Range', max_date=defaultEnd, min_date=df['Date'].min(), default_start=defaultStart, default_end=defaultEnd)
        secondary_columns = [col for col in df.columns if col != 'Date']
        select2 = st.multiselect(f'Select the {second}', secondary_columns, secondary_columns, key='historicalSecondary')
        secondarySwtich = st.toggle(f'Select all {second}s', False, key='historicalSecondarySwitch')
        if secondarySwtich:
            select2 = secondary_columns
        timeSwich = st.toggle('Select all time', False, key='historicalTimeSwitch')
        if timeSwich:
            date_range = [df['Date'].min(), df['Date'].max()]

    filtered_df = df[(df['Date'] >= date_range[0]) & (df['Date'] <= date_range[1])]

    def secondarys_list(select2):
        if len(select2) > 1 and not inverse:
            return f'{select1} price change in {', '.join(select2[:-1]) + ' and ' + select2[-1]}'
        elif len(select2) > 1 and inverse:
            return f'{', '.join(select2[:-1]) + ' and ' + select2[-1]} price change in {select1}'
        elif select2 and not inverse:
            return f'{select1} price change in {select2[0]}'
        elif select2 and inverse:
            return f'{select2[0]} price change in {select1}'
        else:
            return ''

    historicalChart = historicalPlot(filtered_df, select2, secondarys_list(select2))
    
    with historicalGrid.container():
        components.html(historicalChart, height=400)

    rolling_means = filtered_df[secondary_columns].rolling(window=7, min_periods=1).mean()
    filtered_df['Rolling Mean'] = rolling_means.mean(axis=1)
    filtered_df = filtered_df.round(2)

    if inverse:
        title = f'Trend of prices in {select1}'
    else:
        title = f'Trend of {select1} prices'
    trendChart = trendPlot(filtered_df, title)

    with historicalGrid.container():
        components.html(trendChart, height=400)