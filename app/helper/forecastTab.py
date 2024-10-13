import streamlit as st
from streamlit_extras.mandatory_date_range import date_range_picker
from streamlit_extras.grid import grid
import pandas as pd
from helper.plot import forecastPlot, insightPlot
import streamlit.components.v1 as components

def forecastTab(primaryDataframes, primary, secondaryDataframes, secondary, prime, second, today, inverse=False, farmerFlag=False):
    forecastGrid = grid([1, 1, 1, 2, 0.7], 1, [1, 0.5, 2], vertical_align='center')

    select1 = forecastGrid.selectbox(f'Select the {prime}', primary, key='forecastPrimary')
    df = primaryDataframes[select1]
    defaultStart = max(today.date() - pd.Timedelta(days=7), df['Date'].min())
    if farmerFlag:
        defaultEnd = min(today.date() + pd.Timedelta(days=90), df['Date'].max())
        forward = 90
    else:
        defaultEnd = min(today.date() + pd.Timedelta(days=30), df['Date'].max())
        forward = 30
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    with forecastGrid.container():
        date_range = date_range_picker('Select the Date Range', max_date=df['Date'].max(), min_date=df['Date'].min(), default_start=defaultStart, default_end=defaultEnd)
    chartTypes = ['Area', 'Bar', 'Line', 'Scatter']
    chartType = forecastGrid.selectbox('Select the Chart Type', chartTypes, key='chartType', index=2)
    secondary_columns = [col for col in df.columns if col != 'Date']
    select2 = forecastGrid.multiselect(f'Select the {second}', secondary_columns, secondary_columns, key='forecastSecondary')
    secondarySwtich = forecastGrid.toggle(f'Select all {second}s', False, key='forecastSecondarySwitch')
    if secondarySwtich:
        select2 = secondary_columns

    filtered_df = df[(df['Date'] >= date_range[0]) & (df['Date'] <= date_range[1])]

    forecastChart = forecastPlot(filtered_df, select2, select1, chartType, today)
    with forecastGrid.container():
        components.html(forecastChart, height=400)

    if not inverse:
        primaryDataframes, secondaryDataframes = secondaryDataframes, primaryDataframes
    else:
        primary, secondary = secondary, primary

    next_df = pd.DataFrame()

    for pri, dataframe in primaryDataframes.items():
        filtered_df = dataframe[(dataframe['Date'] >= today.date()) & (dataframe['Date'] <= today.date() + pd.Timedelta(days=forward))]
        filtered_df_no_date = filtered_df.drop(columns=['Date'])
        filtered_df_no_date.columns = [f'{pri} in {col}' for col in filtered_df_no_date.columns]
        filtered_df_no_date['Date'] = filtered_df['Date']

        if next_df.empty:
            next_df = filtered_df_no_date
        else:
            next_df = pd.merge(next_df, filtered_df_no_date, on='Date', how='outer')

    next_df = next_df.sort_values(by='Date').reset_index(drop=True)
    columns = [col for col in next_df.columns if col != 'Date']

    nextChart = insightPlot(next_df, columns)
    
    with forecastGrid.container():
        components.html(nextChart, height=400)

    means = {}
    for pri in secondary:
        pri_columns = [col for col in next_df.columns if col.startswith(f'{pri} in')]
        means[pri] = next_df[pri_columns].mean(axis=1).mean()
    
    highest = max(means, key=means.get)
    lowest = min(means, key=means.get)

    if farmerFlag:
        message = f"""
        In the coming 3 montsh, {highest} is expected to have the highest average selling price.\n
        While {lowest} is expected to have the lowest average selling price.\n
        {highest} would be a profitable choice to farm in for the next 3 months.
        """
    else:
        message = f"""
        In the coming month, {lowest} is expected to be the cheapest in market.\n
        While {highest} is expected to be the most expensive.\n
        
        """

    with forecastGrid.container():
        st.html(f'<p class="insight-message">{message}</p>')

    def getMetrics(dataframes):
        metrics = {}
        for sec, dataframe in dataframes.items():
            for pri in dataframe.columns[1:]:
                today_data = dataframe.loc[dataframe['Date'] == today.date()]
                today_value = today_data[pri].values[0] if not today_data.empty else 0.00

                yesterday_data = dataframe.loc[dataframe['Date'] == today.date() - pd.Timedelta(days=1)]
                yesterday_value = yesterday_data[pri].values[0] if not yesterday_data.empty else 0.00

                change_from_yesterday = today_value - yesterday_value
                metrics[sec, pri] = (today_value, change_from_yesterday)
        
        return metrics
    
    metrics = getMetrics(primaryDataframes)
    metric = forecastGrid.columns(4)
    
    colors = colors = ['#008ffb', '#00e396', '#feb019', '#ff4560', '#775dd0', '#546E7A', '#26a69a', '#D10CE8', '#FFD700', '#FF6347']

    for i, m in enumerate(primary):
        for j, v in enumerate(secondary):
            with metric[j % 4].container():
                st.html('<span class="metric-div"></span>')
                st.html(f'<span class="color-{colors[j][1:] if not inverse else colors[i][1:]}"></span>')
                st.metric(label=f'{v} in {m}', label_visibility='visible', value='Rs.'+' {:.2f}'.format(metrics[v, m][0]), delta=round(metrics[v, m][1], 2), delta_color='normal' if metrics[v, m][1] != 0 else 'off')