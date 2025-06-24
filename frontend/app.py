import os
import sys

# Ensure that the project root is in sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import streamlit as st
from utils import set_page_config, set_page_style, initialize_session_state, setup_sidebar
from admin.admin_dashboard import admin_dashboard  # Import from the admin folder
from client import client_main                      # Import from client.py

def main():
    set_page_config()
    set_page_style()
    initialize_session_state()
    setup_sidebar()

    view_choice = st.radio("Select View:", ("Client", "Admin"))
    if view_choice == "Admin":
        admin_dashboard()
    else:
        client_main()

if __name__ == "__main__":
    main()
