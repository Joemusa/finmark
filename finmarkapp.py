import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("📊 Financial Dashboard")

@st.cache_data
def load_data():
    return pd.read_csv("clean_data.csv")

df = load_data()

df['Insured'] = df['INSURANCE'].replace({2: 0})
df['Insurance_Gap'] = (
    (df['Included'] == 1) & (df['Insured'] == 0)
).astype(int)

included_pct = df['Included'].mean() * 100
insured_pct = df['Insured'].mean() * 100
gap_pct = df['Insurance_Gap'].mean() * 100

col1, col2, col3, col4 = st.columns(4)

col1.metric("Market Size", f"{len(df):,}")
col2.metric("Financial Inclusion", f"{included_pct:.1f}%")
col3.metric("Insurance Penetration", f"{insured_pct:.1f}%")
col4.metric("Insurance Gap", f"{gap_pct:.1f}%")

st.subheader("Market Overview")

chart_data = df[['Included','Insured','Insurance_Gap']].mean()

st.bar_chart(chart_data)

st.subheader("Key Insight")

st.info(f"""
{gap_pct:.1f}% of the population is financially active but uninsured.

👉 This represents a strong opportunity to convert existing financial users
into insurance customers.
""")
gender = st.sidebar.multiselect(
    "Select Gender",
    df['Gender'].unique()
)

if gender:
    df = df[df['c9'].isin(gender)]
