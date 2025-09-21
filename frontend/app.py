# frontend/app.py
import streamlit as st
from app_show_data_ui import show_home_page, show_fred_data, show_notebook_data, test_backend_connection, show_indicator_data

# 应用标题和基本信息
st.set_page_config(page_title="经济政策影响分析工具", layout="wide")

# 侧边栏导航
st.sidebar.title("经济政策影响分析工具")

# 使用按钮代替选择框进行页面导航
if st.sidebar.button("首页"):
    st.session_state.page = "首页"
if st.sidebar.button("数据呈现"):
    st.session_state.page = "数据呈现"
if st.sidebar.button("数据分析"):
    st.session_state.page = "数据分析"
if st.sidebar.button("数据预测"):
    st.session_state.page = "数据预测"

# 初始化页面状态
if 'page' not in st.session_state:
    st.session_state.page = "首页"  # 默认选择首页

# 根据选择的页面显示相应内容
if st.session_state.page == "首页":
    show_home_page()
elif st.session_state.page == "数据呈现":
    test_backend_connection()
    show_fred_data()
    show_indicator_data()
elif st.session_state.page == "数据分析":
    st.title("数据分析")
    st.write("此页面将用于展示经济政策分析功能，包括VAR模型和脉冲响应函数等。")
elif st.session_state.page == "数据预测":
    st.title("数据预测")
    st.write("此页面将用于展示基于历史数据和模型的经济预测功能。")