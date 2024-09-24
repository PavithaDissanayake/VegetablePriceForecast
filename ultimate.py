import streamlit as st
from streamlit_theme import st_theme
import pandas as pd
import altair as alt
import firebase_admin
from firebase_admin import credentials, firestore
import os

st.set_page_config(layout="wide")
today = pd.Timestamp('2023-01-23')
defaultStart = today.date() - pd.Timedelta(days=7)
defaultEnd = today.date() + pd.Timedelta(days=7)
st.html('./styles/ultimate.html')

theme = st_theme()
with open('./styles/ultimate.html', 'r') as f:
    css = f.read()
div_color = theme['secondaryBackgroundColor']

if theme['base'] == 'light':
    maxColor = '#ffd5d4'
    minColor = '#bde7bd'
    maxText = '#460000'
    minText = '#013220'
elif theme['base'] == 'dark':
    maxColor = '#460000'
    minColor = '#013220'
    maxText = '#ffd5d4'
    minText = '#bde7bd'

css = css.replace('maxColor', maxColor)
css = css.replace('minColor', minColor)

css = css.replace('divColor', div_color)
st.markdown(css, unsafe_allow_html=True)

# credentials = credentials.Certificate('./vegetablepriceforecast-8c0db-firebase-adminsdk-8yuue-094562d130.json')
# firebase_admin.initialize_app(credentials)

# db = firestore.client()

folder = './Data'
vegetables = [f.split('.')[0] for f in [f for f in os.listdir(folder) if f.endswith('.csv')]]

# for veg in vegetables[-2:]:
#     temp_df = pd.read_csv(f'./Data/{veg}.csv')
#     temp_df['Date'] = pd.to_datetime(temp_df['Date'])
#     temp_data = temp_df.to_dict(orient='records')
#     for data in temp_data:
#         db.collection(veg).add(data)

data, plot = st.columns([2, 3])

# choose a vegetable
vegetable = data.selectbox('Select the vegetable', options=vegetables)
df = pd.read_csv(f'./Data/{vegetable}.csv')
df['Date'] = pd.to_datetime(df['Date']).dt.date

markets = df.drop(columns='Date').columns

metric = data.columns(3)

# create metrics for the following week
filtered = df[(df['Date'] >= today.date()) & (df['Date'] <= today.date() + pd.Timedelta(days=6))]

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

metrics = calculate_metrics(df, today)

max_value = max(metrics.values(), key=lambda x: x[0])
min_value = min(metrics.values(), key=lambda x: x[0])

maxMarkets = [k for k, v in metrics.items() if v == max_value]
minMarkets = [k for k, v in metrics.items() if v == min_value]

# show metrics and data for the week
for i, m in enumerate(markets):
    with metric[i % 3].container():
        st.html(f'<span class="metricsDiv"></span>')
        if max_value != min_value:
            if m in maxMarkets:
                st.html(f'<span class="maxMarket"></span>')
            elif m in minMarkets:
                st.html(f'<span class="minMarket"></span>')
        st.metric(label=m, label_visibility='visible', value='Rs. {:.2f}'.format(metrics[m][0]), delta=round(metrics[m][1], 2), delta_color='inverse' if metrics[m][1] != 0 else 'off')
        with st.container():
            with st.expander('Coming week'):
                for index, day in filtered.iterrows():
                    if day['Date'] != today.date():
                        st.write(f"{day['Date'].strftime('%B %d')} - Rs. {day[m]:.2f}")

# start and end dates for the chart
start, end = plot.columns([1, 1])
start_date = pd.Timestamp(start.date_input('Select start date', value=defaultStart, min_value=df['Date'].min(), max_value=df['Date'].max()))
end_date = pd.Timestamp(end.date_input('Select end date', value=defaultEnd, min_value=df['Date'].min(), max_value=df['Date'].max()))

# market selection
market = start.multiselect('Select market', options=list(markets), default=list(markets))

filtered_table = df[(df['Date'] >= start_date.date()) & (df['Date'] <= end_date.date())]

