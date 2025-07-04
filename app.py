import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="User Behaviour Dashboard", layout="wide")
st.title("Matiks User Behaviour Dashboard")

df = pd.read_csv("Matiks - Data Analyst Data - Sheet1.csv"), parse_dates = ["session_date"])

    st.subheader("Raw Data")
    st.dataframe(df.head())

    st.subheader("Daily Active Users (DAU)")
    dau = df.groupby("session_date")["user_id"].nunique().reset_index()
    fig = px.line(dau, x="session_date", y="user_id", title="Daily Active Users")
    st.plotly_chart(fig, use_container_width=True)
