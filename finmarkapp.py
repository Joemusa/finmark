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

    df['Age_Group'] = pd.cut(
    df['c8c'],
    bins=[0, 25, 35, 50, 65, 100],
    labels=['18-25','26-35','36-50','51-65','65+']
    )

    df['Income'] = pd.to_numeric(df['D3_1'], errors='coerce')

    df['Income'] = df['Income'].replace({0: None})

    df['Income_Group'] = pd.cut(
        df['Income'],
        bins=[0, 5000, 15000, 30000, 60000, 200000],
        labels=[
            'Low Income',
            'Lower-Middle',
            'Middle',
            'Upper-Middle',
            'High Income'
        ]
    )

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

age_group = st.sidebar.multiselect(
    "Select Age Group",
    df['Age_Group'].dropna().unique()
)

income_group = st.sidebar.multiselect(
    "Select Income Group",
    df['Income_Group'].dropna().unique()
)

# -----------------------
# APPLY FILTERS
# -----------------------
filtered_df = df.copy()

if gender:
    filtered_df = filtered_df[filtered_df['Gender'].isin(gender)]
    
if age_group:
    filtered_df = filtered_df[filtered_df['Age_Group'].isin(age_group)]

if income_group:
    filtered_df = filtered_df[
        filtered_df['Income_Group'].isin(income_group)
    ]

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

#===========================#
# Age #
#===========================#
df['Age_Group'] = pd.cut(
    df['c8c'],
    bins=[0, 25, 35, 50, 65, 100],
    labels=['18-25','26-35','36-50','51-65','65+']
)


gap_by_age = filtered_df.groupby('Age_Group')['Insurance_Gap'].mean().reset_index()

fig_age = px.bar(
    gap_by_age,
    x='Age_Group',
    y='Insurance_Gap',
    text='Insurance_Gap',
    color_discrete_sequence=['#2ca02c'],
    title="Insurance Gap by Age Group"
)

fig_age.update_traces(
    texttemplate='%{text:.1%}',
    textposition='outside'
)

fig_age.update_layout(
    height=300,
    yaxis=dict(showgrid=False, title=""),
    xaxis=dict(title="")
)

st.plotly_chart(fig_age, use_container_width=True)

top_age = gap_by_age.sort_values(by='Insurance_Gap', ascending=False).iloc[0]

st.success(f"""
Top Opportunity Age Group: {top_age['Age_Group']}

👉 Insurance gap: {top_age['Insurance_Gap']*100:.1f}%

👉 This group is financially active but underserved
""")

#==============================#
# INCOME#
#==============================#

df['Income'] = pd.to_numeric(df['D3_1'], errors='coerce')

df['Income'] = df['Income'].replace({0: None})

df['Income_Group'] = pd.cut(
    df['Income'],
    bins=[0, 5000, 15000, 30000, 60000, 200000],
    labels=[
        'Low Income',
        'Lower-Middle',
        'Middle',
        'Upper-Middle',
        'High Income'
    ]
)
gap_by_income = filtered_df.groupby('Income_Group')['Insurance_Gap'].mean().reset_index()

# Sort properly
gap_by_income['Income_Group'] = pd.Categorical(
    gap_by_income['Income_Group'],
    categories=[
        'Low Income',
        'Lower-Middle',
        'Middle',
        'Upper-Middle',
        'High Income'
    ],
    ordered=True
)

gap_by_income = gap_by_income.sort_values('Income_Group')

fig_income = px.bar(
    gap_by_income,
    x='Income_Group',
    y='Insurance_Gap',
    text='Insurance_Gap',
    color_discrete_sequence=['#9467bd'],
    title="Insurance Gap by Income Group"
)

fig_income.update_traces(
    texttemplate='%{text:.1%}',
    textposition='outside'
)

fig_income.update_layout(
    height=300,
    yaxis=dict(showgrid=False, title=""),
    xaxis=dict(title="")
)

st.plotly_chart(fig_income, use_container_width=True)

top_income = gap_by_income.sort_values(
    by='Insurance_Gap',
    ascending=False
).iloc[0]

st.success(f"""
Top Opportunity Income Segment: {top_income['Income_Group']}

👉 Insurance gap: {top_income['Insurance_Gap']*100:.1f}%
👉 Strong opportunity for targeted insurance products
""")
