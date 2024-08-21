import streamlit as st
import pandas as pd
import altair as alt

today = pd.Timestamp('2023-01-24')

st.set_page_config(layout="wide")

# title
st.title('Vegetable Market Price')
st.write('---')

col1, col2 = st.columns([3, 4])

col11, col12 = col1.columns([1, 1])

col12.write('Today')
col12.write(today.date())

vegetable = col11.selectbox('Select the vegetable', options=('Beans', 'Carrots'))

if vegetable == 'Beans':
    dataframe = 'Beans.csv'
    image = 'Beans.png'
elif vegetable == 'Carrots':
    dataframe = 'Carrot.csv'
    image = 'Carrot.png'

table = pd.read_csv(dataframe)

# configuring date elements
table['Date'] = pd.to_datetime(table['Date'])
table['Date'] = table['Date'].dt.date
viewTable = table.sort_values('Date', ascending=False)

col11, col12, col13 = col1.columns([1, 1, 1])

col11.image(image, use_column_width=True)

# TODO: make the metrics automatic
# Kandy market value comparison
today_data = table.loc[table['Date'] == today.date()]
if today_data.empty:
    today_data = 0.00
else:
    today_data = float(today_data['Kandy'].values[0])

yesterday_data = table.loc[table['Date'] == today.date() - pd.Timedelta(days=1)]
if yesterday_data.empty:
    yesterday_data = 0.00
else:
    yesterday_data = float(yesterday_data['Kandy'].values[0])

change_from_yesterday = today_data - yesterday_data

if change_from_yesterday == 0:
    col12.metric('Kandy', 'Rs. {:.2f}'.format(today_data), change_from_yesterday, delta_color='off')
else :
    col12.metric('Kandy', 'Rs. {:.2f}'.format(today_data), change_from_yesterday, delta_color='inverse')

# Dambulla market value comparison
today_data = table.loc[table['Date'] == today.date()]
if today_data.empty:
    today_data = 0.00
else:
    today_data = float(today_data['Dambulla'].values[0])

yesterday_data = table.loc[table['Date'] == today.date() - pd.Timedelta(days=1)]
if yesterday_data.empty:
    yesterday_data = 0.00
else:
    yesterday_data = float(yesterday_data['Dambulla'].values[0])

change_from_yesterday = today_data - yesterday_data

if change_from_yesterday == 0:
    col13.metric('Dambulla', 'Rs. {:.2f}'.format(yesterday_data), change_from_yesterday, delta_color='off')
else :
    col13.metric('Dambulla', 'Rs. {:.2f}'.format(yesterday_data), change_from_yesterday, delta_color='inverse')

# selecting the time frame
col21, col22 = col2.columns(2)
start_date = pd.Timestamp(col21.date_input('Select start date', value=pd.Timestamp('2023-01-01'), min_value=table['Date'].min(), max_value=table['Date'].max()))
end_date = pd.Timestamp(col22.date_input('Select end date', value=pd.Timestamp('2023-02-28'), min_value=table['Date'].min(), max_value=table['Date'].max()))

filtered_table = table[(table['Date'] >= start_date.date()) & (table['Date'] <= end_date.date())]

# selecting the market
market = col2.selectbox('Select market', options=['All'] + list(table.columns[1:]))

if market == 'All':
    chart_data = filtered_table.melt(id_vars=['Date'], value_vars=['Kandy', 'Dambulla'], var_name='Market', value_name='Price')
    tooltip=['Date:T', 'Market:N', 'Price:Q']
    legend = alt.Legend(title=None)
else:
    chart_data = filtered_table[['Date', market]].rename(columns={market: 'Price'})
    tooltip=['Date:T', 'Price:Q']
    legend = None

# separate data into past and future
past_data = chart_data[chart_data['Date'] < today.date()]
future_data = chart_data[chart_data['Date'] >= today.date()]

# create past chart
past_chart = alt.Chart(past_data).mark_line().encode(
    x='Date:T',
    y=alt.Y('Price:Q', title='Price (Rs.)'),
    color='Market:N',
    tooltip=tooltip
)

# create future chart
future_chart = alt.Chart(future_data).mark_line(strokeDash=[5, 3]).encode(
    x='Date:T',
    y=alt.Y('Price:Q', title='Price (Rs.)'),
    color='Market:N',
    tooltip=tooltip
)

# vertical line for today
today_line = alt.Chart(pd.DataFrame({'Date': [today]})).mark_rule(
    color='gray', strokeDash=[5 ,3]
).encode(
    x='Date:T',
    tooltip=['Date:T']
)

# today label
today_label = alt.Chart(pd.DataFrame({'Date': [today], 'label': ['Today']})).mark_text(
    align='left', dx=5, dy=105, color='gray'
).encode(
    x='Date:T',
    text='label',
    tooltip=['Date:T']
)

# combine past and future charts
if today < start_date or today > end_date:
    combined_chart = alt.layer(past_chart, future_chart).properties(
        title='Market Price over Time'
    )
else :
    combined_chart = alt.layer(past_chart, future_chart, today_line, today_label).properties(
        title='Market Price over Time'
    )

if market != 'All':
    combined_chart = combined_chart.configure_legend(disable=True)

col2.altair_chart(combined_chart, use_container_width=True)

col2.dataframe(filtered_table, use_container_width=True, hide_index=True)
