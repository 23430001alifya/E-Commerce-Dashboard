import streamlit as st
import pandas as pd
import plotly.express as px
import os

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="ArthaPlan Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>

/* ===== MAIN BACKGROUND ===== */
.stApp {
    background-color: #070B17;
    color: white;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F172A 0%, #111827 100%);
    border-right: 1px solid #1E293B;
}

[data-testid="stSidebar"] * {
    color: white;
}

/* ===== CARD ===== */
.card {
    background: linear-gradient(145deg, #111827, #0F172A);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #1F2937;
    box-shadow: 0 0 15px rgba(59,130,246,0.15);
}

/* ===== METRIC TITLE ===== */
.metric-title {
    font-size: 13px;
    color: #94A3B8;
    margin-bottom: 10px;
    letter-spacing: 1px;
}

/* ===== METRIC VALUE ===== */
.metric-value {
    font-size: 34px;
    font-weight: bold;
    color: white;
}

/* ===== METRIC SUB ===== */
.metric-sub {
    font-size: 13px;
    color: #60A5FA;
    margin-top: 6px;
}

/* ===== TITLE ===== */
.big-title {
    font-size: 38px;
    font-weight: 700;
    color: white;
}

.sub-title {
    color: #94A3B8;
    margin-bottom: 30px;
}

/* ===== CHART CARD ===== */
.chart-card {
    background: #111827;
    padding: 20px;
    border-radius: 18px;
    border: 1px solid #1F2937;
    margin-top: 15px;
}

/* ===== REMOVE STREAMLIT HEADER ===== */
header {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    paths = [
        "main_data.csv",
        "../main_data.csv",
        "dashboard/main_data.csv"
    ]

    for path in paths:
        if os.path.exists(path):
            return pd.read_csv(path)

    st.error("File main_data.csv tidak ditemukan")
    st.stop()

df = load_data()

# =========================
# CLEAN DATA
# =========================
if 'credit_limit_rupiah' in df.columns:
    df['credit_limit_rupiah'] = (
        df['credit_limit_rupiah']
        .astype(str)
        .str.replace("Rp", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", "", regex=False)
    )

    df['credit_limit_rupiah'] = pd.to_numeric(
        df['credit_limit_rupiah'],
        errors='coerce'
    )

# =========================
# FEATURE ENGINEERING
# =========================
user_limit = df.groupby('client_id')['credit_limit_rupiah'].sum().reset_index()
user_limit.columns = ['client_id', 'total_limit']

user_cards = df.groupby('client_id').size().reset_index(name='jumlah_kartu')

df = pd.merge(user_limit, user_cards, on='client_id')

# =========================
# CATEGORY
# =========================
q1 = df['total_limit'].quantile(0.33)
q2 = df['total_limit'].quantile(0.66)

def kategori(x):
    if x < q1:
        return "Hemat"
    elif x < q2:
        return "Normal"
    else:
        return "Boros"

df['kategori'] = df['total_limit'].apply(kategori)

# =========================
# OVERBUDGET
# =========================
df['overbudget'] = df['total_limit'] > df['total_limit'].mean()

# =========================
# SIDEBAR
# =========================
st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/2489/2489756.png",
    width=80
)

st.sidebar.markdown("## 💰 ArthaPlan")
st.sidebar.caption("Financial Planning Dashboard")

st.sidebar.markdown("---")

# FILTER
kategori = st.sidebar.multiselect(
    "Kategori",
    df['kategori'].unique(),
    default=df['kategori'].unique()
)

min_limit = int(df['total_limit'].min())
max_limit = int(df['total_limit'].max())

range_limit = st.sidebar.slider(
    "Range Total Limit",
    min_limit,
    max_limit,
    (min_limit, max_limit)
)

# APPLY FILTER
df = df[
    (df['kategori'].isin(kategori)) &
    (df['total_limit'] >= range_limit[0]) &
    (df['total_limit'] <= range_limit[1])
]

# =========================
# TITLE
# =========================
st.markdown("""
<div class='big-title'>
💰 Analisis Keuangan Pengguna ArthaPlan
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='sub-title'>
Monitoring perilaku finansial, overbudget risk, dan segmentasi pengguna
</div>
""", unsafe_allow_html=True)

# =========================
# KPI CARDS
# =========================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class='card'>
        <div class='metric-title'>TOTAL USER</div>
        <div class='metric-value'>{df['client_id'].nunique()}</div>
        <div class='metric-sub'>pengguna aktif</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='card'>
        <div class='metric-title'>RATA-RATA LIMIT</div>
        <div class='metric-value'>Rp {df['total_limit'].mean():,.0f}</div>
        <div class='metric-sub'>average spending</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='card'>
        <div class='metric-title'>JUMLAH KARTU</div>
        <div class='metric-value'>{df['jumlah_kartu'].mean():.1f}</div>
        <div class='metric-sub'>rata-rata user</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='card'>
        <div class='metric-title'>OVERBUDGET RISK</div>
        <div class='metric-value'>{df['overbudget'].sum()}</div>
        <div class='metric-sub'>user berisiko</div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# CHARTS
# =========================
c1, c2 = st.columns(2)

# PIE
with c1:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)

    fig1 = px.pie(
        df,
        names='kategori',
        hole=0.5
    )

    fig1.update_layout(
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font_color="white"
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# SCATTER
with c2:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)

    fig2 = px.scatter(
        df,
        x='jumlah_kartu',
        y='total_limit',
        color='kategori',
        size='total_limit'
    )

    fig2.update_layout(
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font_color="white"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# TABLE
# =========================
st.markdown("## 📋 Data Pengguna")

st.dataframe(
    df.head(20),
    use_container_width=True
)
