import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Regional Banking Dashboard", layout="wide")

# ----------------------------------
# LOAD DATA (ROBUST)
# ----------------------------------
st.sidebar.title("📂 Data Upload")

uploaded_file = st.sidebar.file_uploader(
    "Upload dataset (CSV or Excel)", 
    type=["csv", "xlsx"]
)

@st.cache_data
def load_data(file):
    try:
        if isinstance(file, str):
            # default file
            if file.endswith(".csv"):
                return pd.read_csv(file)
            else:
                return pd.read_excel(file)
        else:
            # uploaded file
            if file.name.endswith(".csv"):
                return pd.read_csv(file)
            else:
                return pd.read_excel(file)
    except Exception as e:
        return None

# Load dataset
df = None

if uploaded_file is not None:
    df = load_data(uploaded_file)
else:
    df = load_data("regional_banking_dataset.xlsx")

# If still no data → stop safely
if df is None:
    st.error("❌ No dataset available. Please upload a valid file.")
    st.stop()

# ----------------------------------
# BASIC VALIDATION
# ----------------------------------
required_cols = ["Region", "Revenue", "NPA %", "Loans", "Deposits", "Year"]

missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    st.error(f"❌ Missing columns: {missing_cols}")
    st.stop()

# ----------------------------------
# FEATURE ENGINEERING
# ----------------------------------
df = df.copy()
df["Revenue Growth %"] = df.groupby("Region")["Revenue"].pct_change() * 100

# ----------------------------------
# SIDEBAR FILTERS
# ----------------------------------
st.sidebar.title("🎛 Filters")

regions = st.sidebar.multiselect(
    "Select Region",
    options=df["Region"].dropna().unique(),
    default=df["Region"].dropna().unique()
)

years = st.sidebar.multiselect(
    "Select Year",
    options=sorted(df["Year"].dropna().unique()),
    default=sorted(df["Year"].dropna().unique())
)

filtered_df = df[
    (df["Region"].isin(regions)) &
    (df["Year"].isin(years))
]

# ----------------------------------
# TABS
# ----------------------------------
tab1, tab2, tab3 = st.tabs([
    "📊 KPI Dashboard", 
    "📈 Analysis", 
    "📉 Visualizations"
])

# ----------------------------------
# KPI TAB
# ----------------------------------
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

    st.markdown("---")

    st.subheader("📌 Revenue by Region (Top Performers)")
    st.dataframe(
        filtered_df.groupby("Region")["Revenue"]
        .sum()
        .sort_values(ascending=False)
    )

# ----------------------------------
# ANALYSIS TAB
# ----------------------------------
with tab2:
    st.title("📈 Data Analysis")

    st.subheader("Dataset Preview")
    st.dataframe(filtered_df)

    st.subheader("Summary Statistics")
    st.write(filtered_df.describe())

    st.subheader("Missing Values")
    st.write(filtered_df.isnull().sum())

    st.subheader("Revenue by Region")
    st.write(filtered_df.groupby("Region")["Revenue"].sum())

    st.subheader("Average NPA % by Region")
    st.write(filtered_df.groupby("Region")["NPA %"].mean())

    st.subheader("Loans vs Deposits (Total)")
    st.write(filtered_df[["Loans", "Deposits"]].sum())

# ----------------------------------
# VISUALIZATION TAB
# ----------------------------------
with tab3:
    st.title("📉 Visual Insights")

    # Revenue Bar
    st.subheader("Revenue by Region")
    fig1, ax1 = plt.subplots()
    sns.barplot(x="Region", y="Revenue", data=filtered_df, ax=ax1)
    st.pyplot(fig1)

    # NPA Bar
    st.subheader("NPA % by Region")
    fig2, ax2 = plt.subplots()
    sns.barplot(x="Region", y="NPA %", data=filtered_df, ax=ax2)
    st.pyplot(fig2)

    # Loans vs Deposits
    st.subheader("Loans vs Deposits")
    fig3, ax3 = plt.subplots()
    filtered_df[["Loans", "Deposits"]].sum().plot(kind="bar", ax=ax3)
    st.pyplot(fig3)

    # Revenue Trend
    st.subheader("Revenue Trend Over Time")
    fig4, ax4 = plt.subplots()
    sns.lineplot(
        x="Year", 
        y="Revenue", 
        hue="Region", 
        data=filtered_df, 
        ax=ax4
    )
    st.pyplot(fig4)

# ----------------------------------
# FOOTER
# ----------------------------------
st.markdown("---")
st.caption("🚀 Regional Banking Dashboard | Streamlit App")