def create_area_chart(data, start_date, end_date, markets, today):
    area_data = data.melt(id_vars=['Date'], value_vars=markets, var_name='Market', value_name='Price')

    past_data = area_data[area_data['Date'] <= today.date()]
    future_data = area_data[area_data['Date'] >= today.date()]

    past_chart = alt.Chart(past_data).mark_area().encode(
        x='Date:T',
        y=alt.Y('Price:Q', title='Price (Rs.)'),
        color='Market:N',
        tooltip=['Date:T', 'Market:N', 'Price:Q']
    ).properties(height=550)

    future_chart = alt.Chart(future_data).mark_area(opacity=0.5).encode(
        x='Date:T',
        y='Price:Q',
        color='Market:N',
        tooltip=['Date:T', 'Market:N', 'Price:Q']
    ).properties(height=550)

    # Vertical line for today
    today_line = alt.Chart(pd.DataFrame({'Date': [today]})).mark_rule(
        color='gray', strokeDash=[5, 3]
    ).encode(x='Date:T', tooltip=['Date:T'])

    # Today label
    today_label = alt.Chart(pd.DataFrame({'Date': [today], 'label': ['Today']})).mark_text(
        align='left', dx=5, dy=-170, color='gray'
    ).encode(x='Date:T', text='label')

    if today < start_date or today > end_date:
        combined_chart = alt.layer(past_chart, future_chart).properties(
            title='Market Price over Time', height=550
        )
    else:
        combined_chart = alt.layer(past_chart, future_chart, today_line, today_label).properties(
            title='Market Price over Time', height=550
        )

    return combined_chart

def create_bar_chart(data, start_date, end_date, markets, today):
    bar_data = data.melt(id_vars=['Date'], value_vars=markets, var_name='Market', value_name='Price')

    past_data = bar_data[bar_data['Date'] < today.date()]
    future_data = bar_data[bar_data['Date'] >= today.date()]

    num_days = (end_date - start_date).days
    bar_width = 3 / num_days if num_days > 0 else 3

    past_chart = alt.Chart(past_data).mark_bar(size=bar_width*100).encode(
        x='Date:T',
        y=alt.Y('Price:Q', title='Price (Rs.)'),
        color='Market:N',
        tooltip=['Date:T', 'Market:N', 'Price:Q']
    ).properties(height=550)

    future_chart = alt.Chart(future_data).mark_bar(opacity=0.5, size=bar_width*100).encode(
        x='Date:T',
        y='Price:Q',
        color='Market:N',
        tooltip=['Date:T', 'Market:N', 'Price:Q']
    ).properties(height=550)

    # Vertical line for today
    today_line = alt.Chart(pd.DataFrame({'Date': [today]})).mark_rule(
        color='gray', strokeDash=[5, 3]
    ).encode(x='Date:T', tooltip=['Date:T'])

    # Today label
    today_label = alt.Chart(pd.DataFrame({'Date': [today], 'label': ['Today']})).mark_text(
        align='left', dx=5, dy=-170, color='gray'
    ).encode(x='Date:T', text='label')

    if today < start_date or today > end_date:
        combined_chart = alt.layer(past_chart, future_chart).properties(
            title='Market Price over Time', height=550
        )
    else:
        combined_chart = alt.layer(past_chart, future_chart, today_line, today_label).properties(
            title='Market Price over Time', height=550
        )

    return combined_chart

def create_line_chart(data, start_date, end_date, markets, today):
    chart_data = data.melt(id_vars=['Date'], value_vars=markets, var_name='Market', value_name='Price')
    
    # Separate data into past and future
    past_data = chart_data[chart_data['Date'] <= today.date()]
    future_data = chart_data[chart_data['Date'] >= today.date()]

    # Create past chart
    past_chart = alt.Chart(past_data).mark_line().encode(
        x='Date:T',
        y=alt.Y('Price:Q', title='Price (Rs.)'),
        color=alt.Color('Market:N'),
        tooltip=['Date:T', 'Market:N', 'Price:Q']
    ).properties(height=550)

    # Create future chart
    future_chart = alt.Chart(future_data).mark_line(strokeDash=[5, 3]).encode(
        x='Date:T',
        y='Price:Q',
        color='Market:N',
        tooltip=['Date:T', 'Market:N', 'Price:Q']
    ).properties(height=550)

    # Vertical line for today
    today_line = alt.Chart(pd.DataFrame({'Date': [today]})).mark_rule(
        color='gray', strokeDash=[5, 3]
    ).encode(x='Date:T', tooltip=['Date:T'])

    # Today label
    today_label = alt.Chart(pd.DataFrame({'Date': [today], 'label': ['Today']})).mark_text(
        align='left', dx=5, dy=-170, color='gray'
    ).encode(x='Date:T', text='label')

    # Combine past and future charts
    if today < start_date or today > end_date:
        combined_chart = alt.layer(past_chart, future_chart).properties(
            title='Market Price over Time', height=550
        )
    else:
        combined_chart = alt.layer(past_chart, future_chart, today_line, today_label).properties(
            title='Market Price over Time', height=550
        )
    
    return combined_chart

