# frontend/app.py

import streamlit as st
from app_show_data_ui import show_home_page, show_data_explorer_page, test_backend_connection
from nlp_ui import show_nlp_analysis_page
from var_ui import show_var_simulation_page

# 应用标题和基本信息
st.set_page_config(page_title="经济政策影响分析工具", layout="wide")

# 侧边栏导航
st.sidebar.title("导航")
page = st.sidebar.radio("选择页面", ["首页", "数据浏览器", "政策声明分析(NLP)", "政策效应模拟(VAR)"])

# --- 修改：将后端连接测试放到首页，避免干扰其他页面 ---
if page == "首页":
    show_home_page()
    with st.expander("后端连接状态"):
        test_backend_connection()
elif page == "数据浏览器":
    st.title("数据浏览器")
    show_data_explorer_page()
elif page == "政策声明分析(NLP)":
    st.title("政策声明情感分析 (NLP)")
    show_nlp_analysis_page()
elif page == "政策效应模拟(VAR)":
    st.title("政策效应模拟 (VAR)")
    show_var_simulation_page()