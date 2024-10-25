import streamlit as st
from streamlit_extras.mandatory_date_range import date_range_picker
from streamlit_extras.grid import grid
from helper.plot import historicalPlot, trendPlot
import pandas as pd
import streamlit.components.v1 as components

def historicalTab(primaryDataframes, primary, prime, second, today, language, inverse=False):
    historicalGrid = grid([1, 5], 1, vertical_align='center')
    defaultStart = today.date() - pd.Timedelta(days=31)
    defaultEnd = today.date() - pd.Timedelta(days=1)

    reverseLanguage = {v: k for k, v in language.items()}

    with historicalGrid.container():
        select1 = st.selectbox(
            language.get(f'Select the {prime}', f'Select the {prime}'),
            [language.get(p, p) for p in primary],
            key='historicalPrime')
        select1 = reverseLanguage.get(select1, select1)

        df = primaryDataframes[select1]
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        date_range = date_range_picker(
            language.get('Select the Date Range', 'Select the Date Range'),
            max_date=defaultEnd,
            min_date=df['Date'].min(),
            default_start=defaultStart,
            default_end=defaultEnd)
        
        secondary_columns = [col for col in df.columns if col != 'Date']
        select2 = st.multiselect(
            language.get(f'Select the {second}s', f'Select the {second}s'),
            [language.get(s, s) for s in secondary_columns],
            [language.get(s, s) for s in secondary_columns],
            key='historicalSecondary')
        select2 = [reverseLanguage.get(s, s) for s in select2]

        secondarySwtich = st.toggle(
            language.get(f'Select all {second}s', f'Select all {second}s'),
            False,
            key='historicalSecondarySwitch')
        if secondarySwtich:
            if select2 == secondary_columns:
                with st.container():
                    st.toast(language.get(f'All {second.lower()}s are already selected', f'All {second.lower()}s are already selected'))
            else:
                select2 = secondary_columns

        timeSwich = st.toggle(
            language.get('Select all time', 'Select all time'),
            False,
            key='historicalTimeSwitch')
        if timeSwich:
            if date_range[0] == df['Date'].min() and date_range[1] == defaultEnd:
                st.toast(language.get('Full historical data is already in view', 'Full historical data is already in view'))
            else:
                date_range = [df['Date'].min(), df['Date'].max()]

    filtered_df = df[(df['Date'] >= date_range[0]) & (df['Date'] <= date_range[1])]

    def secondarys_list_en(select2):
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
        
    def secondarys_list_sn(select2):
        if len(select2) > 1 and not inverse:
            return f'{', '.join([language.get(s, s) for s in select2[:-1]]) + ' සහ ' + language.get(select2[-1], select2[-1])} වෙළඳසැල්වල {language.get(select1, select1)} මිල වෙනස් වීම'
        elif len(select2) > 1 and inverse:
            return f'{language.get(select1, select1)} වෙළඳසැලේ {', '.join([language.get(s, s) for s in select2[:-1]]) + ' සහ ' + language.get(select2[-1], select2[-1])} මිල වෙනස් වීම'
        elif select2 and not inverse:
            return f'{language.get(select2[0], select2[0])} වෙළඳසැලේ {language.get(select1, select1)} මිල වෙනස් වීම'
        elif select2 and inverse:
            return f'{language.get(select1, select1)} වෙළඳසැලේ {language.get(select2[0], select2[0])} මිල වෙනස් වීම'
        else:
            return ''
        
    def secondarys_list_tm(select2):
        if len(select2) > 1 and not inverse:
            return f'{', '.join([language.get(s, s) for s in select2[:-1]]) + ' மற்றும் ' + language.get(select2[-1], select2[-1])} கடைகளில் {language.get(select1, select1)} விலை மாறுதல்'
        elif len(select2) > 1 and inverse:
            return f'{language.get(select1, select1)} கடையில் {', '.join([language.get(s, s) for s in select2[:-1]]) + ' மற்றும் ' + language.get(select2[-1], select2[-1])} விலை மாறுதல்'
        elif select2 and not inverse:
            return f'{language.get(select2[0], select2[0])} கடையில் {language.get(select1, select1)} விலை மாறுதல்'
        elif select2 and inverse:
            return f'{language.get(select1, select1)} கடையில் {language.get(select2[0], select2[0])} விலை மாறுதல்'
        else:
            return ''

    if language.get('language', 'English') == 'Sinhala':
        title = secondarys_list_sn(select2)
    elif language.get('language', 'English') == 'Tamil':
        title = secondarys_list_tm(select2)
    else:
        title = secondarys_list_en(select2)
    historicalChart = historicalPlot(filtered_df, select2, title, language)
    
    with historicalGrid.container():
        components.html(historicalChart, height=400)

    rolling_means = filtered_df[secondary_columns].rolling(window=7, min_periods=1).mean()
    filtered_df['Rolling Mean'] = rolling_means.mean(axis=1)
    filtered_df = filtered_df.round(2)

    if inverse:
        title = language.get(f'Trend of prices in {select1}', f'Trend of prices in {select1}')
    else:
        title = language.get(f'Trend of {select1} prices', f'Trend of {select1} prices')
    trendChart = trendPlot(filtered_df, title, language)

    with historicalGrid.container():
        components.html(trendChart, height=400)