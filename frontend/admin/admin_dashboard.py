import streamlit as st
from .products import manage_products
from .orders import manage_orders

def admin_dashboard():
    st.header("Admin Dashboard")
    tab_products, tab_orders = st.tabs(["Manage Products", "Manage Orders"])
    with tab_products:
        manage_products()
    with tab_orders:
        manage_orders()