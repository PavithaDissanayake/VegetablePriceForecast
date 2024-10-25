import streamlit as st
import json

st.set_page_config(
    page_title='Vegetable Price Forecast System',
    page_icon='🥦',
    layout="wide",
    initial_sidebar_state="collapsed"
)
st.html('./styles/Home.html')

if 'language' not in st.session_state:
    st.session_state['language'] = 'English'

language = {}
if st.session_state['language'] == 'සිංහල':
    with open('./languages/sinhala.json', 'r', encoding='utf-8') as file:
        language = json.load(file)
elif st.session_state['language'] == 'தமிழ்':
    with open('./languages/tamil.json', 'r', encoding='utf-8') as file:
        language = json.load(file)

newlang = st.sidebar.selectbox(
    language.get('Select the Language', 'Select the Language'),
    ['English', 'සිංහල', 'தமிழ்'],
    index=['English', 'සිංහල', 'தமிழ்'].index(st.session_state['language'])  # Maintain the previous selection
)

if newlang != st.session_state['language']:
    st.session_state['language'] = newlang
    st.rerun()

with st.sidebar.container():
    st.html('<span class="admin-button-container"></span>')
    st.markdown("""
                <div class="admin-button">
                    <a href="/Admin-Page" class="button" target="_self">Login as Admin 🔓</a>
                </div>
                """, unsafe_allow_html=True)

welcome, separator, choice = st.columns([1.2, 0.05, 1])

with welcome.container():
    st.markdown(f"""
                <div class="home-page-title">
                    <p>{language.get('Welcome to', 'Welcome to')}</p>
                    <h1><a href="/" target="_self">{language.get('Vegetable Price Forecasting System', 'Vegetable Price Forecasting System')}</a></h1>
                </div>
                """,
                unsafe_allow_html=True)

with separator.container():
    st.markdown("""
                <div class="separator"></div>
                """,
                unsafe_allow_html=True)

with choice.container():
    st.markdown(f"""
                <div class="home-page-choice">
                    <h1>{language.get('Are you a', 'Are you a')}</h1>
                    <div class="choice">
                        <a href="/Consumer" class="button" target="_self">{language.get('Consumer', 'Consumer')}</a>
                        <a href="/Farmer" class="button" target="_self">{language.get('Farmer', 'Farmer')}</a> 
                    </div>
                    <h1>?</h1>
                </div>              
                """,
                unsafe_allow_html=True)
