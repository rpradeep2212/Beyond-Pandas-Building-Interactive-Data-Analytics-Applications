import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sales Analytics Dashboard", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("sales_data.csv", parse_dates=["Date"])

df = load_data()

st.title("📊 Interactive Sales Analytics Dashboard")
st.caption("Explore sales performance by region, category and time.")

# Sidebar filters
st.sidebar.header("Filter the data")
regions = ["All"] + sorted(df["Region"].unique().tolist())
categories = ["All"] + sorted(df["Category"].unique().tolist())
selected_region = st.sidebar.selectbox("Choose region", regions)
selected_category = st.sidebar.selectbox("Choose category", categories)
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()
date_range = st.sidebar.date_input("Choose date range", (min_date, max_date))

filtered = df.copy()
if selected_region != "All":
    filtered = filtered[filtered["Region"] == selected_region]
if selected_category != "All":
    filtered = filtered[filtered["Category"] == selected_category]
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[filtered["Date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date))]

if filtered.empty:
    st.warning("No records match these filters. Please change your selection.")
    st.stop()

# KPI metrics
total_sales = filtered["Sales"].sum()
total_orders = len(filtered)
average_order = filtered["Sales"].mean()
units_sold = filtered["Quantity"].sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total sales", f"₹{total_sales:,.0f}")
c2.metric("Transactions", f"{total_orders:,}")
c3.metric("Average transaction", f"₹{average_order:,.0f}")
c4.metric("Units sold", f"{units_sold:,}")

# Charts
left, right = st.columns(2)
with left:
    by_category = filtered.groupby("Category", as_index=False)["Sales"].sum()
    fig_bar = px.bar(by_category, x="Category", y="Sales", color="Category",
                     title="Sales by category", text_auto=".2s")
    st.plotly_chart(fig_bar, use_container_width=True)

with right:
    monthly = (filtered.assign(Month=filtered["Date"].dt.to_period("M").astype(str))
               .groupby("Month", as_index=False)["Sales"].sum())
    fig_line = px.line(monthly, x="Month", y="Sales", markers=True,
                       title="Monthly sales trend")
    st.plotly_chart(fig_line, use_container_width=True)

fig_scatter = px.scatter(filtered, x="Quantity", y="Sales", color="Region",
                         hover_data=["Product", "Category", "Date"],
                         title="Quantity vs sales")
st.plotly_chart(fig_scatter, use_container_width=True)

st.subheader("Filtered transaction records")
st.dataframe(filtered.sort_values("Date", ascending=False), use_container_width=True)

csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("Download filtered data (CSV)", data=csv,
                   file_name="filtered_sales_data.csv", mime="text/csv")
