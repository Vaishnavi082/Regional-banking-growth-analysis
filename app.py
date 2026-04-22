import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Regional Banking Dashboard", layout="wide")

# ---------------------------------------------------
# 🧠 SMART COLUMN STANDARDIZATION
# ---------------------------------------------------
def standardize_columns(df):
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace("%", " percent", regex=False)
        .str.replace(" ", "_")
    )

    rename_map = {
        "region": "Region",
        "year": "Year",
        "revenue": "Revenue",
        "npa_percent": "NPA %",
        "npa": "NPA %",
        "loans": "Loans",
        "deposits": "Deposits"
    }

    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    return df

# ---------------------------------------------------
# 📂 DATA LOADER (ROBUST)
# ---------------------------------------------------
@st.cache_data
def load_data(file):
    try:
        if file is None:
            return None

        if hasattr(file, "name"):
            # uploaded file
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file, engine="openpyxl")
        else:
            # default file
            if file.endswith(".csv"):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file, engine="openpyxl")

        df = standardize_columns(df)
        return df

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        return None

# ---------------------------------------------------
# 📂 SIDEBAR
# ---------------------------------------------------
st.sidebar.title("📂 Data Upload")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV or Excel file",
    type=["csv", "xlsx"]
)

# Try loading
df = load_data(uploaded_file)

# ---------------------------------------------------
# 🛑 IF NO DATA → STOP CLEANLY
# ---------------------------------------------------
if df is None:
    st.warning("⚠ Please upload a valid dataset to continue.")
    st.stop()

# ---------------------------------------------------
# 🔍 VALIDATION
# ---------------------------------------------------
required_cols = ["Region", "Revenue", "NPA %", "Loans", "Deposits", "Year"]

missing = [col for col in required_cols if col not in df.columns]

if missing:
    st.error(f"❌ Missing required columns: {missing}")
    st.write("📌 Found columns:", df.columns.tolist())
    st.stop()

# ---------------------------------------------------
# ⚙️ FEATURE ENGINEERING
# ---------------------------------------------------
df["Revenue Growth %"] = df.groupby("Region")["Revenue"].pct_change() * 100

# ---------------------------------------------------
# 🎛 FILTERS
# ---------------------------------------------------
st.sidebar.title("🎛 Filters")

regions = st.sidebar.multiselect(
    "Select Region",
    df["Region"].dropna().unique(),
    default=df["Region"].dropna().unique()
)

years = st.sidebar.multiselect(
    "Select Year",
    sorted(df["Year"].dropna().unique()),
    default=sorted(df["Year"].dropna().unique())
)

filtered_df = df[
    (df["Region"].isin(regions)) &
    (df["Year"].isin(years))
]

# ---------------------------------------------------
# 📊 TABS
# ---------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📊 KPIs", "📈 Analysis", "📉 Visuals"])

# ---------------------------------------------------
# 📊 KPI TAB
# ---------------------------------------------------
with tab1:
    st.title("📊 KPI Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Revenue", f"{filtered_df['Revenue'].sum():,.0f}")
    col2.metric("🏦 Loans", f"{filtered_df['Loans'].sum():,.0f}")
    col3.metric("💳 Deposits", f"{filtered_df['Deposits'].sum():,.0f}")
    col4.metric("⚠ Avg NPA %", f"{filtered_df['NPA %'].mean():.2f}")

    st.markdown("---")

    st.subheader("Top Regions by Revenue")
    st.dataframe(
        filtered_df.groupby("Region")["Revenue"]
        .sum()
        .sort_values(ascending=False)
    )

# ---------------------------------------------------
# 📈 ANALYSIS TAB
# ---------------------------------------------------
with tab2:
    st.title("📈 Data Analysis")

    st.subheader("Dataset")
    st.dataframe(filtered_df)

    st.subheader("Statistics")
    st.write(filtered_df.describe())

    st.subheader("Missing Values")
    st.write(filtered_df.isnull().sum())

# ---------------------------------------------------
# 📉 VISUAL TAB
# ---------------------------------------------------
with tab3:
    st.title("📉 Visual Insights")

    # Revenue
    st.subheader("Revenue by Region")
    fig1, ax1 = plt.subplots()
    sns.barplot(x="Region", y="Revenue", data=filtered_df, ax=ax1)
    st.pyplot(fig1)

    # NPA
    st.subheader("NPA % by Region")
    fig2, ax2 = plt.subplots()
    sns.barplot(x="Region", y="NPA %", data=filtered_df, ax=ax2)
    st.pyplot(fig2)

    # Loans vs Deposits
    st.subheader("Loans vs Deposits")
    fig3, ax3 = plt.subplots()
    filtered_df[["Loans", "Deposits"]].sum().plot(kind="bar", ax=ax3)
    st.pyplot(fig3)

    # Trend
    st.subheader("Revenue Trend")
    fig4, ax4 = plt.subplots()
    sns.lineplot(
        x="Year",
        y="Revenue",
        hue="Region",
        data=filtered_df,
        ax=ax4
    )
    st.pyplot(fig4)

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.markdown("---")
st.caption("🚀 Built for smooth deployment | Streamlit Dashboard")
