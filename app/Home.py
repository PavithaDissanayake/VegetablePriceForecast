import streamlit as st

st.set_page_config(
    page_title='Vegetable Price Forecast System',
    page_icon='🥦',
    layout="wide",
    initial_sidebar_state="collapsed"
)
st.html('./styles/Home.html')

welcome, separator, choice = st.columns([1.2, 0.05, 1])

with welcome.container():
    st.markdown("""
                <div class="home-page-title">
                    <p>Welcome to</p>
                    <h1><a href="/" target="_self">Vegetable Price Forecasting System</a></h1>
                </div>
                """,
                unsafe_allow_html=True)

with separator.container():
    st.markdown("""
                <div class="separator"></div>
                """,
                unsafe_allow_html=True)

with choice.container():
    st.markdown("""
                <div class="home-page-choice">
                    <h1>Are you a</h1>
                    <div class="choice">
                        <a href="/Consumer" class="button" target="_self">Consumer</a>
                        <a href="/Farmer" class="button" target="_self">Farmer</a> 
                    </div>
                    <h1>?</h1>
                </div>              
                """,
                unsafe_allow_html=True)
