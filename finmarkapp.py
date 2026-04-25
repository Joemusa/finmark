import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("📊 Financial Dashboard")

@st.cache_data
def load_data():
    return pd.read_csv("clean_data.csv")

df = load_data()
