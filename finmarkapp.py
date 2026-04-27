import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

#np.average(df['Included'], weights=df['population_wt'])

# -----------------------
# PAGE SETUP
# -----------------------
st.set_page_config(layout="wide")
#st.image("FinMarkimages.png", width=200)
st.title("📊 Financial Inclusion Dashboard")

# -----------------------
# LOAD DATA
# -----------------------
@st.cache_data
def load_data():
    df = pd.read_csv(
        "FinScope Tanzania 2023_Individual Main Data_FINAL.csv",
        sep=";",
        encoding="latin1",
        low_memory=False,
        on_bad_lines='skip'
    )

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

    df['Financial_Stress'] = (
        (df['e_1_1'] == 1) |
        (df['e_1_1new'] == 1)
    ).astype(int)

    df['Financial_Health'] = (
        (1 - df['Financial_Stress']) +
        df['Included']
    ) / 2

    df['Health_Group'] = pd.cut(
    df['Financial_Health'],
    bins=[0, 0.4, 0.7, 1],
    labels=['Vulnerable', 'Moderate', 'Healthy']
    )
    

    return df

df = load_data()

numeric_cols = [
    'BANKED', 'MM', 'INSURANCE',
    'Included', 'Insured', 'Insurance_Gap',
    'population_wt'
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

df['population_wt'] = (
    df['population_wt']
    .astype(str)
    .str.replace(',', '')
    .str.strip()
)

df['population_wt'] = pd.to_numeric(df['population_wt'], errors='coerce')

df['population_wt'] = pd.to_numeric(
    df['population_wt'],
    errors='coerce'
)
valid = filtered_df[
    (filtered_df['population_wt'].notna()) &
    (filtered_df['population_wt'] > 0) &
    (filtered_df['Included'].notna())
]

# -----------------------
# SIDEBAR FILTERS
# -----------------------
st.sidebar.header("Filters")

if "gender" not in st.session_state:
    st.session_state["gender"] = []

if "age_group" not in st.session_state:
    st.session_state["age_group"] = []

if "health" not in st.session_state:
    st.session_state["health"] = []

gender = st.sidebar.multiselect(
    "Select Gender",
    df['Gender'].dropna().unique(),
    key="gender"
)

age_group = st.sidebar.multiselect(
    "Select Age Group",
    df['Age_Group'].dropna().unique(),
    key="age_group"
)

health = st.sidebar.multiselect(
    "Financial Health",
    df['Health_Group'].dropna().unique(),
    key="health"
)
if st.sidebar.button("Reset Filters"):
    st.session_state.clear()
    st.rerun()

# -----------------------
# APPLY FILTERS
# -----------------------
filtered_df = df.copy()

if gender:
    filtered_df = filtered_df[filtered_df['Gender'].isin(gender)]
    
if age_group:
    filtered_df = filtered_df[filtered_df['Age_Group'].isin(age_group)]

if health:
    filtered_df = filtered_df[filtered_df['Health_Group'].isin(health)]


combined = filtered_df.groupby(
    ['Age_Group','Health_Group']
)['Insurance_Gap'].mean().reset_index()

combined = combined.dropna()

top_segment = combined.sort_values(
    by='Insurance_Gap',
    ascending=False
).head(3)



# -----------------------
# KPIs
# -----------------------
included_pct = np.average(
    filtered_df['Included'],
    weights=filtered_df['population_wt']
)
insured_pct = filtered_df['Insured'].mean()
gap_pct = filtered_df['Insurance_Gap'].mean()

col1, col2, col3, col4 = st.columns(4)

total_population = filtered_df['population_wt'].sum()

col1.metric("Total Respondents", f"{int(total_population):,}")
col2.metric("Financial Inclusion", f"{included_pct*100:.1f}%")
col3.metric("Insurance Penetration", f"{insured_pct*100:.1f}%")
col4.metric("Insurance Gap", f"{gap_pct*100:.1f}%")


# -----------------------
# CHARTS (COMPACT + CLEAN)
# -----------------------
colA, colB = st.columns(2)

# 📊 Popolation Overview
chart_data = filtered_df[['Included','Insured','Insurance_Gap']].mean().reset_index()
chart_data.columns = ['Metric', 'Value']

fig1 = px.bar(
    chart_data,
    x='Metric',
    y='Value',
    text='Value',
    color_discrete_sequence=['#1f77b4'],
    title="Population Overview"
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
# FINANCIAL STRESS #
#==============================#

gap_by_health = filtered_df.groupby('Health_Group')['Insurance_Gap'].mean().reset_index()

fig_health = px.bar(
    gap_by_health,
    x='Health_Group',
    y='Insurance_Gap',
    text='Insurance_Gap',
    title="Insurance Gap by Financial Health"
)

fig_health.update_traces(
    texttemplate='%{text:.1%}',
    textposition='outside'
)

fig_health.update_layout(
    height=300,
    yaxis=dict(showgrid=False),
)

st.plotly_chart(fig_health, use_container_width=True)

top_health = gap_by_health.sort_values(
    by='Insurance_Gap',
    ascending=False
).iloc[0]

st.success(f"""
Top Opportunity Segment: {top_health['Health_Group']}

'👉' Insurance gap: {top_health['Insurance_Gap']*100:.1f}%
'👉' Prioritize this segment for tailored insurance products
""")

st.subheader("🎯 Top Target Segments")

cols = st.columns(3)

for i, (_, row) in enumerate(top_segment.iterrows()):
    with cols[i]:
        st.metric(
            label=f"{row['Age_Group']} | {row['Health_Group']}",
            value=f"{row['Insurance_Gap']*100:.1f}%",
            delta="Opportunity"
        )
if not top_segment.empty:
    gap_value = top_segment.iloc[0]['Insurance_Gap']
    
    # Ensure it's a number
    gap_value = float(gap_value)

    st.success(
        f"""👉 Insurance Gap: {gap_value*100:.1f}%

💡 This segment represents the highest opportunity for insurance expansion.

👉 Recommended Action:
- Design affordable products
- Use simple onboarding
- Leverage mobile channels
"""
    )
else:
    st.warning("No data available for selected filters.")
    
fig_combined = px.bar(
    combined,
    x='Age_Group',
    y='Insurance_Gap',
    color='Health_Group',
    text='Insurance_Gap',
    barmode='group',
    title="Insurance Gap by Age & Financial Health"
)

fig_combined.update_traces(
    texttemplate='%{text:.1%}',
    textposition='outside'
)

fig_combined.update_layout(
    height=350,
    yaxis=dict(showgrid=False, title=""),
    xaxis=dict(title="")
)

st.plotly_chart(fig_combined, use_container_width=True)