def create_scatter_plot(data, start_date, end_date, markets, today):
    scatter_data = data.melt(id_vars=['Date'], value_vars=markets, var_name='Market', value_name='Price')

    past_data = scatter_data[scatter_data['Date'] < today.date()]
    future_data = scatter_data[scatter_data['Date'] >= today.date()]

    num_days = (end_date - start_date).days
    scatter_size = 100 / num_days if num_days > 0 else 100

    past_chart = alt.Chart(past_data).mark_circle(size=scatter_size*100).encode(
        x='Date:T',
        y=alt.Y('Price:Q', title='Price (Rs.)'),
        color='Market:N',
        tooltip=['Date:T', 'Market:N', 'Price:Q']
    ).properties(height=550)

    future_chart = alt.Chart(future_data).mark_circle(opacity=0.5, size=scatter_size*100).encode(
        x='Date:T',
        y='Price:Q',
        color='Market:N',
        tooltip=['Date:T', 'Market:N', 'Price:Q']
    ).properties(height=550)

    # Vertical line for today
    today_line = alt.Chart(pd.DataFrame({'Date': [today]})).mark_rule(
        color='gray', strokeDash=[5, 3]
    ).encode(x='Date:T', tooltip=['Date:T'])

    # Today label
    today_label = alt.Chart(pd.DataFrame({'Date': [today], 'label': ['Today']})).mark_text(
        align='left', dx=5, dy=170, color='gray'
    ).encode(x='Date:T', text='label')

    if today < start_date or today > end_date:
        combined_chart = alt.layer(past_chart, future_chart).properties(
            title='Market Price over Time', height=550
        )
    else:
        combined_chart = alt.layer(past_chart, future_chart, today_line, today_label).properties(
            title='Market Price over Time', height=550
        )

    return combined_chart

def create_step_chart(data, start_date, end_date, markets, today):
    step_data = data.melt(id_vars=['Date'], value_vars=markets, var_name='Market', value_name='Price')

    past_data = step_data[step_data['Date'] <= today.date()]
    future_data = step_data[step_data['Date'] >= today.date()]

    past_chart = alt.Chart(past_data).mark_line(interpolate='step-after').encode(
        x='Date:T',
        y=alt.Y('Price:Q', title='Price (Rs.)'),
        color='Market:N',
        tooltip=['Date:T', 'Market:N', 'Price:Q']
    ).properties(height=550)

    future_chart = alt.Chart(future_data).mark_line(interpolate='step-after', strokeDash=[5, 3]).encode(
        x='Date:T',
        y='Price:Q',
        color='Market:N',
        tooltip=['Date:T', 'Market:N', 'Price:Q']
    ).properties(height=550)

    # Vertical line for today
    today_line = alt.Chart(pd.DataFrame({'Date': [today]})).mark_rule(
        color='gray', strokeDash=[5, 3]
    ).encode(x='Date:T', tooltip=['Date:T'])

    # Today label
    today_label = alt.Chart(pd.DataFrame({'Date': [today], 'label': ['Today']})).mark_text(
        align='left', dx=5, dy=-170, color='gray'
    ).encode(x='Date:T', text='label')

    if today < start_date or today > end_date:
        combined_chart = alt.layer(past_chart, future_chart).properties(
            title='Market Price over Time', height=550
        )
    else:
        combined_chart = alt.layer(past_chart, future_chart, today_line, today_label).properties(
            title='Market Price over Time', height=550
        )

    return combined_chart

def show_raw_data(data, markets, today):
    
    selected_columns = ['Date'] + markets
    final_data = data[selected_columns]

    def highlight(row):
        return [f'background-color: {theme['primaryColor']}' if row['Date'] == today.date() else f'color: grey' if row['Date'] > today.date() else '' for _ in row]
    
    final_data = final_data.style.apply(highlight, axis=1)

    format_dict = {column: lambda x: f'Rs. {x:.2f}' if pd.notnull(x) else 'N/A' for column in final_data.columns[1:]}
    
    final_data = final_data.format(format_dict)

    return final_data

# Choose the chart type
chart_type = end.selectbox("Select chart type", index=2, options=["Area Chart", "Bar Chart", "Line Chart", "Scatter Plot", "Step Chart", "Raw Data"])

combined_chart = None
if chart_type == "Area Chart":
    combined_chart = create_area_chart(filtered_table, start_date, end_date, market, today)
elif chart_type == "Bar Chart":
    combined_chart = create_bar_chart(filtered_table, start_date, end_date, market, today)
elif chart_type == "Line Chart":
    combined_chart = create_line_chart(filtered_table, start_date, end_date, market, today)
elif chart_type == "Scatter Plot":
    combined_chart = create_scatter_plot(filtered_table, start_date, end_date, market, today)
elif chart_type == "Step Chart":
    combined_chart = create_step_chart(filtered_table, start_date, end_date, market, today)
else:
    plot.dataframe(show_raw_data(filtered_table, market, today), use_container_width=True, height=550, hide_index=True, column_order=['Date']+sorted(filtered_table.columns[1:]))

if combined_chart is not None:
    with plot.container():
        st.html(f'<span class="chartDiv"></span>')
        st.altair_chart(combined_chart, use_container_width=True)
