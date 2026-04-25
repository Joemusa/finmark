import streamlit as st
import pandas as pd
import plotly.express as px

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

    # Clean column names
    df.columns = df.columns.str.strip()

    # Convert Yes/No (1/2 → 1/0)
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

    # Decode Gender
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
# KPIs
# -----------------------
included_pct = filtered_df['Included'].mean()
insured_pct = filtered_df['Insured'].mean()
gap_pct = filtered_df['Insurance_Gap'].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Market Size", f"{len(filtered_df):,}")
col2.metric("Financial Inclusion", f"{included_pct*100:.1f}%")
col3.metric("Insurance Penetration", f"{insured_pct*100:.1f}%")
col4.metric("Insurance Gap", f"{gap_pct*100:.1f}%")

# -----------------------
# CHARTS (COMPACT + CLEAN)
# -----------------------
colA, colB = st.columns(2)

# 📊 Market Overview
chart_data = filtered_df[['Included','Insured','Insurance_Gap']].mean().reset_index()
chart_data.columns = ['Metric', 'Value']

fig1 = px.bar(
    chart_data,
    x='Metric',
    y='Value',
    text='Value',
    color_discrete_sequence=['#1f77b4'],
    title="Market Overview"
)

fig1.update_traces(
    texttemplate='%{text:.1%}',
    textposition='outside'
)

fig1.update_layout(
    height=300,
    margin=dict(l=20, r=20, t=40, b=20),
    yaxis=dict(showgrid=False, title=""),
    xaxis=dict(title="")
)

# 📊 Insurance Gap by Gender
gap_by_gender = filtered_df.groupby('Gender')['Insurance_Gap'].mean().reset_index()

fig2 = px.bar(
    gap_by_gender,
    x='Gender',
    y='Insurance_Gap',
    text='Insurance_Gap',
    color_discrete_sequence=['#ff7f0e'],
    title="Insurance Gap by Gender"
)

fig2.update_traces(
    texttemplate='%{text:.1%}',
    textposition='outside'
)

fig2.update_layout(
    height=300,
    margin=dict(l=20, r=20, t=40, b=20),
    yaxis=dict(showgrid=False, title=""),
    xaxis=dict(title="")
)

with colA:
    st.plotly_chart(fig1, use_container_width=True)

with colB:
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------
# INSIGHT BOX
# -----------------------
st.subheader("Key Insight")

st.info(f"""
{gap_pct*100:.1f}% of financially active individuals are uninsured.

👉 This represents a strong opportunity to convert existing financial users
into insurance customers.

👉 Focus on segments where financial inclusion is high but insurance uptake is low.
""")
