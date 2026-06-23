{\rtf1\ansi\ansicpg1252\cocoartf2639
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;\f1\fnil\fcharset0 AppleColorEmoji;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import pandas as pd\
import plotly.express as px\
\
# --- Configuration ---\
st.set_page_config(page_title="ED Hospital Besut Dashboard", layout="wide")\
\
# --- Data Processing ---\
@st.cache_data\
def load_data(file_path):\
    xls = pd.ExcelFile(file_path)\
    all_data = []\
    \
    for month in xls.sheet_names:\
        df_raw = pd.read_excel(file_path, sheet_name=month)\
        \
        # Find the row containing 'DATE' to dynamically set the header\
        date_row_idx = df_raw[df_raw.eq('DATE').any(axis=1)].index[0]\
        df = pd.read_excel(file_path, sheet_name=month, header=date_row_idx + 1)\
        \
        # Clean column names (remove newlines and extra spaces)\
        df.columns = df.columns.str.replace('\\n', ' ').str.strip()\
        \
        # Filter to keep only rows where DATE is a valid day (1-31)\
        df = df[pd.to_numeric(df['DATE'], errors='coerce').notnull()]\
        df['Month'] = month\
        all_data.append(df)\
        \
    combined_df = pd.concat(all_data, ignore_index=True)\
    \
    # Convert relevant columns to numeric\
    numeric_cols = ['OPD', 'ADM', 'JUM', 'MVA', 'AMB CALL', 'BID', 'DID', 'M', 'K', 'H <120', 'H >120']\
    for col in numeric_cols:\
        if col in combined_df.columns:\
            combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce').fillna(0)\
            \
    # Apply custom logic: Combine H <120 and H >120 into Total Green (H)\
    if 'H <120' in combined_df.columns and 'H >120' in combined_df.columns:\
        combined_df['Total Green (H)'] = combined_df['H <120'] + combined_df['H >120']\
        \
    return combined_df, xls.sheet_names\
\
# --- Main App Layout ---\
st.title("
\f1 \uc0\u55356 \u57317 
\f0  Unit Kecemasan Hospital Besut Dashboard (2026)")\
st.markdown("---")\
\
file_path = "Reten ED HOSBES 2026.xlsx" \
\
try:\
    df, months_order = load_data(file_path)\
    \
    # --- Top KPI Metrics ---\
    st.subheader("Overview (Jan - May)")\
    col1, col2, col3, col4 = st.columns(4)\
    \
    total_jum = int(df['JUM'].sum())\
    total_opd = int(df['OPD'].sum())\
    total_adm = int(df['ADM'].sum())\
    total_mva = int(df['MVA'].sum())\
    \
    col1.metric("Total Patients (JUM)", f"\{total_jum:,\}")\
    col2.metric("Discharged (OPD)", f"\{total_opd:,\}")\
    col3.metric("Admissions (ADM)", f"\{total_adm:,\}")\
    col4.metric("MVA Cases", f"\{total_mva:,\}")\
    \
    st.markdown("---")\
    \
    # --- Charts Section ---\
    col_chart1, col_chart2 = st.columns(2)\
    \
    with col_chart1:\
        st.subheader("
\f1 \uc0\u55357 \u56998 
\f0  Triage Distribution")\
        # Data preparation for Triage Donut Chart\
        triage_data = pd.DataFrame(\{\
            'Category': ['Red (M)', 'Yellow (K)', 'Green (H)'],\
            'Count': [df['M'].sum(), df['K'].sum(), df['Total Green (H)'].sum()]\
        \})\
        \
        fig_triage = px.pie(\
            triage_data, \
            values='Count', \
            names='Category', \
            color='Category',\
            color_discrete_map=\{'Red (M)':'#ef4444', 'Yellow (K)':'#eab308', 'Green (H)':'#22c55e'\},\
            hole=0.4\
        )\
        st.plotly_chart(fig_triage, use_container_width=True)\
        \
    with col_chart2:\
        st.subheader("
\f1 \uc0\u55357 \u56520 
\f0  Monthly Patient Volume")\
        # Data preparation for Trend Line Chart\
        monthly_trend = df.groupby('Month')[['JUM', 'OPD', 'ADM']].sum().reindex(months_order).reset_index()\
        \
        fig_trend = px.line(\
            monthly_trend, \
            x='Month', \
            y=['JUM', 'OPD', 'ADM'], \
            labels=\{'value':'Number of Patients', 'variable':'Patient Type'\},\
            markers=True\
        )\
        st.plotly_chart(fig_trend, use_container_width=True)\
\
except FileNotFoundError:\
    st.error("
\f1 \uc0\u9888 \u65039 
\f0  Error: Excel file not found. Please make sure 'Reten ED HOSBES 2026.xlsx' is in the same directory as this script.")\
except Exception as e:\
    st.error(f"
\f1 \uc0\u9888 \u65039 
\f0  An error occurred: \{e\}")}