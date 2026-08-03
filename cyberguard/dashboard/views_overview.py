"""
Executive SOC Overview Dashboard View
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from cyberguard.ai.insight_engine import AIInsightEngine

def render_overview_view(df: pd.DataFrame):
    st.subheader("🎯 SOC Executive Overview & Threat Intelligence")
    
    # 1. Top KPI Row
    total_events = len(df)
    failed_logins = int((df["status"] == "Failed").sum())
    fail_rate = (failed_logins / total_events * 100.0) if total_events > 0 else 0.0
    critical_alerts = int((df["severity"] == "CRITICAL").sum())
    high_alerts = int((df["severity"] == "HIGH").sum())
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Authentication Events", f"{total_events:,}")
    k2.metric("Failed Logins", f"{failed_logins:,}", f"{fail_rate:.1f}% Fail Rate")
    k3.metric("Critical Threat Incidents", f"{critical_alerts:,}", delta_color="inverse")
    k4.metric("High Severity Alerts", f"{high_alerts:,}", delta_color="inverse")
    
    st.markdown("---")
    
    # 2. AI Security Insights Narrative Card
    st.markdown("### 🤖 AI Threat Insights & Executive Briefing")
    insights = AIInsightEngine.generate_narrative_insights(df)
    with st.container():
        st.info("\n\n".join([f"• {insight}" for insight in insights]))

    st.markdown("---")

    # 3. Interactive Plotly Visualizations
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("#### 📈 Authentication Velocity & Threat Timeline")
        df_time = df.set_index("timestamp").resample("1h")["status"].value_counts().unstack().fillna(0)
        
        fig_time = px.line(
            df_time,
            title="Hourly Authentication Success vs Failure Velocity",
            labels={"value": "Login Volume", "timestamp": "Timestamp"},
            color_discrete_map={"Success": "#10b981", "Failed": "#ef4444"}
        )
        fig_time.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_time, use_container_width=True)

    with col_right:
        st.markdown("#### 🎯 Threat Vector & Risk Severity Distribution")
        fig_pie = px.pie(
            df,
            names="severity",
            title="Incident Severity Breakdown",
            color="severity",
            color_discrete_map={
                "CRITICAL": "#dc2626",
                "HIGH": "#ea580c",
                "MEDIUM": "#eab308",
                "LOW": "#10b981",
                "INFO": "#3b82f6"
            },
            hole=0.4
        )
        fig_pie.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_pie, use_container_width=True)

    # 4. Top Risky Users & Devices Table
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 👤 Top 5 Risky User Accounts")
        risky_users = df.groupby("username").agg(
            total_logins=("status", "count"),
            failures=("is_failed", "sum"),
            max_risk=("risk_score", "max"),
            threat_vector=("threat_vector", "last")
        ).sort_values(by="max_risk", ascending=False).head(5).reset_index()
        st.dataframe(risky_users, use_container_width=True)
        
    with c2:
        st.markdown("#### 💻 Top Risky Origin Devices")
        risky_devices = df.groupby("device_type").agg(
            total_attempts=("status", "count"),
            failures=("is_failed", "sum"),
            max_risk=("risk_score", "max")
        ).sort_values(by="max_risk", ascending=False).reset_index()
        st.dataframe(risky_devices, use_container_width=True)
