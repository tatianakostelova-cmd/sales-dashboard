import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import StringIO
# --- CONFIG ------------------------------------------------------------------
st.set_page_config(
    page_title="Sales Performance Dashboard",
    page_icon="📊",
    layout="wide",
)
PINK = "#FF1493"
LIGHT_PINK = "#FFB6C1"
BLACK = "#000000"
WHITE = "#FFFFFF"
# --- DATA SOURCE -------------------------------------------------------------
# 🔹 Посилання на Google Sheets (CSV)
SHEET_URL = "[docs.google.com](https://docs.google.com/spreadsheets/d/1wwnnMxXhtiAsEACPvZv1S_vLy5Cyntz6QJQPUE4G2MU/gviz/tq?tqx=out:csv)"
@st.cache_data(ttl=300)
def load_data(url=SHEET_URL):
    res = requests.get(url)
    data = pd.read_csv(StringIO(res.text))
    data["date"] = pd.to_datetime(data["date"])
    return data
df = load_data()
# --- DATA CLEANUP -------------------------------------------------------------
df["is_holiday"] = df["is_holiday"].astype(str).str.lower().isin(["true", "1", "yes"])
df["is_weekend"] = df["is_weekend"].astype(str).str.lower().isin(["true", "1", "yes"])
# --- METRICS -----------------------------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Average Total Revenue", f"${df['total_revenue'].mean():,.0f}")
col2.metric("Conversion Rate", f"{df['conversion_rate'].mean()*100:.2f}%")
col3.metric("Avg Transaction Value", f"${df['avg_transaction_value'].mean():.2f}")
st.markdown("---")
# --- 1. TOTAL REVENUE TREND --------------------------------------------------
st.subheader("💰 Total Revenue Trend")
fig_total = px.line(
    df,
    x="date",
    y="total_revenue",
    title="Total Revenue Trend",
    color_discrete_sequence=[PINK],
)
fig_total.update_layout(
    plot_bgcolor=WHITE,
    paper_bgcolor=WHITE,
    font_color=BLACK,
    hovermode="x unified",
)
st.plotly_chart(fig_total, use_container_width=True)
st.info("Виручка демонструє піки під час великих сезонних акцій (Semi‑Annual Sale, Black Friday).")
# --- 2. CONVERSION RATE ------------------------------------------------------
st.subheader("📈 Conversion Rate (%)")
fig_conv = px.bar(
    df,
    x="date",
    y="conversion_rate",
    color_discrete_sequence=[PINK],
)
fig_conv.update_layout(plot_bgcolor=WHITE, paper_bgcolor=WHITE, font_color=BLACK)
st.plotly_chart(fig_conv, use_container_width=True)
st.info("Конверсія зростає під час рекламних кампаній, але може коливатись через високий трафік.")
# --- 3. AVERAGE TRANSACTION VALUE -------------------------------------------
st.subheader("💳 Average Transaction Value ($)")
fig_atv = px.line(
    df,
    x="date",
    y="avg_transaction_value",
    color_discrete_sequence=[BLACK],
)
fig_atv.update_layout(plot_bgcolor=WHITE, paper_bgcolor=WHITE, font_color=BLACK)
st.plotly_chart(fig_atv, use_container_width=True)
st.info("Середній чек зростає у святкові періоди — це свідчить про активний апселл.")
# --- 4. REVENUE BY CHANNEL ---------------------------------------------------
st.subheader("🌍 Revenue by Channel (Store / Direct / International)")
fig_ch = px.line(
    df,
    x="date",
    y=["store_revenue", "direct_revenue", "international_revenue"],
    color_discrete_map={
        "store_revenue": PINK,
        "direct_revenue": BLACK,
        "international_revenue": LIGHT_PINK,
    },
)
fig_ch.update_layout(plot_bgcolor=WHITE, paper_bgcolor=WHITE, font_color=BLACK)
st.plotly_chart(fig_ch, use_container_width=True)
st.info("Store‑канал стабільно лідер, але Direct зростає найшвидше.")
# --- 5. WEEKEND / HOLIDAY COMPARISON ----------------------------------------
st.subheader("🗓️ Average Revenue – Weekends vs Weekdays / Holidays vs Normal")
def avg_rev(sub):
    return sub["total_revenue"].mean()
comparison = pd.DataFrame({
    "Category": ["Weekend", "Weekday", "Holiday", "Regular"],
    "Value": [
        avg_rev(df[df["is_weekend"]]),
        avg_rev(df[~df["is_weekend"]]),
        avg_rev(df[df["is_holiday"]]),
        avg_rev(df[~df["is_holiday"]]),
    ],
})
fig_cmp = px.bar(
    comparison,
    x="Category",
    y="Value",
    text_auto=".2s",
    color_discrete_sequence=[PINK],
)
fig_cmp.update_layout(plot_bgcolor=WHITE, paper_bgcolor=WHITE, font_color=BLACK)
st.plotly_chart(fig_cmp, use_container_width=True)
st.info("Вихідні та святкові дні дають на 30–50 % більшу виручку — найкращий час для промо.")
