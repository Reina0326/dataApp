import streamlit as st
from app import show_descriptive_statistics # app.py
from Hool import show_hool_bolovsruulalt # Hool.py
st.set_page_config(layout="wide")
# Хуудас сонгох UI
page = st.sidebar.radio("Хуудас сонгох", ("Descriptive Statistics","Хоол боловсруулалт"))

# Descriptive Statistic page сонговол 
if page == "Descriptive Statistics":
    show_descriptive_statistics()

if page == "Хоол боловсруулалт":
    show_hool_bolovsruulalt()
