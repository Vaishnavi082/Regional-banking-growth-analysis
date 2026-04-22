import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Regional Banking Dashboard", layout="wide")

# ---------------------------------------------------
# 🧠 COLUMN NORMALIZATION (handles messy headers)
# ---------------------------------------------------
def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace("%", " percent", regex=False)
        .str.replace(r"[^\w]+", "_", regex=True)
        .str.strip("_")
    )

    rename_map = {
        "region": "Region",
        "year": "Year",
        "revenue": "Revenue",
        "npa_percent": "NPA %",
        "npa": "NPA %",
        "loans": "Loans",
        "deposits": "Deposits",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    return df

# ---------------------------------------------------
# 📂 ROBUST LOADER (CSV-first, Excel optional)
# ---------------------------------------------------
@st.cache_data
def load_data(file):
    if file is None:
        return None

    # 1) CSV path (no external deps)
    try:
        if hasattr(file, "name") and file.name.lower().endswith(".csv"):
            return standardize_columns(pd.read_csv(file))
    except Exception as e:
        st.error(f"❌ CSV read failed: {e}")

    # 2) Excel path (tries openpyxl if available)
    try:
        return standardize_columns(pd.read_excel(file, engine="openpyxl"))
    except Exception as e:
        st.warning("⚠ Excel read failed (missing dependency or invalid file).")
        st.info("👉 Quick fix: upload the same file as CSV, or add 'openpyxl' to requirements.")
        st.error(f"Details: {e}")
        return None

# ---------------------------------------------------
# 📂 SIDEBAR
# ---------------------------------------------------
st.sidebar.title("📂 Data Upload")
uploaded_file = st.sidebar.file_uploader("Upload CSV (recommended) or Excel", type=["csv", "xlsx"])

df = load_data(uploaded_file)

# ---------------------------------------------------
# 🛑 GUARDRAIL
# ---------------------------------------------------
if df is None:
    st.warning("⚠ No usable dataset loaded. Please upload a CSV (preferred) or a valid Excel file.")
    st.stop()

# ---------------------------------------------------
# 🔍 VALIDATION
# ---------------------------------------------------
required_cols = ["Region", "Revenue", "NPA %", "Loans", "Deposits", "Year"]
missing = [c for c in required_cols if c not in df.columns]

if missing:
    st.error(f"❌ Missing required columns: {missing}")
    st.write("📌 Detected columns:", df.columns.tolist())
    st.stop()

# ---------------------------------------------------
# ⚙️ FEATURES
# ---------------------------------------------------
df = df.copy()
df["Revenue Growth %"] = df.groupby("Region")["Revenue"].pct_change() * 100

# ---------------------------------------------------
# 🎛 FILTERS
# ---------------------------------------------------
st.sidebar.title("🎛 Filters")
regions = st.sidebar.multiselect(
    "Region",
    options=sorted(df["Region"].dropna().unique()),
    default=sorted(df["Region"].dropna().unique()),
)
years = st.sidebar.multiselect(
    "Year",
    options=sorted(df["Year"].dropna().unique()),
    default=sorted(df["Year"].dropna().unique()),
)

filtered_df = df[(df["Region"].isin(regions)) & (df["Year"].isin(years))]

# ---------------------------------------------------
# 📊 TABS
# ---------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📊 KPIs", "📈 Analysis", "📉 Visuals"])

# ---------------------------------------------------
# 📊 KPI TAB
# ---------------------------------------------------
with tab1:
    st.title("📊 KPI Dashboard")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Revenue", f"{filtered_df['Revenue'].sum():,.0f}")
    c2.metric("🏦 Loans", f"{filtered_df['Loans'].sum():,.0f}")
    c3.metric("💳 Deposits", f"{filtered_df['Deposits'].sum():,.0f}")
    c4.metric("⚠ Avg NPA %", f"{filtered_df['NPA %'].mean():.2f}")

    st.markdown("---")
    st.subheader("Top Regions by Revenue")
    st.dataframe(
        filtered_df.groupby("Region", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=False)
    )

# ---------------------------------------------------
# 📈 ANALYSIS TAB
# ---------------------------------------------------
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

# ---------------------------------------------------
# 📉 VISUALS TAB
# ---------------------------------------------------
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

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.markdown("---")
st.caption("🚀 Streamlit dashboard | CSV-first, Excel-optional")
