import streamlit as st
import pandas as pd

# ======================
# CONFIG
# ======================
st.set_page_config(
    page_title="E-Commerce Dashboard",
    layout="wide"
)

# ======================
# LOAD DATA
# ======================
df = pd.read_csv("main_data.csv")
df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])

# ======================
# SIDEBAR FILTER
# ======================
st.sidebar.title("Menu Dashboard")

min_date = df["order_purchase_timestamp"].min()
max_date = df["order_purchase_timestamp"].max()

date_range = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    [min_date, max_date]
)

df = df[
    (df["order_purchase_timestamp"] >= pd.to_datetime(date_range[0])) &
    (df["order_purchase_timestamp"] <= pd.to_datetime(date_range[1]))
]

product_list = df["product_id"].unique()

selected_product = st.sidebar.multiselect(
    "Filter Produk",
    product_list
)

if selected_product:
    df = df[df["product_id"].isin(selected_product)]

# ======================
# TITLE
# ======================
st.title("WELCOME! E-Commerce Dashboard")
st.caption("Analisis sederhana penjualan & produk")

st.divider()

# ======================
# KPI SECTION (RAPI)
# ======================
col1, col2, col3, col4 = st.columns(4)

revenue = df["total_price"].sum()
orders = df["order_id"].nunique()
customers = df["customer_id"].nunique()
avg_order = revenue / orders if orders else 0

col1.metric("💰 Revenue", f"{revenue:,.0f}")
col2.metric("🧾 Orders", f"{orders:,}")
col3.metric("👤 Customers", f"{customers:,}")
col4.metric("📦 Avg Order", f"{avg_order:,.0f}")

st.divider()

# ======================
# CHART SECTION
# ======================
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Sales Trend")

    monthly = df.groupby(
        df["order_purchase_timestamp"].dt.to_period("M")
    )["total_price"].sum()

    monthly.index = monthly.index.astype(str)

    st.line_chart(monthly)

with col2:
    st.subheader("🛒 Top Produk")

    top_products = df.groupby("product_id")["total_price"] \
        .sum() \
        .sort_values(ascending=False) \
        .head(7)

    st.bar_chart(top_products)

st.divider()

# ======================
# DATA SECTION (EXPANDER BIAR RAPI)
# ======================
with st.expander("📋 Lihat Data Mentah"):
    st.dataframe(df, use_container_width=True)
