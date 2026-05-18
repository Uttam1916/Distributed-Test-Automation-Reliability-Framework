import sqlite3
import pandas as pd
import streamlit as st
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "metrics.db")
ANOMALY_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "anomalies.json")

st.set_page_config(page_title="Reliability Dashboard", layout="wide")
st.title("Distributed Reliability Dashboard")

# Load data
try:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM metrics", conn)
    conn.close()
except:
    st.error("No metrics database found. Run runner.py first.")
    st.stop()

if df.empty:
    st.warning("No data yet. Run runner.py first.")
    st.stop()

# Top level numbers
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Requests", len(df))
col2.metric("Successes", len(df[df["status"] == "success"]))
col3.metric("Failures", len(df[df["status"] == "failure"]))
col4.metric("Avg Latency (ms)", f"{df[df['status'] == 'success']['latency'].mean():.2f}")

st.divider()

# Latency by endpoint
st.subheader("Average Latency by Endpoint")
latency_df = df[df["status"] == "success"].groupby("endpoint")["latency"].mean().reset_index()
st.bar_chart(latency_df.set_index("endpoint"))

# Failure counts
st.subheader("Failure Count by Endpoint")
failure_df = df[df["status"] == "failure"].groupby("endpoint").size()
if not failure_df.empty:
    st.bar_chart(failure_df)
else:
    st.write("No failures recorded.")

# Raw data
st.subheader("Raw Metrics Table")
st.dataframe(df)

# Anomalies
st.subheader("Detected Anomalies")
try:
    with open(ANOMALY_FILE, "r") as f:
        anomalies = json.load(f)
    if anomalies:
        st.json(anomalies)
    else:
        st.success("No anomalies detected.")
except:
    st.warning("No anomalies file found. Run runner.py first.")