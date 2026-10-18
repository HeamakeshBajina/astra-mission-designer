"""ASTRA Mission Designer application entry point."""

import streamlit as st

st.set_page_config(
    page_title="ASTRA Mission Designer",
    page_icon="rocket",
    layout="wide",
)

dashboard_page = st.Page(
    "pages/0_Mission_Dashboard.py",
    title="Mission Dashboard",
    default=True,
)

guide_page = st.Page(
    "pages/1_User_Guide.py",
    title="User Guide",
)

st.navigation([dashboard_page, guide_page], position="sidebar").run()
