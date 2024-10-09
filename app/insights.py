import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from streamlit_extras.grid import grid
import os

def insights():
    folder = './Data/NewData'
    vegetables = sorted([f.split('.')[0] for f in [f for f in os.listdir(folder) if f.endswith('.csv')]][:-1])
    st.selectbox('Select Vegetable', vegetables)