import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
from datetime import datetime
from io import StringIO
from streamlit_extras.metric_cards import style_metric_cards
import tempfile
from fpdf import FPDF
import plotly.io as pio

st.set_page_config(page_title="Influencer Campaign ROI Dashboard", layout="wide")
st.title("Influencer Campaign ROI Dashboard 📊")

# ---- SIDEBAR: DATA UPLOAD ---- #
st.sidebar.header("🔄 Upload Your Data")
with st.sidebar.expander("📖 Data Format Guide & Sample"):
    st.markdown("""
    **Your data should include these columns:**  
    - `date` (YYYY-MM-DD or DD/MM/YYYY)
    - `name` (Influencer name)
    - `platform` (e.g., Instagram, YouTube)
    - `campaign`
    - `category` (Content/vertical)
    - `gender` (Influencer gender)
    - `reach`
    - `followers`
    - `likes`
    - `comments`
    - `orders`
    - `revenue`
    - `total_payout`
    - `basis` (Payout basis: Post/Order)
    """)
    st.write("**Sample data:**")
    st.dataframe(pd.DataFrame({
        "date": ["2024-01-01", "2024-01-04"],
        "name": ["Influencer 1", "Influencer 2"],
        "platform": ["Instagram", "YouTube"],
        "campaign": ["Spring", "New Year"],
        "category": ["Beauty", "Fitness"],
        "gender": ["Female", "Male"],
        "reach": [10000, 8000],
        "followers": [11000, 8200],
        "likes": [350, 200],
        "comments": [40, 15],
        "orders": [27, 15],
        "revenue": [22000, 12000],
        "total_payout": [2000, 1000],
        "basis": ["Post", "Order"],
    }))

uploaded_file = st.sidebar.file_uploader(
    "Upload Excel (.xlsx) or CSV file", 
    type=["csv", "xlsx"],
    help="Upload your influencer campaign data following the shown format."
)

# ---- LOAD DATA LOGIC ---- #
@st.cache_data
def clean_and_engineer(df):
    df["date"] = pd.to_datetime(df["date"])
    df["engagement"] = df["likes"] + df["comments"]
    df["engagement_rate"] = (df["engagement"] / df["reach"].replace(0, np.nan)) * 100
    df["roas"] = df["revenue"] / df["total_payout"].replace(0, np.nan)
    df["roi_percentage"] = (df["revenue"] - df["total_payout"]) / df["total_payout"].replace(0, np.nan) * 100
    df["average_order_value"] = df["revenue"] / df["orders"].replace(0, np.nan)
    df["performance_category"] = df["roi_percentage"].apply(
        lambda x: ("High Performer" if x >= 200 else
                   "Good Performer" if x >= 100 else
                   "Average Performer" if x >= 0 else
                   "Poor Performer")
    )
    return df

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        df = clean_and_engineer(df)
        st.success("✅ File uploaded and processed successfully!")
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        st.stop()
else:
    st.info("No file uploaded yet. Using sample data for demonstration.")
    df = pd.read_excel("MOCK_DATA-2.xlsx")
    df = clean_and_engineer(df)

# ---- DYNAMIC FILTERS ---- #
st.sidebar.header("🔍 Filters")

date_min, date_max = st.sidebar.date_input(
    "Date range",
    (df["date"].min(), df["date"].max()),
    min_value=df["date"].min(),
    max_value=df["date"].max(),
)

# Use multiselect for multiple checkbox-like selections
campaigns = st.sidebar.multiselect(
    "Select Campaign(s):", 
    options=sorted(df["campaign"].unique()), 
    default=sorted(df["campaign"].unique())
)
platforms = st.sidebar.multiselect(
    "Select Platform(s):", 
    options=sorted(df["platform"].unique()), 
    default=sorted(df["platform"].unique())
)
categories = st.sidebar.multiselect(
    "Select Category(s):", 
    options=sorted(df["category"].unique()), 
    default=sorted(df["category"].unique())
)
genders = st.sidebar.multiselect(
    "Select Gender(s):", 
    options=sorted(df["gender"].unique()), 
    default=sorted(df["gender"].unique())
)

perf_band = st.sidebar.selectbox(
    "Performance band", 
    options=["All", "High Performer", "Good Performer", "Average Performer", "Poor Performer"], 
    index=0
)

# Filter data by user selections
flt = (
    df["date"].dt.date.between(date_min, date_max) &
    df["campaign"].isin(campaigns) &
    df["platform"].isin(platforms) &
    df["category"].isin(categories) &
    df["gender"].isin(genders)
)

if perf_band != "All":
    flt &= df["performance_category"].eq(perf_band)

