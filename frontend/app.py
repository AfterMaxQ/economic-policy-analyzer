# frontend/app.py

import streamlit as st
# 导入我们新的统一函数
from app_show_data_ui import show_home_page, show_data_explorer_page, test_backend_connection

# 应用标题和基本信息
st.set_page_config(page_title="经济政策影响分析工具", layout="wide")

# 侧边栏导航
st.sidebar.title("导航")
page = st.sidebar.radio("选择页面", ["首页", "数据浏览器", "数据分析", "数据预测"])


# 根据选择的页面显示相应内容
if page == "首页":
    show_home_page()
elif page == "数据浏览器":
    st.title("数据浏览器")
    test_backend_connection()
    # 调用我们新的统一函数
    show_data_explorer_page()
elif page == "数据分析":
    st.title("数据分析")
    st.info("功能开发中... 此页面将用于展示经济政策分析功能，包括VAR模型和脉冲响应函数等。")
elif page == "数据预测":
    st.title("数据预测")
    st.info("功能开发中... 此页面将用于展示基于历史数据和模型的经济预测功能。")