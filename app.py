import pandas as pd
import plotly.express as px
import streamlit as st

PBI_DIR = "powerbi_data"
OUT_DIR = "output"
TEMPLATE = "plotly_white"
COLOR_MAIN = "#0f766e"

st.set_page_config(page_title="Online Retail Dashboard", layout="wide")


@st.cache_data
def load_sales():
    return pd.read_csv(
        f"{PBI_DIR}/FactSales.csv",
        parse_dates=["InvoiceDate"],
        dtype={"InvoiceNo": "str", "CustomerID": "Int64"},
    )


@st.cache_data
def load_segments():
    df = pd.read_csv(f"{OUT_DIR}/customer_segments.csv")
    df["CustomerID"] = df["CustomerID"].round().astype("Int64")
    df["CustomerID"] = df["CustomerID"].astype(str)
    return df


@st.cache_data
def load_cohort_retention():
    long_df = pd.read_csv(f"{PBI_DIR}/CohortRetention_long.csv")
    return long_df.pivot(index="Cohort", columns="CohortIndex", values="Retention")


@st.cache_data
def load_clv():
    return pd.read_csv(f"{PBI_DIR}/DimCohortCLV.csv")


def fmt_money(value):
    return f"\u00a3{value:,.0f}"


def fmt_int(value):
    return f"{value:,.0f}"


