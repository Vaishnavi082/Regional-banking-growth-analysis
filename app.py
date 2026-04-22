import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Regional Banking Dashboard", layout="wide")

# -------------------------------
# DATA LOADING
# -------------------------------
st.sidebar.title("📂 Data Upload")

uploaded_file = st.sidebar.file_uploader("Upload your dataset", type=["xlsx"])

@st.cache_data
def load_data(file):
    return pd.read_excel(file)

if uploaded_file is not None:
    df = load_data(uploaded_file)
else:
    df = load_data("regional_banking_dataset.xlsx")

# -------------------------------
# DATA PREPROCESSING
# -------------------------------
df["Revenue Growth %"] = df.groupby("Region")["Revenue"].pct_change() * 100

# -------------------------------
# SIDEBAR FILTERS
# -------------------------------
st.sidebar.title("🎛 Filters")

regions = st.sidebar.multiselect(
    "Select Region",
    options=df["Region"].unique(),
    default=df["Region"].unique()
)

years = st.sidebar.multiselect(
    "Select Year",
    options=df["Year"].unique(),
    default=df["Year"].unique()
)

filtered_df = df[(df["Region"].isin(regions)) & (df["Year"].isin(years))]

# -------------------------------
# TABS
# -------------------------------
tab1, tab2, tab3 = st.tabs(["📊 KPIs", "📈 Analysis", "📉 Visualizations"])

# -------------------------------
# KPI TAB
# -------------------------------
with tab1:
    st.title("📊 Key Performance Indicators")

    total_revenue = filtered_df["Revenue"].sum()
    total_loans = filtered_df["Loans"].sum()
    total_deposits = filtered_df["Deposits"].sum()
    avg_npa = filtered_df["NPA %"].mean()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Total Revenue", f"{total_revenue:,.0f}")
    col2.metric("🏦 Total Loans", f"{total_loans:,.0f}")
    col3.metric("💳 Total Deposits", f"{total_deposits:,.0f}")
    col4.metric("⚠ Avg NPA %", f"{avg_npa:.2f}%")

# -------------------------------
# ANALYSIS TAB
# -------------------------------
with tab2:
    st.title("📈 Data Analysis")

    st.subheader("Dataset Overview")
    st.dataframe(filtered_df)

    st.subheader("Summary Statistics")
    st.write(filtered_df.describe())

    st.subheader("Missing Values")
    st.write(filtered_df.isnull().sum())

    st.subheader("Revenue by Region")
    st.write(filtered_df.groupby("Region")["Revenue"].sum())

    st.subheader("Average NPA by Region")
    st.write(filtered_df.groupby("Region")["NPA %"].mean())

# -------------------------------
# VISUALIZATION TAB
# -------------------------------
with tab3:
    st.title("📉 Visual Insights")

    st.subheader("Revenue by Region")
    fig1, ax1 = plt.subplots()
    sns.barplot(x="Region", y="Revenue", data=filtered_df, ax=ax1)
    st.pyplot(fig1)

    st.subheader("NPA % by Region")
    fig2, ax2 = plt.subplots()
    sns.barplot(x="Region", y="NPA %", data=filtered_df, ax=ax2)
    st.pyplot(fig2)

    st.subheader("Loans vs Deposits")
    fig3, ax3 = plt.subplots()
    filtered_df[["Loans", "Deposits"]].sum().plot(kind="bar", ax=ax3)
    st.pyplot(fig3)

    st.subheader("Revenue Trend")
    fig4, ax4 = plt.subplots()
    sns.lineplot(x="Year", y="Revenue", hue="Region", data=filtered_df, ax=ax4)
    st.pyplot(fig4)

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.caption("🚀 Regional Banking Dashboard | Built with Streamlit")