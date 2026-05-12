import streamlit as st
import pandas as pd
import plotly.express as px
import os

# =========================
# CONFIG
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

/* MAIN */
.stApp {
    background-color: #F3F4F6;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background-color: #E5E7EB;
    padding-top: 20px;
}

[data-testid="stSidebar"] * {
    color: #1E293B;
}

/* TITLE */
.main-title {
    font-size: 55px;
    font-weight: bold;
    color: #1E293B;
}

.sub-title {
    color: #6B7280;
    margin-bottom: 30px;
    font-size: 18px;
}

/* KPI BOX */
.metric-box {
    background: white;
    padding: 25px;
    border-radius: 18px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transition: 0.3s;
}

.metric-box:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.12);
}

/* KPI TITLE */
.metric-title {
    font-size: 15px;
    color: #6B7280;
    margin-bottom: 10px;
}

/* KPI VALUE */
.metric-value {
    font-size: 36px;
    font-weight: bold;
    color: #111827;
}

/* CHART BOX */
.chart-box {
    background: white;
    padding: 25px;
    border-radius: 18px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    margin-top: 20px;
}

/* TABLE BOX */
.table-box {
    background: white;
    padding: 25px;
    border-radius: 18px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    margin-top: 20px;
}

/* BUTTON */
.stButton>button {
    background-color: #2563EB;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 18px;
}

.stButton>button:hover {
    background-color: #1D4ED8;
    color: white;
}

/* HIDE STREAMLIT */
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

    st.error("❌ File main_data.csv tidak ditemukan")
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
st.sidebar.markdown("# ⚙️ Smart Filter Panel")

st.sidebar.markdown("### 🏷️ Pilih Kategori")

kategori = st.sidebar.multiselect(
    "",
    df['kategori'].unique(),
    default=df['kategori'].unique()
)

st.sidebar.markdown("### 💰 Range Total Limit")

min_limit = int(df['total_limit'].min())
max_limit = int(df['total_limit'].max())

range_limit = st.sidebar.slider(
    "",
    min_limit,
    max_limit,
    (min_limit, max_limit)
)

# RESET BUTTON
if st.sidebar.button("🔄 Reset Semua Filter"):
    kategori = df['kategori'].unique()
    range_limit = (min_limit, max_limit)

# FILTER DATA
df = df[
    (df['kategori'].isin(kategori)) &
    (df['total_limit'] >= range_limit[0]) &
    (df['total_limit'] <= range_limit[1])
]

# =========================
# HEADER
# =========================
st.markdown("""
<div class='main-title'>
💰 ArthaPlan Dashboard
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='sub-title'>
Analisis perilaku finansial pengguna dan overbudget risk
</div>
""", unsafe_allow_html=True)

# =========================
# RINGKASAN
# =========================
st.subheader("📊 Ringkasan")

col1, col2, col3 = st.columns(3)

# TOTAL USER
with col1:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">Total User</div>
        <div class="metric-value">
            {df['client_id'].nunique()}
        </div>
    </div>
    """, unsafe_allow_html=True)

# TOTAL LIMIT
with col2:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">Total Limit</div>
        <div class="metric-value">
            Rp {df['total_limit'].sum():,.0f}
        </div>
    </div>
    """, unsafe_allow_html=True)

# AVG LIMIT
with col3:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">Rata-rata Limit</div>
        <div class="metric-value">
            Rp {df['total_limit'].mean():,.0f}
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# PIE CHART
# =========================
st.markdown("<div class='chart-box'>", unsafe_allow_html=True)

st.subheader("📊 Segmentasi Pengguna")

fig1 = px.pie(
    df,
    names='kategori',
    hole=0.5
)

fig1.update_layout(
    paper_bgcolor='white',
    plot_bgcolor='white',
    font_color='black'
)

st.plotly_chart(fig1, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# =========================
# SCATTER CHART
# =========================
st.markdown("<div class='chart-box'>", unsafe_allow_html=True)

st.subheader("📈 Total Limit vs Jumlah Kartu")

fig2 = px.scatter(
    df,
    x='jumlah_kartu',
    y='total_limit',
    color='kategori',
    size='total_limit',
    hover_data=['client_id']
)

fig2.update_layout(
    paper_bgcolor='white',
    plot_bgcolor='white',
    font_color='black'
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# =========================
# HISTOGRAM
# =========================
st.markdown("<div class='chart-box'>", unsafe_allow_html=True)

st.subheader("📉 Distribusi Total Limit")

fig3 = px.histogram(
    df,
    x='total_limit',
    nbins=40
)

fig3.update_layout(
    paper_bgcolor='white',
    plot_bgcolor='white',
    font_color='black'
)

st.plotly_chart(fig3, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# =========================
# TABLE
# =========================
st.markdown("<div class='table-box'>", unsafe_allow_html=True)

st.subheader("📋 Data Pengguna")

st.dataframe(
    df.head(20),
    use_container_width=True
)

st.markdown("</div>", unsafe_allow_html=True)
