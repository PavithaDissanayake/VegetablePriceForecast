import streamlit as st
from streamlit_extras.mandatory_date_range import date_range_picker
from streamlit_extras.grid import grid
import pandas as pd
from helper.plot import forecastPlot, insightPlot
import streamlit.components.v1 as components

def forecastTab(primaryDataframes, primary, secondaryDataframes, secondary, prime, second, today, language, inverse=False, farmerFlag=False):
    # Create a grid layout for the forecast tab
    forecastGrid = grid([1, 1, 1, 1.5, 1], 1, [1, 0.5, 2], vertical_align='bottom')

    # Reverse the language dictionary for easy lookup
    reverseLanguage = {v: k for k, v in language.items()}

    # Select the primary data for forecasting
    select1 = forecastGrid.selectbox(
        language.get(f'Select the {prime}', f'Select the {prime}'),
        [language.get(p, p) for p in primary],
        key='forecastPrimary')
    select1 = reverseLanguage.get(select1, select1)

    # Get the corresponding DataFrame based on the selection
    df = primaryDataframes[select1]
    defaultStart = max(today.date() - pd.Timedelta(days=7), df['Date'].min())
    
    # Set the default end date and forward days based on farmerFlag
    if farmerFlag:
        defaultEnd = min(today.date() + pd.Timedelta(days=90), df['Date'].max())
        forward = 90
    else:
        defaultEnd = min(today.date() + pd.Timedelta(days=30), df['Date'].max())
        forward = 30

    print(f"today: {today.date()}")
    minDate = defaultStart
    print(f"minDate: {minDate}")
    maxDate = min(today.date() + pd.Timedelta(days=90), df['Date'].max())
    print(f"maxDate: {maxDate}")
    df['Date'] = pd.to_datetime(df['Date']).dt.date  # Ensure the 'Date' column is in date format

    # Create a date range picker for user input
    with forecastGrid.container():
        date_range = date_range_picker(
            language.get('Select the Date Range', 'Select the Date Range'),
            min_date=minDate,
            max_date=maxDate,
            default_start=defaultStart,
            default_end=defaultEnd)
        
    # Allow user to select the type of chart for forecasting
    chartTypes = ['Area', 'Bar', 'Line', 'Scatter']
    chartType = forecastGrid.selectbox(
        language.get('Select the Chart Type', 'Select the Chart Type'),
        [language.get(c, c) for c in chartTypes],
        key='chartType',
        index=2)  # Default to 'Line'
    chartType = reverseLanguage.get(chartType, chartType)

    # Create a multiselect for the secondary columns to forecast
    secondary_columns = [col for col in df.columns if col != 'Date']
    select2 = forecastGrid.multiselect(
        language.get(f'Select the {second}s', f'Select the {second}s'),
        [language.get(s, s) for s in secondary_columns],
        [language.get(s, s) for s in secondary_columns],
        key='forecastSecondary')
    select2 = [reverseLanguage.get(s, s) for s in select2]

    # Toggle to select all secondary items
    with forecastGrid.container():
        secondarySwtich = st.toggle(
            language.get(f'Select all {second}s', f'Select all {second}s'),
            False,
            key='forecastSecondarySwitch')
        if secondarySwtich:
            # Check if all items are already selected
            if select2 == secondary_columns:
                st.toast(language.get(f'All {second.lower()}s are already selected', f'All {second.lower()}s are already selected'))
            else:                
                select2 = secondary_columns  # Select all

        # Toggle to view the full forecast range
        timeSwich = st.toggle(
            language.get('View full forecast', 'View full forecast'),
            False,
            key='forecastTimeSwitch')
        if timeSwich:
            # Check if the full forecast is already in view
            if date_range[0] == minDate and date_range[1] == maxDate:
                st.toast(language.get('Full forecast of 90 days is already in view', 'Full forecast of 90 days is already in view'))
            else:
                date_range = [minDate, maxDate]  # Set to full range

    # Filter the DataFrame based on the selected date range
    filtered_df = df[(df['Date'] >= date_range[0]) & (df['Date'] <= date_range[1])]

    # Generate the forecast chart
    forecastChart = forecastPlot(filtered_df, select2, select1, chartType, today, language)
    
    with forecastGrid.container():
        components.html(forecastChart, height=400)  # Render the forecast chart

    # Swap primary and secondary dataframes based on inverse flag
    if not inverse:
        primaryDataframes, secondaryDataframes = secondaryDataframes, primaryDataframes
    else:
        primary, secondary = secondary, primary

    next_df = pd.DataFrame()  # Initialize DataFrame for the next forecast

    # Prepare the next forecast DataFrame based on the primary dataframes
    for pri, dataframe in primaryDataframes.items():
        filtered_df = dataframe[(dataframe['Date'] >= today.date()) & (dataframe['Date'] <= today.date() + pd.Timedelta(days=forward))]
        filtered_df_no_date = filtered_df.drop(columns=['Date'])
        filtered_df_no_date.columns = [f'{pri} in {col}' for col in filtered_df_no_date.columns]  # Rename columns
        filtered_df_no_date['Date'] = filtered_df['Date']

        if next_df.empty:
            next_df = filtered_df_no_date
        else:
            next_df = pd.merge(next_df, filtered_df_no_date, on='Date', how='outer')  # Merge DataFrames on 'Date'

    next_df = next_df.sort_values(by='Date').reset_index(drop=True)  # Sort the DataFrame by date
    columns = [col for col in next_df.columns if col != 'Date']  # Get columns for the next chart

    # Generate the insight chart for the next forecast
    nextChart = insightPlot(next_df, columns, language)
    
    with forecastGrid.container():
        components.html(nextChart, height=400)  # Render the insight chart

    means = {}  # Initialize a dictionary to store means
    for pri in secondary:
        # Calculate the average of the next forecast for each secondary item
        pri_columns = [col for col in next_df.columns if col.startswith(f'{pri} in')]
        means[pri] = next_df[pri_columns].mean(axis=1).mean()  # Average across rows and columns
    
    highest = max(means, key=means.get)  # Get the highest mean
    lowest = min(means, key=means.get)  # Get the lowest mean

    # Prepare a message based on the highest and lowest expected prices
    if farmerFlag:
        message = f"""
        {language.get('In the coming 3 months', 'In the coming 3 months')}, {language.get(highest, highest)} {language.get('is expected to have the highest average selling price', 'is expected to have the highest average selling price')}.\n
        {language.get('While', 'While')} {language.get(lowest, lowest)} {language.get('is expected to have the lowest average selling price', 'is expected to have the lowest average selling price')}.\n
        {language.get(highest, highest)} {language.get('could be a profitable choice to farm in for the next 3 months', 'could be a profitable choice to farm in for the next 3 months')}.
        """
    else:
        message = f"""
        {language.get('In the coming month', 'In the coming month')} {language.get(lowest, lowest)} {language.get('is expected to be the cheapest in market', 'is expected to be the cheapest in market')}.\n
        {language.get('While', 'While')} {language.get(highest, highest)} {language.get('is expected to be the most expensive', 'is expected to be the most expensive')}.        
        """

    with forecastGrid.container():
        st.html(f'<p class="insight-message">{message}</p>')  # Render the insight message

    # Function to calculate metrics for the primary dataframes
    def getMetrics(dataframes):
        metrics = {}
        for sec, dataframe in dataframes.items():
            for pri in dataframe.columns[1:]:
                today_data = dataframe.loc[dataframe['Date'] == today.date()]
                today_value = today_data[pri].values[0] if not today_data.empty else 0.00

                # Get yesterday's data for comparison
                yesterday_data = dataframe.loc[dataframe['Date'] == today.date() - pd.Timedelta(days=1)]
                yesterday_value = yesterday_data[pri].values[0] if not yesterday_data.empty else 0.00

                change_from_yesterday = today_value - yesterday_value
                metrics[sec, pri] = (today_value, change_from_yesterday)
        
        return metrics
    
    metrics = getMetrics(primaryDataframes)  # Get the metrics for the primary dataframes
    metric = forecastGrid.columns(4)  # Create a 4-column layout for metrics
    
    # Define color palette for metrics
    colors = ['#008ffb', '#00e396', '#feb019', '#ff4560', '#775dd0', '#546E7A', '#26a69a', '#D10CE8', '#FFD700', '#FF6347']
    
    # Function to get colors for the metrics
    def getColors(select, primary, secondary):
        colorMap = {(sec, pri): 0 for pri in primary for sec in secondary}
        for i, s in enumerate(select):
            for p in primary:
                colorMap[s, p] = colors[i]
        k = len(select)
        for i, s in enumerate(secondary):
            flag = False
            for p in primary:
                if colorMap[s, p] == 0:
                    colorMap[s, p] = colors[k]
                    flag = True
            k += 1 if flag else 0
        return colorMap

    if inverse:
        colorMapI = getColors(select2, secondary, primary)
        colorMap = {}
        for a, b in list(colorMapI.keys()):
            colorMap[b, a] = colorMapI[a, b]
    else:
        colorMap = getColors(select2, primary, secondary)

    # Render the metrics for the primary dataframes
    for i, m in enumerate(primary):
        for j, v in enumerate(secondary):
            with metric[j % 4].container():
                st.html('<span class="metric-div"></span>')
                st.html(f'<span class="color-{colorMap[v, m][1:]}"></span>')
                st.metric(
                    label=f'{language.get(f'{v} in {m}', f'{v} in {m}')}',
                    label_visibility='visible',
                    value=f'{language.get('Rs', 'Rs')}.'+' {:.2f}'.format(metrics[v, m][0]),
                    delta=f'{language.get('Rs', 'Rs')}.'+' {:.2f}'.format(round(metrics[v, m][1], 2)),
                    delta_color='normal' if metrics[v, m][1] != 0 else 'off')