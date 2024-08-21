import streamlit as st
import pandas as pd
import altair as alt

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

markets = dataframes['Beans'].columns[1:]

# Initialize session state for selected vegetable and market
if "selected_vegetable" not in st.session_state:
    st.session_state.selected_vegetable = vegetables[0]  # Default to the first vegetable in the list

if "selected_market" not in st.session_state:
    st.session_state.selected_market = markets[0]  # Default to the first market in the list

# Function to show Filter View
def show_filter_view():
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
    market = col2.selectbox('Select market', options=['All'] + list(dataframe.columns[1:]))

    if market == 'All':
        chart_data = filtered_table.melt(id_vars=['Date'], value_vars=dataframe.columns[1:], var_name='Market', value_name='Price')
        tooltip = ['Date:T', 'Market:N', 'Price:Q']
        legend = alt.Legend(title=None)
    else:
        chart_data = filtered_table[['Date', market]].rename(columns={market: 'Price'})
        tooltip = ['Date:T', 'Price:Q']
        legend = None

    # Separate data into past and future
    past_data = chart_data[chart_data['Date'] < today.date()]
    future_data = chart_data[chart_data['Date'] >= today.date()]

    # Create past chart
    past_chart = alt.Chart(past_data).mark_line().encode(
        x='Date:T',
        y=alt.Y('Price:Q', title='Price (Rs.)'),
        color='Market:N',
        tooltip=tooltip
    )

    # Create future chart
    future_chart = alt.Chart(future_data).mark_line(strokeDash=[5, 3]).encode(
        x='Date:T',
        y=alt.Y('Price:Q', title='Price (Rs.)'),
        color='Market:N',
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

# Function to show Whole View
def show_whole_view():
    openView, scrollView = st.columns([3, 2])

    st.markdown(
        """
    <style>
    [data-testid="stMetricValue"] {
        font-size: 18px;
    }
    [data-testid="stMetric"] {
        padding: 0px;
    }
    .st-emotion-cache-1l269bu.e1f1d6gn3 {
        display: flex;
        align-items: center;
    }
    .st-emotion-cache-e370rw.e1vs0wn31 {
        visibility: hidden;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Scrollable view with buttons arranged in three columns
    with scrollView.container(height=800):
        # Determine how many buttons per column
        cols = st.columns(4)

        # ignoring the selected vegetable
        visible_vegetables = [veg for veg in vegetables if veg != st.session_state.selected_vegetable]

        for idx, veg in enumerate(visible_vegetables):
            with st.container(height=150):
                vegCols = st.columns(6)
                if vegCols[0].button(veg, key=veg):
                    st.session_state.selected_vegetable = veg
                    st.experimental_rerun()

                for i, market in enumerate(markets):  # Displaying the market values
                    df = dataframes[veg]
                    today_value = df.loc[df['Date'] == today.date()]
                    with vegCols[i % 5 + 1].container():
                        st.metric(market, 'Rs. {:.2f}'.format(float(today_value[market].values[0])))

    # Open view showing the selected vegetable's dataframe
    with openView.container(height=800):
        st.title(st.session_state.selected_vegetable)
        graph, values = st.columns([4, 1])

        visible_markets = [market for market in markets if market != st.session_state.selected_market]
        df = dataframes[st.session_state.selected_vegetable]
        filteredDF = df[(df['Date'] >= today.date()) & (df['Date'] <= today.date() + pd.Timedelta(days=6))]

        lineChart = alt.Chart(filteredDF).mark_line().encode(
            x='Date',
            y=st.session_state.selected_market,
            tooltip=['Date:T', f'{st.session_state.selected_market}:Q']
        ).properties(
            width=750,
            height=480,
            title=f'{st.session_state.selected_market} Market Prices'
        )

        with graph.container(height=516):
            st.altair_chart(lineChart)

        for index, row in filteredDF.iterrows():
            with values.container(height=60):
                st.write(f"{row['Date'].strftime('%B %d')} - Rs. {row[st.session_state.selected_market]:.2f}")

        marketCol = st.columns(3)
        for idx, market in enumerate(visible_markets):
            if marketCol[idx % 3].button(market, key=market):
                st.session_state.selected_market = market
                st.experimental_rerun()

# Show the selected view
if view_selection == "Filter View":
    show_filter_view()
else:
    show_whole_view()