data = df[flt]

if data.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# ───────── TABS ───────── #
tab_titles = [
    "Overview",
    "Marketing Funnel",
    "Influencers Deep Dive",
    "Content & Audience",
    "Comparisons",
    "Seasonality & Cohorts",
    "Distributions & Outliers",
    "Raw Data & Export",
]
tabs = st.tabs(tab_titles)

# ---- TAB 1: OVERVIEW ---- #
with tabs[0]:
    st.header("📊 Campaign Highlights")

    # KPI Cards
    kpi_cols = st.columns(5)
    kpi_cols[0].metric("Total Revenue", f"${data['revenue'].sum():,.0f}")
    kpi_cols[1].metric("Total Investment", f"${data['total_payout'].sum():,.0f}")
    roi_all = (data["revenue"].sum() - data["total_payout"].sum()) / data["total_payout"].sum() * 100
    kpi_cols[2].metric("Overall ROI", f"{roi_all:.1f}%", delta_color="normal" if roi_all >= 0 else "inverse")
    kpi_cols[3].metric("Avg Engagement Rate", f"{data['engagement_rate'].mean():.1f}%")
    kpi_cols[4].metric("Total Orders", f"{data['orders'].sum():,}")
    style_metric_cards(
        background_color="#fbfbfb",
        border_color="#2d6cdf",
        border_radius_px=10,
        border_size_px=2,
        box_shadow=True,
    )

    kpi_cols2 = st.columns(5)
    kpi_cols2[0].metric("Total Reach", f"{data['reach'].sum():,}")
    kpi_cols2[1].metric("Avg ROAS", f"{data['roas'].mean():.2f}x")
    kpi_cols2[2].metric("Active Influencers", data["name"].nunique())
    kpi_cols2[3].metric("Avg Order Value", f"${data['average_order_value'].mean():.2f}")
    kpi_cols2[4].metric("Cost / Order", f"${data['total_payout'].sum() / data['orders'].sum():.2f}")
    style_metric_cards(
        background_color="#fbfbfb",
        border_color="#2d6cdf",
        border_radius_px=10,
        border_size_px=2,
        box_shadow=True,
    )

    st.subheader("Key Analytical Summary")
    st.info(
        f"""
    - **{data['name'].nunique():,}** active influencers across **{data['platform'].nunique()}** platforms.
    - **Top performing campaign:** {data.groupby('campaign')['roi_percentage'].mean().idxmax()} 
      ({data.groupby('campaign')['roi_percentage'].mean().max():.1f}% avg ROI).
    - **Lowest performing campaign:** {data.groupby('campaign')['roi_percentage'].mean().idxmin()}
      ({data.groupby('campaign')['roi_percentage'].mean().min():.1f}% avg ROI).
    - **Most active day:** {data['date'].value_counts().idxmax().date()}.
    """
    )

    # Monthly trend chart
    trend = data.copy()
    trend["month"] = trend["date"].dt.to_period("M").astype(str)
    mon = trend.groupby("month").agg(
        revenue=("revenue", "sum"),
        spend=("total_payout", "sum"),
        orders=("orders", "sum")
    ).reset_index()
    mon["roi%"] = (mon["revenue"] - mon["spend"]) / mon["spend"] * 100

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=mon["month"], y=mon["revenue"], name="Revenue", marker_color="lightskyblue"), secondary_y=False)
    fig.add_trace(go.Bar(x=mon["month"], y=mon["spend"], name="Spend", marker_color="salmon"), secondary_y=False)
    fig.add_trace(go.Scatter(x=mon["month"], y=mon["roi%"], name="ROI %", line=dict(color="green", width=3)), secondary_y=True)
    fig.update_layout(title_text="Monthly Trend", barmode="group", height=480, legend=dict(orientation="h"))
    fig.update_yaxes(title_text="USD", secondary_y=False)
    fig.update_yaxes(title_text="ROI %", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)
    
    c1, c2 = st.columns(2)
    with c1:
        camp = data.groupby("campaign").agg({"revenue": "sum", "total_payout": "sum"}).reset_index()
        camp["roi %"] = (camp["revenue"] - camp["total_payout"]) / camp["total_payout"] * 100
        fig = px.bar(
            camp.sort_values("roi %"),
            x="roi %",
            y="campaign",
            orientation="h",
            color="roi %",
            color_continuous_scale="RdYlGn",
            title="ROI by Campaign",
            labels={
                "roi %": "ROI %",
                "campaign": "Campaign"
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        eng = data.groupby("platform")["engagement_rate"].mean().reset_index()
        fig = px.bar(
        eng,
        x="platform", y="engagement_rate", color="engagement_rate",
        title="Engagement Rate by Platform",
        labels={
            "platform": "Platform",
            "engagement_rate": "Engagement Rate"
        }
    )
    fig.update_layout(coloraxis_colorbar=dict(title="Engagement Rate"))
    st.plotly_chart(fig, use_container_width=True)


# ───────── TAB 2: MARKETING FUNNEL ───────── #
with tabs[1]:
    st.header("🛒 Marketing Funnel Analysis")

    funnel_df = data[["reach", "engagement", "orders", "revenue", "total_payout"]].sum()
    funnel_labels = ["Reach", "Engagements", "Orders", "Revenue", "Investment"]
    funnel_vals = [int(funnel_df["reach"]), int(funnel_df["engagement"]), int(funnel_df["orders"]), int(funnel_df["revenue"]), int(funnel_df["total_payout"])]

    fig = go.Figure(
        go.Funnel(
            y=funnel_labels,
            x=funnel_vals,
            marker={"color": ["#f6c85f", "#6f4e7c", "#c8553d", "#1786d7", "#19a979"]},
            textinfo="value+percent initial",
        )
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("This marketing funnel visualizes the entire influencer journey—from total campaign reach, through engagement, to orders, revenue, and total investment. It highlights how much of your initial reach was retained at each stage, helping diagnose bottlenecks and optimize your campaign ROI.")

    st.markdown(f"- **Conversion efficiency:** {funnel_vals[2] / funnel_vals[0] * 100:.2f}% of reach converted to orders.")

    cols = st.columns(4)
    cols[0].metric("Reach → Engagement", f"{funnel_vals[1] / funnel_vals[0] * 100:.2f}%")
    cols[1].metric("Engagement → Order", f"{funnel_vals[2] / funnel_vals[1] * 100:.2f}%")
    cols[2].metric("Order → Revenue (AOV)", f"${funnel_vals[3] / funnel_vals[2]:.2f}")
    cols[3].metric("ROAS (Revenue/Ad Spend)", f"{funnel_df['revenue'] / funnel_df['total_payout']:.2f}x")
    style_metric_cards(box_shadow=True, border_radius_px=8, border_color="#6f4e7c")

# ───────── TAB 3: INFLUENCER DEEP DIVE ───────── #
with tabs[2]:
    st.header("🧑‍💼 Influencer Breakdown")

    metric_col = st.selectbox(
        "Top/Bottom Influencers by:",
        [
            "engagement_rate",
            "orders",
            "roi_percentage",
            "revenue",
            "reach",
        ],
        format_func=lambda x: {
            "engagement_rate": "Engagement Rate",
            "orders": "Orders",
            "roi_percentage": "ROI (%)",
            "revenue": "Revenue",
            "reach": "Reach",
        }[x],
    )
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 10 Influencers")
        st.dataframe(
            data.nlargest(10, metric_col)[
                ["name", "platform", "campaign", "engagement_rate", "orders", "roi_percentage", "revenue", "followers"]
                if "followers" in data.columns
                else ["name", "platform", "campaign", "engagement_rate", "orders", "roi_percentage", "revenue"]
            ]
            .style.format(
                {
                    "engagement_rate": "{:.1f}%",
                    "roi_percentage": "{:.1f}%",
                    "orders": "{:,}",
                    "revenue": "${:,.0f}",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )
    with col2:
        st.subheader("Bottom 10 Influencers")
        st.dataframe(
            data.nsmallest(10, metric_col)[
                ["name", "platform", "campaign", "engagement_rate", "orders", "roi_percentage", "revenue", "followers"]
                if "followers" in data.columns
                else ["name", "platform", "campaign", "engagement_rate", "orders", "roi_percentage", "revenue"]
            ]
            .style.format(
                {
                    "engagement_rate": "{:.1f}%",
                    "roi_percentage": "{:.1f}%",
                    "orders": "{:,}",
                    "revenue": "${:,.0f}",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

    import plotly.express as px

    facet_by = st.radio(
        "Facet by:", 
        ["platform", "gender", "performance_category"], 
        index=0, 
        horizontal=True
    )
    color_choices = [x for x in ["platform", "gender", "performance_category"] if x != facet_by]
    color_by = st.radio(
        "Color by:", 
        color_choices, 
        index=0, 
        horizontal=True
    )
    
    fig = px.scatter(
        data,
        x="followers" if "followers" in data.columns else "reach",
        y="revenue",
        size="engagement_rate",
        color=color_by,
        facet_col=facet_by,
        hover_data=["name", "roi_percentage", "orders", "campaign"],
        log_x=True,
        title=f"Followers vs Revenue, faceted by {facet_by.capitalize()}, colored by {color_by.capitalize()}",
        color_discrete_sequence=px.colors.qualitative.Set2 if color_by == "gender" 
                                else px.colors.qualitative.Set1 if color_by == "platform"
                                else px.colors.diverging.Portland,  # for categories
        size_max=22,
    )
    fig.update_layout(
        height=450, 
        xaxis_title="Followers", 
        yaxis_title="Revenue",
        legend_title=color_by.replace("_", " ").title()
    )
    st.plotly_chart(fig, use_container_width=True)



# ───────── TAB 4: CONTENT & AUDIENCE ───────── #
with tabs[3]:
    st.header("📝 Content & Audience Analysis")

    # Only the content category distribution (single column chart)
    perf_cat = data.groupby(["category", "performance_category"]).size().unstack(fill_value=0)
    st.bar_chart(perf_cat)
    st.caption("Distribution of performance bands across content categories.")
    
    st.subheader("Campaigns by Platform")
    sunburst_fig = px.sunburst(
        data,
        path=["platform", "campaign", "category"],
        values="revenue",
        color="platform",
        title="Nested Platform → Campaign → Category Revenue",
        width=800,    
        height=600,   
    )
    st.plotly_chart(sunburst_fig, use_container_width=False)  

# ───────── TAB 5: COMPARISONS ───────── #
with tabs[4]:
    st.header("🔀 Slice & Compare Segments")

    compare_by = st.selectbox("Compare by:", ["platform", "gender", "category", "campaign"])
    metric = st.selectbox("Metric:", ["revenue", "orders", "roi_percentage", "engagement_rate", "total_payout"])
    if compare_by and metric:
        metric_df = data.groupby(compare_by)[metric].mean().reset_index()
        bar = px.bar(metric_df, x=compare_by, y=metric, color=compare_by, title=f"Avg {metric.replace('_', ' ').title()} by {compare_by.title()}")
        st.plotly_chart(bar, use_container_width=True)
        pie = px.pie(metric_df, names=compare_by, values=metric, title=f"{metric.replace('_', ' ').title()} Share by {compare_by.title()}")
        st.plotly_chart(pie, use_container_width=True)

# ───────── TAB 6: SEASONALITY & COHORTS ───────── #
with tabs[5]:
    st.header("📆 Seasonality & Cohort Trends")

    data["year_month"] = data["date"].dt.to_period("M").astype(str)
    group_by = st.radio("Cohort by:", ["platform", "campaign", "category"], horizontal=True)
    metric_sel = st.selectbox("Trend metric:", ["revenue", "orders", "roi_percentage", "engagement_rate"])

    cohort_df = data.groupby([group_by, "year_month"])[metric_sel].mean().reset_index()
    fig = px.line(cohort_df, x="year_month", y=metric_sel, color=group_by, title=f"{metric_sel.replace('_', ' ').title()} Cohorts Over Time")
    st.plotly_chart(fig, use_container_width=True)

# ───────── TAB 7: DISTRIBUTIONS & OUTLIERS ───────── #
with tabs[6]:
    st.header("📈 Distributions & Outliers")

    c1, c2 = st.columns(2)
    with c1:
        # Violin plot for ROI Distribution (shows density, spread, and quartiles)
        fig = px.violin(data, y="roi_percentage", color="performance_category", box=True, points="all",
                        title="ROI (%) Distribution by Performance Category")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Box plot + swarm/strip-like plot overlay for Engagement Rate
        # Plotly doesn't have swarm plot natively, so we do a box plot with points
        fig = px.box(data, y="engagement_rate", color="platform", points="all",
                     title="Engagement Rate Distribution by Platform")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top/Bottom ROI Outliers")
    outlier_df = data.loc[
        (data["roi_percentage"] > data["roi_percentage"].mean() + 2 * data["roi_percentage"].std()) |
        (data["roi_percentage"] < data["roi_percentage"].mean() - 2 * data["roi_percentage"].std())
    ][["name", "campaign", "platform", "roi_percentage", "revenue", "total_payout"]]
    st.dataframe(outlier_df, use_container_width=True)

# ───────── TAB 8: RAW DATA & EXPORT ───────── #
with tabs[7]:
    st.header("Raw Filtered Data & Report Export")
    st.write("Preview & download your filtered influencer campaign data.")

    st.dataframe(data, use_container_width=True)
    csv = data.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "filtered_influencer_data.csv", "text/csv", key="download-csv")

    st.markdown("---")
    st.subheader("Generate Automated Analytics Report (PDF)")

    # Helper function to save plotly figure as image and return path
    def plotly_fig_to_img(fig):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        pio.write_image(fig, tmp.name, format='png', width=900, height=500)
        return tmp.name

    def build_pdf_report(data):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 18)
        pdf.cell(0, 15, "Influencer Campaign Analytics Report", ln=True, align="C")
        pdf.set_font("Arial", size=12)
        pdf.ln(2)
        pdf.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)

        # Example: Add key metrics
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 12, "Key Metrics", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 8, 
            f"Total Revenue: ${data['revenue'].sum():,.0f}\n"
            f"Total Investment: ${data['total_payout'].sum():,.0f}\n"
            f"Overall ROI: {((data['revenue'].sum()-data['total_payout'].sum())/data['total_payout'].sum()*100):.1f}%\n"
            f"Total Orders: {data['orders'].sum():,}\n"
            f"Active Influencers: {data['name'].nunique()}"
        )
        pdf.ln(2)

        # Add key charts (reuse your actual chart code)
        charts = []

        # 1. Monthly Trend Chart
        trend = data.copy()
        trend["month"] = trend["date"].dt.to_period("M").astype(str)
        mon = trend.groupby("month").agg(
            revenue=("revenue", "sum"),
            spend=("total_payout", "sum"),
            orders=("orders", "sum")
        ).reset_index()
        mon["roi%"] = (mon["revenue"] - mon["spend"]) / mon["spend"] * 100
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=mon["month"], y=mon["revenue"], name="Revenue", marker_color="lightskyblue"), secondary_y=False)
        fig.add_trace(go.Bar(x=mon["month"], y=mon["spend"], name="Spend", marker_color="salmon"), secondary_y=False)
        fig.add_trace(go.Scatter(x=mon["month"], y=mon["roi%"], name="ROI %", line=dict(color="green", width=3)), secondary_y=True)
        fig.update_layout(title_text="Monthly Trend", barmode="group", height=400, legend=dict(orientation="h"))
        charts.append(("Monthly Trend", fig))

        # 2. ROI By Campaign Chart
        camp = data.groupby("campaign").agg({"revenue": "sum", "total_payout": "sum"}).reset_index()
        camp["roi %"] = (camp["revenue"] - camp["total_payout"]) / camp["total_payout"] * 100
        fig2 = px.bar(
            camp.sort_values("roi %"),
            x="roi %",
            y="campaign",
            orientation="h",
            color="roi %",
            color_continuous_scale="RdYlGn",
            title="ROI by Campaign"
        )
        charts.append(("ROI by Campaign", fig2))

        # 3. Engagement Rate by Platform
        eng = data.groupby("platform")["engagement_rate"].mean().reset_index()
        fig3 = px.bar(eng, x="platform", y="engagement_rate", color="engagement_rate", title="Engagement Rate by Platform")
        charts.append(("Engagement by Platform", fig3))

        # 4. ROI Distribution (Violin)
        fig4 = px.violin(data, y="roi_percentage", color="performance_category", box=True, points="all", title="ROI (%) Distribution")
        charts.append(("ROI Distribution", fig4))

        # 5. Engagement Rate Distribution (Box)
        fig5 = px.box(data, y="engagement_rate", color="platform", points="all", title="Engagement Rate by Platform")
        charts.append(("Engagement Distribution", fig5))

        # Add charts to PDF
        for title, fig in charts:
            chart_img = plotly_fig_to_img(fig)
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 12, title, ln=True)
            pdf.image(chart_img, w=185)
            pdf.ln(5)

        # Advanced: Add more analyses, data tables, commentary as needed
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 12, "Top/Bottom ROI Outliers", ln=True)
        outlier_df = data.loc[
            (data["roi_percentage"] > data["roi_percentage"].mean() + 2 * data["roi_percentage"].std()) |
            (data["roi_percentage"] < data["roi_percentage"].mean() - 2 * data["roi_percentage"].std())
        ][["name", "campaign", "platform", "roi_percentage", "revenue", "total_payout"]]
        pdf.set_font("Arial", size=8)
        pdf.multi_cell(0, 6, outlier_df.to_string(index=False))

        return pdf.output(dest="S").encode("latin-1")

    if st.button("Download Report (PDF)"):
        with st.spinner("Generating report..."):
            pdf_data = build_pdf_report(data)
            st.download_button(
                label="Download Analytics Report",
                data=pdf_data,
                file_name="Influencer_Analysis_Report.pdf",
                mime="application/pdf"
            )

# ───────── FOOTER ───────── #
st.markdown("---")
st.caption(f"© {datetime.now().year} Influencer ROI Dashboard")

