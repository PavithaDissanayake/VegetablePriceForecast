# FOR TESTING OUT STUFF

import streamlit as st

# Create two columns
col1, col2 = st.columns(2)

# Add scrollable content to the first column
with col1.container(height=600):  # You can adjust the height
    for i in range(100):
        st.write(i)

# Add scrollable content to the second column
with col2.container(height=300):  # You can adjust the height
    st.write("Column 2")
    st.write("Content" * 100)  # Add content to make it scrollable
