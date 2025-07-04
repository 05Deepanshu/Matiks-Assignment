import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
import calendar
import matplotlib.pyplot as plt

st.set_page_config(page_title="Matiks Dashboard", layout="wide")
st.markdown(
    """
    <style>
        .main { background-color: #0e1117; color: white; }
        .block-container { padding-top: 2rem; }
        .css-1v0mbdj { background: linear-gradient(90deg,#6441a5,#2a0845) !important; border-radius: 12px; }
        .metric-label { font-weight: 600; color: #f9fafb; font-size: 16px; }
        .st-bf { background-color: #1f2937 !important; }
        .st-eb { border: none !important; }
    </style>
    """,
    unsafe_allow_html=True
)


@st.cache_data
def load_data():
    df = pd.read_csv("data/user_data.csv")
    df['Signup_Date'] = pd.to_datetime(df['Signup_Date'], format="%d-%b-%Y")
    df['Last_Login'] = pd.to_datetime(df['Last_Login'], format="%d-%b-%Y")
    df['Revenue_Category'] = pd.cut(df['Total_Revenue_USD'],
                                    bins=[-1, 50, 200, 500, float('inf')],
                                    labels=['Low', 'Medium', 'High', 'Whale'])
    df['Churn_Risk'] = (datetime.now() - df['Last_Login']).dt.days
    df['Churn_Risk'] = pd.cut(df['Churn_Risk'], bins=[-1, 7, 30, 60, float('inf')],
                              labels=['Active (7 days)', 'Medium (8-30 days)', 'Low (31-60 days)', 'High Risk (60+ days)'])
    return df


df = load_data()

st.sidebar.header("📊 Dashboard Filters")
with st.sidebar:
    date_range = st.date_input("Select Signup Date Range", [
                               df['Signup_Date'].min(), df['Signup_Date'].max()])
    countries = st.multiselect(
        "Select Countries", sorted(df['Country'].dropna().unique()))
    devices = st.multiselect("Select Device Types", sorted(
        df['Device_Type'].dropna().unique()))
    games = st.multiselect("Select Games", sorted(
        df['Game_Title'].dropna().unique()))
    revenue_range = st.slider("Select Revenue Range", 0, int(
        df['Total_Revenue_USD'].max()), (0, int(df['Total_Revenue_USD'].max())))

filtered_df = df[
    (df['Signup_Date'] >= pd.to_datetime(date_range[0])) &
    (df['Signup_Date'] <= pd.to_datetime(date_range[1]))
]

if countries:
    filtered_df = filtered_df[filtered_df['Country'].isin(countries)]
if devices:
    filtered_df = filtered_df[filtered_df['Device_Type'].isin(devices)]
if games:
    filtered_df = filtered_df[filtered_df['Game_Title'].isin(games)]
filtered_df = filtered_df[(filtered_df['Total_Revenue_USD'] >= revenue_range[0]) & (
    filtered_df['Total_Revenue_USD'] <= revenue_range[1])]

# TABS
overview, revenue, behavior, segmentation, raw = st.tabs(
    ["📈 Overview", "💰 Revenue", "👥 User Behavior", "🔍 Segmentation", "📂 Raw Data"])

with overview:
    st.subheader("📌 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Users", len(filtered_df))
    col2.metric("Total Revenue",
                f"${filtered_df['Total_Revenue_USD'].sum():,.2f}")
    col3.metric("Avg Session Duration",
                f"{filtered_df['Avg_Session_Duration_Min'].mean():.1f} min")
    col4.metric("Avg Revenue/User",
                f"${(filtered_df['Total_Revenue_USD'].sum() / len(filtered_df)):.2f}")

with revenue:
    st.subheader("📊 Revenue by Device & Game")
    dev_rev = filtered_df.groupby('Device_Type')[
        'Total_Revenue_USD'].sum().reset_index()
    game_rev = filtered_df.groupby('Game_Title')[
        'Total_Revenue_USD'].sum().reset_index()
    col1, col2 = st.columns(2)
    col1.plotly_chart(px.bar(dev_rev, x='Device_Type', y='Total_Revenue_USD',
                      title="Revenue by Device", color='Device_Type'))
    col2.plotly_chart(px.bar(game_rev, x='Game_Title', y='Total_Revenue_USD',
                      title="Revenue by Game", color='Game_Title'))

with behavior:
    st.subheader("🧭 Engagement Heatmap")
    heat_df = filtered_df.groupby(['Game_Title', 'Device_Type'])[
        'Avg_Session_Duration_Min'].mean().reset_index()
    heat_pivot = heat_df.pivot(
        index='Game_Title', columns='Device_Type', values='Avg_Session_Duration_Min')
    st.dataframe(heat_pivot.style.background_gradient(cmap='Blues'))

with segmentation:
    st.subheader("🧬 User Segmentation")
    seg_count = filtered_df['Revenue_Category'].value_counts().reset_index()
    seg_count.columns = ['Segment', 'Users']
    churn = filtered_df['Churn_Risk'].value_counts().reset_index()
    churn.columns = ['Churn Risk', 'Users']
    col1, col2 = st.columns(2)
    col1.plotly_chart(px.pie(seg_count, values='Users',
                      names='Segment', title='Revenue Segments'))
    col2.plotly_chart(px.pie(churn, values='Users',
                      names='Churn Risk', title='Churn Risk Levels'))

with raw:
    st.subheader("📁 Raw Dataset")
    st.dataframe(filtered_df)
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Filtered Data", csv,
                       "filtered_data.csv", "text/csv")
