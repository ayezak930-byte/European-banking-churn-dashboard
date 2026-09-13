# STEP 10.5 — European Banking Churn Analytics Dashboard

import streamlit as st
import pandas as pd
import plotly.express as px


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="European Banking Churn Analytics",
    page_icon="🏦",
    layout="wide"
)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    return pd.read_csv("European_Bank_Segmented.csv")


df = load_data()


# --------------------------------------------------
# CUSTOMER SEGMENT NAMES
# --------------------------------------------------

segment_names = {
    0: "Active High-Balance Customers",
    1: "Inactive Low-Balance Customers",
    2: "Senior At-Risk Customers",
    3: "Inactive High-Balance Customers",
    4: "Active Low-Balance Loyal Customers",
    5: "Multi-Product At-Risk Customers"
}


df["Segment_Name"] = df["Cluster"].map(segment_names)


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🏦 European Banking Customer Churn Analytics")

st.markdown(
    "### Customer Segmentation & Churn Pattern Analytics"
)

st.markdown(
    "Interactive dashboard for analysing customer churn, "
    "customer segments and retention priorities."
)


# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("🔎 Dashboard Filters")

geography_filter = st.sidebar.multiselect(
    "Geography",
    options=sorted(df["Geography"].dropna().unique()),
    default=sorted(df["Geography"].dropna().unique())
)

gender_filter = st.sidebar.multiselect(
    "Gender",
    options=sorted(df["Gender"].dropna().unique()),
    default=sorted(df["Gender"].dropna().unique())
)

segment_filter = st.sidebar.multiselect(
    "Customer Segment",
    options=sorted(df["Segment_Name"].dropna().unique()),
    default=sorted(df["Segment_Name"].dropna().unique())
)


# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

filtered_df = df[
    (df["Geography"].isin(geography_filter)) &
    (df["Gender"].isin(gender_filter)) &
    (df["Segment_Name"].isin(segment_filter))
].copy()


# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------

total_customers = len(filtered_df)

total_churned = int(filtered_df["Exited"].sum())

if total_customers > 0:
    churn_rate = filtered_df["Exited"].mean() * 100
else:
    churn_rate = 0


# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Customers",
    f"{total_customers:,}"
)

col2.metric(
    "Churned Customers",
    f"{total_churned:,}"
)

col3.metric(
    "Churn Rate",
    f"{churn_rate:.2f}%"
)

col4.metric(
    "Customer Segments",
    filtered_df["Cluster"].nunique()
)


st.divider()


# --------------------------------------------------
# GEOGRAPHY ANALYSIS
# --------------------------------------------------

st.subheader("🌍 Churn Rate by Geography")

geo_churn = (
    filtered_df.groupby("Geography")["Exited"]
    .mean()
    .mul(100)
    .reset_index()
)

geo_churn.columns = ["Geography", "Churn_Rate"]

fig_geo = px.bar(
    geo_churn,
    x="Geography",
    y="Churn_Rate",
    title="Churn Rate by Geography",
    labels={
        "Churn_Rate": "Churn Rate (%)",
        "Geography": "Geography"
    }
)

st.plotly_chart(
    fig_geo,
    use_container_width=True
)


# --------------------------------------------------
# CUSTOMER SEGMENT ANALYSIS
# --------------------------------------------------

st.subheader("👥 Churn Rate by Customer Segment")

segment_churn = (
    filtered_df.groupby("Segment_Name")["Exited"]
    .mean()
    .mul(100)
    .reset_index()
)

segment_churn.columns = [
    "Segment_Name",
    "Churn_Rate"
]

segment_churn = segment_churn.sort_values(
    "Churn_Rate",
    ascending=False
)

fig_segment = px.bar(
    segment_churn,
    x="Churn_Rate",
    y="Segment_Name",
    orientation="h",
    title="Churn Rate by Customer Segment",
    labels={
        "Churn_Rate": "Churn Rate (%)",
        "Segment_Name": "Customer Segment"
    }
)

st.plotly_chart(
    fig_segment,
    use_container_width=True
)


# --------------------------------------------------
# AGE GROUP ANALYSIS
# --------------------------------------------------

st.subheader("📊 Churn Rate by Age Group")

age_bins = [17, 25, 35, 45, 55, 65, 100]

age_labels = [
    "18–25",
    "26–35",
    "36–45",
    "46–55",
    "56–65",
    "66+"
]

filtered_df["AgeGroup"] = pd.cut(
    filtered_df["Age"],
    bins=age_bins,
    labels=age_labels
)

age_churn = (
    filtered_df.groupby(
        "AgeGroup",
        observed=False
    )["Exited"]
    .mean()
    .mul(100)
    .reset_index()
)

age_churn.columns = [
    "Age_Group",
    "Churn_Rate"
]

fig_age = px.bar(
    age_churn,
    x="Age_Group",
    y="Churn_Rate",
    title="Churn Rate by Age Group",
    labels={
        "Churn_Rate": "Churn Rate (%)",
        "Age_Group": "Age Group"
    }
)

st.plotly_chart(
    fig_age,
    use_container_width=True
)


# --------------------------------------------------
# SEGMENT PROFILE TABLE
# --------------------------------------------------

st.subheader("📋 Customer Segment Profile")

profile = (
    filtered_df.groupby("Segment_Name")
    .agg(
        Customer_Count=("CustomerId", "count"),
        Average_Age=("Age", "mean"),
        Average_Balance=("Balance", "mean"),
        Average_Products=("NumOfProducts", "mean"),
        Churn_Rate=("Exited", "mean")
    )
    .reset_index()
)

profile["Average_Age"] = profile["Average_Age"].round(2)

profile["Average_Balance"] = (
    profile["Average_Balance"].round(2)
)

profile["Average_Products"] = (
    profile["Average_Products"].round(2)
)

profile["Churn_Rate"] = (
    profile["Churn_Rate"] * 100
).round(2)

st.dataframe(
    profile,
    use_container_width=True
)


# --------------------------------------------------
# RETENTION PRIORITY
# --------------------------------------------------

st.subheader("🎯 Retention Priority")

priority = (
    filtered_df.groupby("Segment_Name")
    .agg(
        Customers=("CustomerId", "count"),
        Churned_Customers=("Exited", "sum"),
        Churn_Rate=("Exited", "mean")
    )
    .reset_index()
)

priority["Churn_Rate"] = (
    priority["Churn_Rate"] * 100
).round(2)

priority = priority.sort_values(
    "Churn_Rate",
    ascending=False
)

st.dataframe(
    priority,
    use_container_width=True
)


# --------------------------------------------------
# DATA PREVIEW
# --------------------------------------------------

with st.expander("View Customer Data"):

    st.dataframe(
        filtered_df,
        use_container_width=True
    )