def style_fig(fig, height=400, title=None, x_title=None, y_title=None):
    fig.update_layout(
        template=TEMPLATE,
        height=height,
        title=title,
        margin=dict(l=20, r=20, t=50 if title else 30, b=20),
        xaxis_title=x_title,
        yaxis_title=y_title,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


st.title("Online Retail \u2014 Sales & Customer Dashboard")

sales = load_sales()
segments = load_segments()
retention = load_cohort_retention()
clv = load_clv()

min_date = sales["InvoiceDate"].min().date()
max_date = sales["InvoiceDate"].max().date()

with st.sidebar:
    st.header("Filters")
    date_range = st.date_input(
        "Transaction period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    country_filter = st.multiselect(
        "Country",
        options=sorted(sales["Country"].unique()),
        placeholder="All countries",
    )
    st.caption("Leave Country empty to include every country.")
    st.divider()
    st.caption(
        f"Dataset: Dec 2010 - Dec 2011\n\n"
        f"Rows: {fmt_int(len(sales))} transactions"
    )

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

mask = (sales["InvoiceDate"].dt.date >= start_date) & (
    sales["InvoiceDate"].dt.date <= end_date
)
fdf = sales.loc[mask]
if country_filter:
    fdf = fdf[fdf["Country"].isin(country_filter)]

if fdf.empty:
    st.warning("No data matches the selected filters. Adjust the date range or countries.")
    st.stop()

tab_overview, tab_products, tab_customers, tab_segments, tab_retention = st.tabs(
    ["Overview", "Products", "Customers", "Segments (RFM)", "Retention & CLV"]
)

total_revenue = float(fdf["TotalPrice"].sum())
total_orders = int(fdf["InvoiceNo"].nunique())
total_customers = int(fdf["CustomerID"].nunique())
aov = total_revenue / total_orders if total_orders else 0.0
items_sold = int(fdf["Quantity"].sum())

with tab_overview:
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Revenue", fmt_money(total_revenue))
    k2.metric("Total Orders", fmt_int(total_orders))
    k3.metric("Unique Customers", fmt_int(total_customers))
    k4.metric("Avg Order Value", fmt_money(aov))
    k5.metric("Items Sold", fmt_int(items_sold))

    left, right = st.columns([3, 2])

    monthly = (
        fdf.groupby("YearMonth", as_index=False)["TotalPrice"]
        .sum()
        .sort_values("YearMonth")
    )
    fig_trend = px.line(monthly, x="YearMonth", y="TotalPrice", markers=True)
    fig_trend.update_traces(line_color=COLOR_MAIN)
    style_fig(
        fig_trend,
        height=420,
        title="Monthly Revenue Trend",
        x_title="Month",
        y_title="Revenue (\u00a3)",
    )
    left.plotly_chart(fig_trend, width="stretch")

    country_rev = (
        fdf.groupby("Country", as_index=False)["TotalPrice"]
        .sum()
        .nlargest(10, "TotalPrice")
        .sort_values("TotalPrice")
    )
    fig_country = px.bar(
        country_rev,
        x="TotalPrice",
        y="Country",
        orientation="h",
        color_discrete_sequence=[COLOR_MAIN],
        text_auto="~s",
    )
    style_fig(
        fig_country,
        height=420,
        title="Top 10 Countries by Revenue",
        x_title="Revenue (\u00a3)",
        y_title=None,
    )
    right.plotly_chart(fig_country, width="stretch")

with tab_products:
    prod = (
        fdf.groupby(["StockCode", "Description"], as_index=False)
        .agg(Quantity=("Quantity", "sum"), Revenue=("TotalPrice", "sum"))
    )
    prod["Product"] = prod["StockCode"] + " \u00b7 " + prod["Description"].str.strip()

    p_left, p_right = st.columns(2)

    top_qty = prod.nlargest(10, "Quantity").sort_values("Quantity")
    fig_qty = px.bar(
        top_qty,
        x="Quantity",
        y="Product",
        orientation="h",
        color_discrete_sequence=[COLOR_MAIN],
        text_auto="~s",
    )
    style_fig(fig_qty, height=480, title="Top 10 Products by Units Sold")

    top_rev = prod.nlargest(10, "Revenue").sort_values("Revenue")
    fig_rev = px.bar(
        top_rev,
        x="Revenue",
        y="Product",
        orientation="h",
        color_discrete_sequence=["#115e59"],
        text_auto="~s",
    )
    style_fig(fig_rev, height=480, title="Top 10 Products by Revenue (\u00a3)")

    p_left.plotly_chart(fig_qty, width="stretch")
    p_right.plotly_chart(fig_rev, width="stretch")

    bottom_rev = prod.nsmallest(10, "Revenue").sort_values("Revenue", ascending=False)
    fig_bottom = px.bar(
        bottom_rev,
        x="Revenue",
        y="Product",
        orientation="h",
        color_discrete_sequence=["#b91c1c"],
        text_auto="~s",
    )
    style_fig(
        fig_bottom,
        height=420,
        title="Bottom 10 Products by Revenue (worst performers)",
        x_title="Revenue (\u00a3)",
    )
    st.plotly_chart(fig_bottom, width="stretch")

with tab_customers:
    cust = (
        fdf.groupby("CustomerID", as_index=False)
        .agg(
            Revenue=("TotalPrice", "sum"),
            Orders=("InvoiceNo", "nunique"),
            Items=("Quantity", "sum"),
        )
    )
    cust["AOV"] = cust["Revenue"] / cust["Orders"]

    c1, c2 = st.columns(2)
    c1.metric("Avg Orders per Customer", f"{len(cust) and total_orders / len(cust):,.2f}")
    repeat_rate = (cust["Orders"] > 1).mean() * 100 if len(cust) else 0
    c2.metric("Repeat Purchase Rate", f"{repeat_rate:,.1f}%")

    cu_left, cu_right = st.columns(2)

    top_cust = cust.nlargest(10, "Revenue").sort_values("Revenue")
    top_cust["Customer"] = top_cust["CustomerID"].astype(str)
    fig_top_cust = px.bar(
        top_cust,
        x="Revenue",
        y="Customer",
        orientation="h",
        color_discrete_sequence=[COLOR_MAIN],
        text_auto="~s",
    )
    style_fig(
        fig_top_cust,
        height=440,
        title="Top 10 Customers by Revenue",
        x_title="Revenue (\u00a3)",
    )
    cu_left.plotly_chart(fig_top_cust, width="stretch")

    aov_cap = cust["AOV"].quantile(0.99)
    fig_aov = px.histogram(cust, x="AOV", nbins=50, color_discrete_sequence=[COLOR_MAIN])
    fig_aov.update_xaxes(range=(0, aov_cap))
    style_fig(
        fig_aov,
        height=440,
        title="Distribution of Avg Order Value per Customer",
        x_title="Avg Order Value (\u00a3, clipped at P99)",
        y_title="Customers",
    )
    cu_right.plotly_chart(fig_aov, width="stretch")

    table_cust = cust.nlargest(15, "Revenue").copy()
    table_cust["CustomerID"] = table_cust["CustomerID"].astype(str)
    table_cust["Revenue"] = table_cust["Revenue"].map(fmt_money)
    table_cust["AOV"] = table_cust["AOV"].map(fmt_money)
    table_cust.index = range(1, len(table_cust) + 1)
    st.dataframe(
        table_cust[["CustomerID", "Orders", "Items", "Revenue", "AOV"]],
        width="stretch",
    )

with tab_segments:
    st.caption(
        "RFM scores and K-Means clusters are computed on the full cleaned dataset "
        "(Dec 2010 - Dec 2011), so they are not affected by the sidebar filters."
    )

    s_left, s_right = st.columns(2)

    seg_counts = segments["Segment"].value_counts().reset_index()
    seg_counts.columns = ["Segment", "Customers"]
    fig_seg = px.pie(
        seg_counts,
        names="Segment",
        values="Customers",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    style_fig(fig_seg, height=420, title="Customers by RFM Segment")
    s_left.plotly_chart(fig_seg, width="stretch")

    cluster_counts = segments["Cluster_Name"].value_counts().reset_index()
    cluster_counts.columns = ["Cluster", "Customers"]
    fig_cluster = px.bar(
        cluster_counts.sort_values("Customers"),
        x="Customers",
        y="Cluster",
        orientation="h",
        color_discrete_sequence=[COLOR_MAIN],
        text_auto=True,
    )
    style_fig(fig_cluster, height=420, title="Customers by K-Means Cluster")
    s_right.plotly_chart(fig_cluster, width="stretch")

    fig_rfm = px.scatter(
        segments,
        x="Recency",
        y="Monetary",
        color="Cluster_Name",
        hover_data={"Frequency": True, "Segment": True},
        opacity=0.6,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_rfm.update_yaxes(type="log")
    style_fig(
        fig_rfm,
        height=480,
        title="Recency vs Monetary by Cluster (log scale)",
        x_title="Recency (days since last purchase)",
        y_title="Monetary (\u00a3, log)",
    )
    st.plotly_chart(fig_rfm, width="stretch")

    st.subheader("Customer Detail")
    search_id = st.text_input("Search Customer ID")
    seg_table = segments[
        ["CustomerID", "Recency", "Frequency", "Monetary", "RFM_score", "Segment", "Cluster_Name"]
    ].copy()
    if search_id.strip():
        seg_table = seg_table[seg_table["CustomerID"].str.contains(search_id.strip())]
    seg_table["Monetary"] = seg_table["Monetary"].map(fmt_money)
    seg_table = seg_table.reset_index(drop=True)
    st.dataframe(seg_table, width="stretch", height=380)
    st.caption(f"{fmt_int(len(seg_table))} customers shown")

with tab_retention:
    st.caption(
        "Cohort retention and CLV are computed on the full cleaned dataset "
        "(Dec 2010 - Dec 2011), so they are not affected by the sidebar filters."
    )

    fig_heat = px.imshow(
        retention,
        text_auto=".0%",
        aspect="auto",
        color_continuous_scale="Tealgrn",
        labels=dict(
            x="Months Since First Purchase",
            y="Cohort (first purchase month)",
            color="Retention",
        ),
    )
    fig_heat.update_yaxes(autorange="reversed")
    style_fig(fig_heat, height=520, title="Monthly Cohort Retention Heatmap")
    st.plotly_chart(fig_heat, width="stretch")

    avg_retention = retention.mean(skipna=True).reset_index()
    avg_retention.columns = ["Months Since First Purchase", "Avg Retention"]
    fig_avg = px.line(
        avg_retention,
        x="Months Since First Purchase",
        y="Avg Retention",
        markers=True,
    )
    fig_avg.update_traces(line_color=COLOR_MAIN)
    fig_avg.update_yaxes(tickformat=".0%")
    style_fig(
        fig_avg,
        height=340,
        title="Average Retention Curve Across Cohorts",
        y_title="Retention",
    )
    st.plotly_chart(fig_avg, width="stretch")

    st.subheader("Customer Lifetime Value (CLV)")

    clv_k1, clv_k2, clv_k3 = st.columns(3)
    clv_k1.metric("Average CLV", fmt_money(clv["CLV"].mean()))
    clv_k2.metric("Median CLV", fmt_money(clv["CLV"].median()))
    clv_k3.metric("Avg Lifespan (months)", f"{clv['Lifespan'].mean():,.1f}")

    clv_left, clv_right = st.columns(2)

    top_clv = clv.nlargest(15, "CLV").sort_values("CLV")
    top_clv["Customer"] = top_clv["CustomerID"].astype(str)
    fig_clv = px.bar(
        top_clv,
        x="CLV",
        y="Customer",
        orientation="h",
        color_discrete_sequence=[COLOR_MAIN],
        text_auto="~s",
    )
    style_fig(
        fig_clv,
        height=440,
        title="Top 15 Customers by CLV",
        x_title="CLV (\u00a3)",
    )
    clv_left.plotly_chart(fig_clv, width="stretch")

    clv_cohort = clv.groupby("Cohort", as_index=False)["CLV"].mean()
    fig_clv_cohort = px.bar(
        clv_cohort,
        x="Cohort",
        y="CLV",
        color_discrete_sequence=["#115e59"],
        text_auto="~s",
    )
    style_fig(
        fig_clv_cohort,
        height=440,
        title="Average CLV per Cohort Month",
        x_title="Cohort",
        y_title="Avg CLV (\u00a3)",
    )
    clv_right.plotly_chart(fig_clv_cohort, width="stretch")
