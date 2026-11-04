
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

# Make the src folder available for imports
PROJECT_DIR = Path(__file__).resolve().parent
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from config import get_engine
from data_access import load_data
from analysis import build_reports


st.set_page_config(
    page_title="Online Store Transaction Analysis",
    page_icon="🛒",
    layout="wide"
)


@st.cache_data(ttl=60)
def get_reports():
    engine = get_engine()

    try:
        orders, items = load_data(engine)
    finally:
        engine.dispose()

    return build_reports(orders, items)


st.title("🛒 Online Store Transaction Analysis")
st.write("Analyze orders, payments, sales, and product performance.")

if st.button("🔄 Refresh Data"):
    get_reports.clear()
    st.rerun()

try:
    reports = get_reports()
    stats = reports["stats"]

    st.subheader("Transaction Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Orders", stats["total_orders"])
    col2.metric("Completed Orders", stats["completed_orders"])
    col3.metric(
        "Completed Sales",
        f"₹{stats['completed_sales_value']:,.2f}"
    )
    col4.metric(
        "Average Order Value",
        f"₹{stats['average_order_value']:,.2f}"
    )

    st.divider()

    # Order status
    st.subheader("1. Order Status Distribution")
    status = reports["status_report"]

    if not status.empty:
        st.bar_chart(
            status.set_index("order_status")["order_count"]
        )
        st.dataframe(status, use_container_width=True)

    # Payment methods
    st.subheader("2. Payment Method Analysis")
    payment = reports["payment_report"]

    if not payment.empty:
        st.bar_chart(
            payment.set_index("payment_method")["order_count"]
        )
        st.dataframe(payment, use_container_width=True)

    # Daily orders
    st.subheader("3. Daily Order Volume")
    daily = reports["daily_orders"]

    if not daily.empty:
        st.line_chart(
            daily.set_index("day")["order_count"]
        )

    # Monthly orders
    st.subheader("4. Monthly Order Volume")
    monthly = reports["monthly_orders"]

    if not monthly.empty:
        st.bar_chart(
            monthly.set_index("month")["order_count"]
        )

    # Product performance
    st.subheader("5. Top Products by Units Sold")
    products = reports["product_units"].head(15)

    if not products.empty:
        st.bar_chart(
            products.set_index("product_name")["units_sold"]
        )
        st.dataframe(products, use_container_width=True)
    else:
        st.info("No completed product sales found.")

    # Transaction details
    st.subheader("6. Transaction Details")
    transactions = reports["transaction_summary"]

    st.dataframe(
        transactions,
        use_container_width=True,
        hide_index=True
    )

    st.success("Dashboard connected to MySQL successfully!")

except ValueError as error:
    st.warning(str(error))

except Exception as error:
    st.error("Unable to load data from MySQL.")
    st.exception(error)
