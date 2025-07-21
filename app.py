import streamlit as st
import pandas as pd
from utils import process_file
from database import insert_receipt
import os
import tempfile
from datetime import datetime

st.set_page_config(page_title="Receipt Analyzer", layout="wide")
st.title("🧾 Receipt Analyzer Dashboard")

# Session state init
if "data" not in st.session_state:
    st.session_state["data"] = pd.DataFrame()
if "processed_files" not in st.session_state:
    st.session_state["processed_files"] = set()

# 🔁 Refresh button
if st.button("🔄 Refresh / Start Over"):
    st.session_state["data"] = pd.DataFrame()
    st.session_state["processed_files"] = set()
    st.rerun()

# File upload
uploaded_files = st.file_uploader(
    "Upload Receipt",
    type=["jpg", "jpeg", "png", "pdf", "txt"],
    accept_multiple_files=True,
    help="Drag and drop or select receipt files (max 200MB each)",
)

# File processing
if uploaded_files:
    for file in uploaded_files:
        if file.name in st.session_state["processed_files"]:
            continue
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name

        result = process_file(tmp_path, file.name)
        os.remove(tmp_path)

        if result:
            df_row = pd.DataFrame([result])
            st.session_state["data"] = pd.concat(
                [st.session_state["data"], df_row], ignore_index=True
            )
            st.session_state["processed_files"].add(file.name)
            insert_receipt(result)

# Display table
df = st.session_state["data"]

if not df.empty:
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    if df["date"].notna().any():
        min_date = df["date"].min().date()
        max_date = df["date"].max().date()
    else:
        min_date = max_date = datetime.today().date()

    st.warning("⚠️ Some receipts may not have a valid date.") if df["date"].isna().any() else None

    # Sidebar filters
    col1, col2, col3, col4, col5 = st.columns(5)

    vendor_opt = ["All"] + sorted(df["vendor"].dropna().unique().tolist())
    category_opt = ["All"] + sorted(df["category"].dropna().unique().tolist())
    currency_opt = ["All", "₹", "$", "€", "£"]

    vendor = col1.selectbox("Vendor", vendor_opt)
    category = col2.selectbox("Category", category_opt)
    currency = col3.selectbox("Currency", currency_opt)

    date_from = col4.date_input("From Date", min_value=min_date, max_value=max_date, value=min_date)
    date_to = col5.date_input("To Date", min_value=min_date, max_value=max_date, value=max_date)

    filtered = df.copy()
    if vendor != "All":
        filtered = filtered[filtered["vendor"] == vendor]
    if category != "All":
        filtered = filtered[filtered["category"] == category]
    if currency != "All":
        filtered = filtered[filtered["amount"].astype(str).str.contains(currency)]

    filtered = filtered[
        (filtered["date"] >= pd.to_datetime(date_from)) &
        (filtered["date"] <= pd.to_datetime(date_to))
    ]

    st.subheader("📄 Parsed Receipt Data")
    st.dataframe(filtered)

    # Exports
    st.download_button("⬇️ Export as CSV", filtered.to_csv(index=False), "receipts.csv")
    st.download_button("⬇️ Export as JSON", filtered.to_json(orient="records"), "receipts.json")

    if filtered["amount"].notna().any():
        st.subheader("📊 Visualizations")
        col6, col7 = st.columns(2)

        with col6:
            st.markdown("**Expenditure by Category**")
            st.bar_chart(filtered.groupby("category")["amount"].sum())

        with col7:
            st.markdown("**Expenditure by Vendor**")
            st.bar_chart(filtered.groupby("vendor")["amount"].sum())

        st.markdown("**📈 Time-Series Trend (3-day Moving Avg)**")
        ts_data = filtered.dropna(subset=["date", "amount"])
        if not ts_data.empty:
            time_series = ts_data.groupby("date")["amount"].sum().sort_index()
            st.line_chart(time_series.rolling(3, min_periods=1).mean())
    else:
        st.warning("No valid amount values found for plotting charts.")

    # Show missing-date receipts
    no_date_df = df[df["date"].isna()]
    if not no_date_df.empty:
        st.subheader("🕓 Receipts without Valid Date")
        st.dataframe(no_date_df)
else:
    st.info("Upload one or more receipt files to start.")
