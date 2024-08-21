import streamlit as st
import pandas as pd
import altair as alt

#initialization
st.set_page_config(layout="wide")
today = pd.Timestamp('2023-01-23')

st.sidebar.title('Vegetable Market Price')
st.sidebar.write('---')
st.sidebar.button("Whole View")
st.sidebar.button("Filter View")

# Vegetbles and markets
vegetables = ['Beans', 'BeetRoot', 'Brinjals', 'Cabbage', 'Capsicum', 'Carrot', 'Cucumber', 'Knolkhol', 'LadiesFingers', 'Leaks', 'Lime', 'Manioc', 'Pumpkin', 'Raddish', 'Tomato']
dataframes = {veg: pd.read_csv(f'./Data/{veg}.csv') for veg in vegetables}
for veg in vegetables :
    dataframes[veg]['Date'] = pd.to_datetime(dataframes[veg]['Date'])
    dataframes[veg]['Date'] = dataframes[veg]['Date'].dt.date
markets = dataframes['Beans'].columns[1:]

# Initialize session state for selected vegetable
if "selected_vegetable" not in st.session_state:
    st.session_state.selected_vegetable = vegetables[0]  # Default to the first vegetable in the list

if "selected_market" not in st.session_state:
    st.session_state.selected_market = markets[0]  # Default to the first market in the list

# Layout
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
        
        with st.container(height=150) :
            vegCols = st.columns(6)
            if vegCols[0].button(veg, key=veg):
                st.session_state.selected_vegetable = veg
                st.experimental_rerun()

            for i, market in enumerate(markets): # Displaying the market values
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

    with graph.container(height=516) :
        st.altair_chart(lineChart)

    for index, row in filteredDF.iterrows():
        with values.container(height=60) :
            st.write(f"{row['Date'].strftime('%B %d')} - Rs. {row[st.session_state.selected_market]:.2f}")

    marketCol = st.columns(3)
    for idx, market in enumerate(visible_markets):
        if marketCol[idx % 3].button(market, key=market):
            st.session_state.selected_market = market
            st.experimental_rerun()

