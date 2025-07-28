# Influencer Campaign ROI Dashboard

Table of Contents
01. Introduction
02. Goals
03. App Features
04. How to Use
05. Data Format
06. Dashboard Walkthrough
07. Technical Approach
08. How to Run Locally
09. Dependencies
10. Customization
11. Contact

# Introduction
This repository contains a Streamlit app that allows you to track, visualize, and analyze the ROI of influencer marketing campaigns. It empowers marketing teams to evaluate campaign performance, explore influencer/segment-level analytics, and produce polished PDF analytics reports—all from a no-code, interactive dashboard.

# Goals
1. Build a dashboard to analyze influencer marketing campaigns across social platforms.
2. Track and visualize return on ad spend (incremental ROAS), influencer insights, and payout tracking.
3. Provide data-driven insights via intuitive charts/tables, and an end-to-end reporting workflow.

# App Features
- Data Upload: Accepts Excel/CSV files formatted as required.
- Smart Data Processing: Cleans, engineers, and calculates key marketing metrics on upload.
- Dynamic Filtering: Segment your analysis by date, campaign, platform, category, gender, or performance band.
- Rich Visualizations: Interactive Plotly charts—monthly trends, ROI breakdown, marketing funnel, influencer deep-dive, category comparisons, outlier analysis, and more.
- Influencer Deep Dive: Drill down to top/bottom performers using configurable metrics.
- Campaign Comparison: Compare channels or segments across any metric (ROI, revenue, engagement, etc.).
- Seasonality & Cohorts: Explore trends by cohort and over time.
- Export: Download filtered data as CSV, generate analytics PDF reports (charts and tables).
- Clean UI/UX: Responsive Streamlit interface, KPI cards, color-coded visual cues.

# How to Use
- Upload Your Data.
- Use the sidebar to upload your influencer campaign data (Excel or CSV).
- A sample data preview and formatting guide are available in-app.
- Apply Filters.
- Filter by campaign, category, platform, gender, date, and performance band.
- Navigate Tabs.
- Explore charts and tables organized into logical tabs: Overview, Funnel, Influencer Deep Dive, Content Analysis, Comparisons, Seasonality/Cohorts, Outliers, and Raw Data Export.
- Download Reports.
- Download your filtered data as CSV.
- Generate a full PDF analytics report with key metrics and charts.

# Data Format
Required columns:
- date (YYYY-MM-DD or DD/MM/YYYY)
- name (Influencer name)
- platform (e.g., Instagram, YouTube)
- campaign
- category (Content/vertical)
- gender
- reach
- followers
- likes
- comments
- orders
- revenue
- total_payout
- basis (Payout basis: Post/Order)
A sample data table is displayed in-app. Ensure columns are named as above for correct processing.

# Dashboard Walkthrough
Tabs include:
1. Overview: KPI cards, monthly trends, campaign ROI bar charts, platform engagement rates, and highlights.
2. Marketing Funnel: Visualizes user journey (from reach to revenue/investment).
3. Influencer Deep Dive: Top/bottom performers and scatter plots for influencer analysis.
4. Content & Audience: Performance vs. categories, platform/campaign/category sunburst.
5. Comparisons: Segment bar/pie charts across platform, gender, category, or campaign.
6. Seasonality & Cohorts: Trend lines across any metric and cohort dimension.
7. Distributions & Outliers: Violin/box plots and outlier influencer tables.
8. Raw Data & Export: Data download and PDF report generation.

# Technical Approach
- Framework: Built in Python with Streamlit for UI/UX.
- Visualization: Uses Plotly Express and Graph Objects for interactive, high-fidelity charts.
- Data Processing: Pandas for all aggregation, grouping, and metric engineering.
- PDF Reports: Plotly image export + FPDF for high-quality snapshots of analyses.
- Performance Banding: Built-in categorization for "High", "Good", "Average", and "Poor" performers, fully dynamic.
- Deployment: Runs on Streamlit Cloud (or locally).

# How to Run Locally
- Clone repo or copy code.
Install dependencies:
bash
pip install -r requirements.txt

- (Optional) For plot export:
bash
pip install -U kaleido

- Run the app:
bash
streamlit run app.py

# Dependencies
streamlit, 
pandas, 
numpy, 
plotly,
streamlit_extras.metric_cards, 
fpdf, 
kaleido (for exporting Plotly figures as images in PDF reports), 
openpyxl (for Excel data support).

# Customization
Change filters or metrics by editing the relevant code block for each tab.
Add or remove KPIs and visualizations as needed for your use case.

# Contact
If you have questions about the assignment or this app, please reach out via GitHub issues or shalmali0401@gmail.com.

