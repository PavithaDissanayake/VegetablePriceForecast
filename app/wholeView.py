import streamlit as st
import pandas as pd
import altair as alt

def show_whole_view(today, dataframes, vegetables, markets):
    openView, scrollView = st.columns([3, 2])

    st.html("./styles/wholeView.html")

    # Scrollable view with buttons arranged in three columns
    with scrollView.container(height=800):
        # Determine how many buttons per column
        cols = st.columns(4)

        # ignoring the selected vegetable
        visible_vegetables = [veg for veg in vegetables if veg != st.session_state.selected_vegetable]

        for idx, veg in enumerate(visible_vegetables):
            with st.container(height=150):
                st.html(f'<span class="vegetablesDiv"></span>')
                vegCols = st.columns(6)
                if vegCols[0].button(veg, key=veg):
                    st.session_state.selected_vegetable = veg
                    st.rerun()

                for i, market in enumerate(markets):  # Displaying the market values
                    df = dataframes[veg]
                    today_value = df.loc[df['Date'] == today.date()]
                    with vegCols[i % 5 + 1].container():
                        st.metric(market, 'Rs. {:.2f}'.format(float(today_value[market].values[0])))

    # Open view showing the selected vegetable's dataframe
    with openView.container(height=800):
        st.title(st.session_state.selected_vegetable)

        visible_markets = [market for market in markets if market != st.session_state.selected_market]
        df = dataframes[st.session_state.selected_vegetable]
        filteredDF = df[(df['Date'] >= today.date()) & (df['Date'] <= today.date() + pd.Timedelta(days=6))]

        lineChart = alt.Chart(filteredDF).mark_line().encode(
            x='Date',
            y=st.session_state.selected_market,
            tooltip=['Date:T', f'{st.session_state.selected_market}:Q']
        ).properties(
            title=f'{st.session_state.selected_market} Market Prices'
        )

        with st.container(height=516):
            graph, values = st.columns([4, 1])
            with graph.container(height=516):
                st.altair_chart(lineChart, use_container_width=True)

            with values.container():
                st.html(f'<span class="valuesDiv"></span>')
                for index, row in filteredDF.iterrows():
                    with st.container(height=60):
                        st.write(f"{row['Date'].strftime('%B %d')} - Rs. {row[st.session_state.selected_market]:.2f}")

        with st.container():
            marketCol = st.columns(3)
            for idx, market in enumerate(visible_markets):
                with marketCol[idx % 3].container(height=70):
                    st.html(f'<span class="marketsDiv"></span>')
                    if st.button(market, key=market):
                        st.session_state.selected_market = market
                        st.rerun()