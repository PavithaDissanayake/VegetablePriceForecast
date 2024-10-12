import streamlit as st
import pandas as pd
import altair as alt
from streamlit_extras.grid import grid
import json

def insights(vegetables):

    columns = st.columns([1, 3])
    vegetable = columns[0].selectbox('Select a vegetable', vegetables)
    insightGrid = grid(2, 1, vertical_align="bottom")

    with open (f'./Insights/{vegetable}.json', 'r') as f:
        data = json.load(f)

    mean_weekly = data['mean_weekly']
    mean_monthly = data['mean_monthly']
    trend = data['trend']

    mean_weekly_df = pd.DataFrame(list(mean_weekly.items()), columns=['Day of the Week', 'Change'])
    mean_monthly_df = pd.DataFrame(list(mean_monthly.items()), columns=['Month', 'Change'])
    trend_df = pd.DataFrame(trend)

    trend_df['ds'] = pd.to_datetime(trend_df['ds'])
    trend_df.rename(columns={'trend': 'Trend'}, inplace=True)

    days_mapping = {
        '0': 'Monday',
        '1': 'Tuesday',
        '2': 'Wednesday',
        '3': 'Thursday',
        '4': 'Friday',
        '5': 'Saturday',
        '6': 'Sunday'
    }

    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    mean_weekly_df['Day of the Week'] = mean_weekly_df['Day of the Week'].replace(days_mapping)
    mean_weekly_df['Day of the Week'] = pd.Categorical(mean_weekly_df['Day of the Week'], categories=days_order, ordered=True)

    months_mapping = {
        '1': 'January',
        '2': 'February',
        '3': 'March',
        '4': 'April',
        '5': 'May',
        '6': 'June',
        '7': 'July',
        '8': 'August',
        '9': 'September',
        '10': 'October',
        '11': 'November',
        '12': 'December'
    }

    months_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    mean_monthly_df['Month'] = mean_monthly_df['Month'].replace(months_mapping)
    mean_monthly_df['Month'] = pd.Categorical(mean_monthly_df['Month'], categories=months_order, ordered=True)

    mean_weekly_chart = alt.Chart(mean_weekly_df).mark_line().encode(
        x=alt.X('Day of the Week', axis=alt.Axis(labelAngle=0)),
        y='Change'
    ).properties(
        title=f'{vegetable} price change through days in a week'
    )

    mean_monthly_chart = alt.Chart(mean_monthly_df).mark_line().encode(
        x=alt.X('Month', axis=alt.Axis(labelAngle=0)),
        y='Change'
    ).properties(
        title=f'{vegetable} price change through months in a year'
    )

    trend_chart = alt.Chart(trend_df).mark_line().encode(
        x='ds',
        y='Trend'
    ).properties(
        title=f'{vegetable} price trend through years'
    )

    with insightGrid.container():
        st.html(f'<span class="chartDiv"></span>')
        st.altair_chart(mean_weekly_chart, use_container_width=True)

    with insightGrid.container():
        st.html(f'<span class="chartDiv"></span>')
        st.altair_chart(mean_monthly_chart, use_container_width=True)
    
    with insightGrid.container():
        st.html(f'<span class="chartDiv"></span>')
        st.altair_chart(trend_chart, use_container_width=True)