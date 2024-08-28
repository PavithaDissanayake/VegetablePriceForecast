import streamlit as st
import altair as alt
import pandas as pd
import altair as alt

def show_filter_view(today, dataframes, vegetables):
    col1, col2 = st.columns([3, 4])
    col11, col12 = col1.columns([1, 1])
    
    col12.write('Today')
    col12.write(today.date())

    vegetable = col11.selectbox('Select the vegetable', options=vegetables)

    # Load the selected vegetable's data
    dataframe = dataframes[vegetable]

    # Configure date elements
    dataframe['Date'] = pd.to_datetime(dataframe['Date'])
    dataframe['Date'] = dataframe['Date'].dt.date
    viewTable = dataframe.sort_values('Date', ascending=False)

    metricCol = col1.columns([1, 1, 1])

    # Function to calculate metrics for all markets
    def calculate_metrics(dataframe, today):
        metrics = {}
        for market in dataframe.columns[1:]:
            today_data = dataframe.loc[dataframe['Date'] == today.date()]
            today_value = today_data[market].values[0] if not today_data.empty else 0.00

            yesterday_data = dataframe.loc[dataframe['Date'] == today.date() - pd.Timedelta(days=1)]
            yesterday_value = yesterday_data[market].values[0] if not yesterday_data.empty else 0.00

            change_from_yesterday = today_value - yesterday_value
            metrics[market] = (today_value, change_from_yesterday)

        return metrics

    metrics = calculate_metrics(dataframe, today)

    # Display metrics for all markets
    for idx, market in enumerate(dataframe.columns[1:]):
        if metrics[market][1] == 0:
            with metricCol[idx % 3].container(height=130):
                st.metric(market, 'Rs. {:.2f}'.format(metrics[market][0]), metrics[market][1], delta_color='off')
        else:
            with metricCol[idx % 3].container(height=130):
                st.metric(market, 'Rs. {:.2f}'.format(metrics[market][0]), metrics[market][1], delta_color='inverse')

    # Selecting the time frame
    col21, col22 = col2.columns(2)
    start_date = pd.Timestamp(col21.date_input('Select start date', value=pd.Timestamp('2023-01-01'), min_value=dataframe['Date'].min(), max_value=dataframe['Date'].max()))
    end_date = pd.Timestamp(col22.date_input('Select end date', value=pd.Timestamp('2023-02-28'), min_value=dataframe['Date'].min(), max_value=dataframe['Date'].max()))

    filtered_table = dataframe[(dataframe['Date'] >= start_date.date()) & (dataframe['Date'] <= end_date.date())]

    # Selecting the market
    market = col2.multiselect('Select market', options=list(dataframe.columns[1:]), default=list(dataframe.columns[1:]))

    if len(market) > 1:
        chart_data = filtered_table.melt(id_vars=['Date'], value_vars=market, var_name='Market', value_name='Price')
        tooltip = ['Date:T', 'Market:N', 'Price:Q']
        legend = alt.Legend(title=None)
    else:
        chart_data = filtered_table.melt(id_vars=['Date'], value_vars=market, var_name='Market', value_name='Price')
        tooltip = ['Date:T', 'Price:Q']
        legend = None

    # Separate data into past and future
    past_data = chart_data[chart_data['Date'] < today.date()]
    future_data = chart_data[chart_data['Date'] >= today.date()]

    # Create past chart
    past_chart = alt.Chart(past_data).mark_line().encode(
        x='Date:T',
        y=alt.Y('Price:Q', title='Price (Rs.)'),
        color=alt.Color('Market:N', legend=legend),
        tooltip=tooltip
    )

    # Create future chart
    future_chart = alt.Chart(future_data).mark_line(strokeDash=[5, 3]).encode(
        x='Date:T',
        y=alt.Y('Price:Q', title='Price (Rs.)'),
        color=alt.Color('Market:N', legend=legend),
        tooltip=tooltip
    )

    # Vertical line for today
    today_line = alt.Chart(pd.DataFrame({'Date': [today]})).mark_rule(
        color='gray', strokeDash=[5, 3]
    ).encode(
        x='Date:T',
        tooltip=['Date:T']
    )

    # Today label
    today_label = alt.Chart(pd.DataFrame({'Date': [today], 'label': ['Today']})).mark_text(
        align='left', dx=5, dy=105, color='gray'
    ).encode(
        x='Date:T',
        text='label',
        tooltip=['Date:T']
    )

    # Combine past and future charts
    if today < start_date or today > end_date:
        combined_chart = alt.layer(past_chart, future_chart).properties(
            title='Market Price over Time'
        )
    else:
        combined_chart = alt.layer(past_chart, future_chart, today_line, today_label).properties(
            title='Market Price over Time'
        )

    if market != 'All':
        combined_chart = combined_chart.configure_legend(disable=True)

    col2.altair_chart(combined_chart, use_container_width=True)
    col2.dataframe(filtered_table, use_container_width=True, hide_index=True)