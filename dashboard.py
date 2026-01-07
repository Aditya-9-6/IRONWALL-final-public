import streamlit as st
import pandas as pd
import json
from state_manager import state_db

st.set_page_config(page_title="IronWall God Mode", layout="wide")

st.title("🛡️ IronWall v3.1: Empire Dashboard (DLC Enabled)")

col1, col2, col3 = st.columns(3)

# Fetch Data
try:
    # Banned IPs
    banned_list = state_db.get_banned_ips()
    banned_count = len(banned_list)
    
    # Schemas
    schemas = state_db.get_all_schemas()
    # Unique endpoints count
    unique_endpoints = set((s['method'], s['path']) for s in schemas)
    schema_count = len(unique_endpoints)
    
    db_status = "🟢 Connected (SQLite)"
except Exception as e:
    banned_count = 0
    schema_count = 0
    banned_list = []
    schemas = []
    db_status = f"🔴 Error: {e}"

# Metrics
col1.metric("DB Status", db_status)
col2.metric("Total Banned IPs", banned_count)
col3.metric("Learned API Endpoints", schema_count)

st.divider()

# --- Metrics & Visualizations ---
st.subheader("📊 Metrics & Visualizations")

# Data for visualizations
waf_events_data = state_db.get_waf_events(limit=1000)
request_logs_data = state_db.get_logs(limit=1000)

if request_logs_data:
    df_logs_viz = pd.DataFrame(request_logs_data)
    df_logs_viz['time'] = pd.to_datetime(df_logs_viz['timestamp'], unit='s')
    
    # Time series chart
    st.caption("Requests per Minute")
    requests_per_minute = df_logs_viz.set_index('time').resample('T').size().reset_index(name='count')
    st.line_chart(requests_per_minute.set_index('time'))

if waf_events_data:
    df_events_viz = pd.DataFrame(waf_events_data)
    
    col1, col2 = st.columns(2)

    with col1:
        # Pie chart for attack types
        st.caption("Blocked Requests by Attack Type")
        attack_types = df_events_viz['rule'].value_counts()
        st.bar_chart(attack_types)

    with col2:
        # Bar chart for top attacked endpoints
        st.caption("Top 10 Attacked Endpoints")
        top_endpoints = df_events_viz['path'].value_counts().head(10)
        st.bar_chart(top_endpoints)

st.divider()

# --- WAF Events Section ---
st.subheader("🚨 Real-time WAF Events")
if waf_events_data:
    df_events = pd.DataFrame(waf_events_data[:50]) # Top 50
    df_events['time'] = pd.to_datetime(df_events['timestamp'], unit='s')
    st.dataframe(df_events, use_container_width=True)
else:
    st.info("No WAF events recorded yet.")

# --- Banned IPs Section ---
st.subheader("🚫 Active Ban List")

if banned_list:
    # [(ip, reason, timestamp, ttl), ...]
    ban_data = []
    for row in banned_list:
        # row: (ip, reason, timestamp, ttl)
        # Note: if fetchall returns tuples or Row objects. 
        # state_manager fetchall returns tuples.
        ban_data.append({
            "IP": row[0],
            "Reason": row[1],
            "Time": pd.to_datetime(row[2], unit='s'),
            "TTL": row[3]
        })
    
    df = pd.DataFrame(ban_data)
    st.dataframe(df, use_container_width=True)

    # Simple Unban Tool
    st.caption("Admin Actions")
    ip_to_unban = st.selectbox("Select IP to Unban", [d["IP"] for d in ban_data])
    if st.button("Unban IP"):
        state_db.unban_ip(ip_to_unban)
        st.success(f"Unbanned {ip_to_unban}")
        st.experimental_rerun()
else:
    st.info("No IPs are currently banned. The Galaxy is safe... for now.")

st.divider()

# --- Learned Schemas Section ---
st.subheader("🧠 Predator Intelligence (Learned Schemas)")
st.caption("Passive API discovery from traffic.")

if schemas:
    # Organize schemas into a tree
    tree = {}
    for entry in schemas:
        # entry keys: host, method, path, field, type_name
        endpoint = f"{entry['method']} {entry['path']}"
        field = entry['field']
        type_name = entry['type_name']
        
        if endpoint not in tree:
            tree[endpoint] = {}
            
        if field not in tree[endpoint]:
            tree[endpoint][field] = []
        
        tree[endpoint][field].append(type_name)
            
    selected_endpoint = st.selectbox("Select an Endpoint to Inspect", list(tree.keys()))
    
    if selected_endpoint:
        st.json(tree[selected_endpoint])
else:
    st.warning("No logic learned yet. Generate some traffic!")

st.divider()

# --- Request Logs Section ---
st.subheader("📜 Live Request Logs")

if request_logs_data:
    df_logs = pd.DataFrame(request_logs_data[:100])
    df_logs['time'] = pd.to_datetime(df_logs['timestamp'], unit='s')
    st.dataframe(df_logs, use_container_width=True)
else:
    st.info("No requests logged yet.")
