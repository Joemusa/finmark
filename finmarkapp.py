import streamlit as st
import pandas as pd

# -----------------------
# PAGE SETUP
# -----------------------
st.set_page_config(layout="wide")
st.title("📊 Financial Inclusion Dashboard")

# -----------------------
# LOAD DATA
# -----------------------
@st.cache_data
def load_data():
    df = pd.read_csv("clean_data.csv")

    # -------- CLEAN / TRANSFORM --------
    
    # Convert Yes/No style columns
    df['BANKED'] = df['BANKED'].replace({2: 0})
    df['MM'] = df['MM'].replace({2: 0})
    df['INSURANCE'] = df['INSURANCE'].replace({2: 0})

    # Financial Inclusion
    df['Included'] = (
        (df['BANKED'] == 1) |
        (df['MM'] == 1)
    ).astype(int)

    # Insurance
    df['Insured'] = df['INSURANCE']

    # Insurance Gap
    df['Insurance_Gap'] = (
        (df['Included'] == 1) & (df['Insured'] == 0)
    ).astype(int)

    # Decode Gender (for better display)
    df['Gender'] = df['c9'].map({
        1: 'Male',
        2: 'Female'
    })

    return df

df = load_data()

# -----------------------
# SIDEBAR FILTERS
# -----------------------
st.sidebar.header("Filters")

gender = st.sidebar.multiselect(
    "Select Gender",
    df['Gender'].dropna().unique()
)

# -----------------------
# APPLY FILTERS
# -----------------------
filtered_df = df.copy()

if gender:
    filtered_df = filtered_df[filtered_df['Gender'].isin(gender)]

# -----------------------
# KPIs (USE filtered_df)
# -----------------------
included_pct = filtered_df['Included'].mean() * 100
insured_pct = filtered_df['Insured'].mean() * 100
gap_pct = filtered_df['Insurance_Gap'].mean() * 100

col1, col2, col3, col4 = st.columns(4)

col1.metric("Market Size", f"{len(filtered_df):,}")
col2.metric("Financial Inclusion", f"{included_pct:.1f}%")
col3.metric("Insurance Penetration", f"{insured_pct:.1f}%")
col4.metric("Insurance Gap", f"{gap_pct:.1f}%")

# -----------------------
# CHART
# -----------------------
st.subheader("Market Overview")

chart_data = filtered_df[['Included','Insured','Insurance_Gap']].mean()

st.bar_chart(chart_data)

# -----------------------
# SEGMENT ANALYSIS
# -----------------------
st.subheader("Insurance Gap by Gender")

gap_by_gender = filtered_df.groupby('Gender')['Insurance_Gap'].mean()

st.bar_chart(gap_by_gender)

# -----------------------
# INSIGHT
# -----------------------
st.subheader("Key Insight")

st.info(f"""
{gap_pct:.1f}% of financially active individuals are uninsured.

👉 This represents a strong opportunity to target existing financial users
with insurance products.
""")
