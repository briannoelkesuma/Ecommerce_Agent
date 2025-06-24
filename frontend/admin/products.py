import streamlit as st
import requests

# Change this URL as needed for your backend.
PRODUCTS_API_URL = "http://localhost:8000/products"

def manage_products():
    st.header("Manage Products")
    
    # Fetch and display products.
    st.subheader("Products Management")
    try:
        res = requests.get(PRODUCTS_API_URL)
        if res.ok:
            products = res.json()
            st.dataframe(products)
        else:
            st.error("Failed to fetch products: " + res.text)
            products = []
    except Exception as e:
        st.error(f"Error fetching products: {e}")
        products = []

    # Add New Product Form.
    st.markdown("#### Add New Product")
    with st.form("admin_add_product", clear_on_submit=True):
        name = st.text_input("Product Name")
        category = st.text_input("Category")
        description = st.text_area("Description")
        price = st.number_input("Price", min_value=0.01, step=0.01, format="%.2f")
        quantity = st.number_input("Quantity", min_value=0, step=1)
        add_submitted = st.form_submit_button("Add Product")
        if add_submitted:
            payload = {
                "ProductName": name,
                "Category": category,
                "Description": description,
                "Price": price,
                "Quantity": quantity,
            }
            try:
                post_res = requests.post(PRODUCTS_API_URL, json=payload)
                if post_res.ok:
                    st.success("Product added successfully.")
                    st.rerun()
                else:
                    st.error("Error adding product: " + post_res.text)
            except Exception as e:
                st.error(f"Error adding product: {e}")

    # Update and Delete Product Section.
    if products:
        st.markdown("#### Update or Delete Product")
        # Build a dict with keys as "id: name" and values as the product dict.
        product_options = {f"{p['ProductId']}: {p['ProductName']}": p for p in products}
        selected_key = st.selectbox("Select Product", list(product_options.keys()))
        selected_product = product_options[selected_key]

        # Update Form.
        with st.form("update_product_form", clear_on_submit=True):
            upd_name = st.text_input("Product Name", value=selected_product["ProductName"])
            upd_category = st.text_input("Category", value=selected_product["Category"])
            upd_description = st.text_area("Description", value=selected_product.get("Description", ""))
            upd_price = st.number_input("Price", min_value=0.01, step=0.01, 
                                        value=float(selected_product["Price"]), format="%.2f")
            upd_quantity = st.number_input("Quantity", min_value=0, step=1, 
                                           value=int(selected_product["Quantity"]))
            update_submitted = st.form_submit_button("Update Product")
            if update_submitted:
                payload = {
                    "ProductName": upd_name,
                    "Category": upd_category,
                    "Description": upd_description,
                    "Price": upd_price,
                    "Quantity": upd_quantity,
                }
                try:
                    put_res = requests.put(f"{PRODUCTS_API_URL}/{selected_product['ProductId']}", json=payload)
                    if put_res.ok:
                        st.success("Product updated successfully.")
                        st.rerun()
                    else:
                        st.error("Error updating product: " + put_res.text)
                except Exception as e:
                    st.error(f"Error updating product: {e}")

        # Delete Button.
        if st.button(f"Delete {selected_product['ProductName']}"):
            try:
                del_res = requests.delete(f"{PRODUCTS_API_URL}/{selected_product['ProductId']}")
                if del_res.ok:
                    st.success("Product deleted successfully.")
                    st.rerun()
                else:
                    st.error("Error deleting product: " + del_res.text)
            except Exception as e:
                st.error(f"Error deleting product: {e}")
