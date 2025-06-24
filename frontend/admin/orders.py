import streamlit as st
import requests

# Change this URL as needed for your backend.
ORDERS_API_URL = "http://localhost:8000/orders"

def manage_orders():
    st.header("Manage Orders")
    
    # Fetch and display orders.
    st.subheader("Orders Overview")
    try:
        orders_res = requests.get(ORDERS_API_URL)
        if orders_res.ok:
            orders = orders_res.json()
            st.dataframe(orders)
        else:
            st.error("Failed to fetch orders: " + orders_res.text)
            orders = []
    except Exception as e:
        st.error(f"Error fetching orders: {e}")
        orders = []

    # For example, include a delete option for orders.
    if orders:
        st.markdown("#### Delete Order")
        order_options = {f"{o['OrderId']}": o for o in orders}
        selected_order_key = st.selectbox("Select Order to Delete", list(order_options.keys()))
        selected_order = order_options[selected_order_key]
        if st.button(f"Delete Order {selected_order['OrderId']}"):
            try:
                del_order_res = requests.delete(f"{ORDERS_API_URL}/{selected_order['OrderId']}")
                if del_order_res.ok:
                    st.success("Order deleted successfully.")
                    st.rerun()
                else:
                    st.error("Error deleting order: " + del_order_res.text)
            except Exception as e:
                st.error(f"Error deleting order: {e}")
    else:
        st.info("No orders available.")
