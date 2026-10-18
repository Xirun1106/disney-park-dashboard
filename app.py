import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Disney Park Operations", page_icon="🎢", layout="wide")
BASE = Path(__file__).resolve().parent

@st.cache_data
def load_data():
    crowd = pd.read_csv(BASE / "data" / "calendar_enriched.csv", parse_dates=["date"])
    rides = pd.read_csv(BASE / "data" / "ride_stats.csv")
    crowd["year"] = pd.to_numeric(crowd["year"], errors="coerce")
    rides["year_num"] = pd.to_numeric(rides["year"], errors="coerce")
    crowd = crowd.dropna(subset=["park_name", "date", "crowd_level_pct", "year"])
    rides = rides.dropna(subset=["park_name", "ride_name", "minutes"])
    return crowd, rides

crowd, rides = load_data()
st.title("🎢 Disney Analytics Team | Park Operations Dashboard")
st.caption("For park operations managers | Identify historically busy periods and attractions that may need staffing attention.")
st.info("Historical Kaggle snapshot, NOT live queues. Daily crowd scores and annual attraction wait summaries have different measurement units and granularity.", icon="ℹ️")

parks = sorted(crowd["park_name"].unique())
years = sorted(crowd["year"].dropna().astype(int).unique(), reverse=True)
with st.sidebar:
    st.header("Filters")
    park = st.selectbox("Theme park", parks, index=parks.index("Magic Kingdom") if "Magic Kingdom" in parks else 0)
    year = st.selectbox("Year", years, index=0)
    st.caption("A park and year are selected to keep comparisons consistent.")

selected = crowd.loc[(crowd["park_name"] == park) & (crowd["year"] == year)].sort_values("date").copy()
selected_rides = rides.loc[(rides["park_name"] == park) & (rides["year_num"] == year) & (rides["metric"] == "ride_avg_wait") & (rides["is_archived"] == 0)].copy()

if selected.empty:
    st.warning("No crowd records for this selection.")
    st.stop()

mean_crowd = selected["crowd_level_pct"].mean()
heavy_days = (selected["crowd_level_pct"] >= 80).mean() * 100
k1,k2,k3 = st.columns(3)
k1.metric("Average crowd score", f"{mean_crowd:.1f}%")
k2.metric("Days at 80%+ crowd score", f"{heavy_days:.1f}%")
k3.metric("Dates observed", f"{len(selected):,}")

st.subheader("1. When are crowds highest?")
selected["rolling_14d"] = selected["crowd_level_pct"].rolling(14, min_periods=1).mean()
fig = px.line(selected, x="date", y="rolling_14d", labels={"date":"Date", "rolling_14d":"14-observation rolling crowd score (%)"})
fig.update_traces(line_color="#2477bc")
fig.update_layout(margin=dict(l=12,r=12,t=16,b=8), yaxis_range=[0,100])
st.plotly_chart(fig, use_container_width=True)
st.caption("Smoothed 14-observation trend. Values are historical crowd scores (0–100), not a direct percentage of park capacity. Missing dates, if any, are not filled.")

st.subheader("2. Which attractions had the longest average waits?")
if selected_rides.empty:
    st.warning("No active-attraction yearly average-wait summary for this park and year.")
else:
    top = selected_rides.nlargest(8,"minutes").sort_values("minutes")
    fig2 = px.bar(top, x="minutes", y="ride_name", orientation="h", labels={"minutes":"Reported average wait (minutes)","ride_name":"Attraction"}, text="minutes")
    fig2.update_traces(marker_color="#2477bc", textposition="outside")
    fig2.update_layout(margin=dict(l=12,r=25,t=12,b=8), yaxis_title=None)
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("Yearly aggregated wait-time statistics for non-archived attractions. These are not waits for the selected date, and not live queue times. Ranking depends on tracked attraction coverage.")

st.divider()
st.caption(f"Crowd data: {selected['date'].min():%b %d, %Y} – {selected['date'].max():%b %d, %Y} for {park}; full dataset: {crowd['date'].min():%b %d, %Y} – {crowd['date'].max():%b %d, %Y}. Source: Kaggle Walt Disney World Wait Times and Crowd Calendar. Proposed production refresh: daily for strategic planning; actual live operations would need a separate live wait-time feed.")
st.caption("Interpretation: the 80% threshold is an illustrative management review trigger, not an official Disney operating standard. Historical results cannot guarantee future crowd conditions.")
