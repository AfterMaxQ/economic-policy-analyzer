# frontend/nlp_ui.py

import streamlit as st
import requests
import plotly.express as px


def show_nlp_analysis_page():
    st.markdown("此模块用于分析美联储(FOMC)政策声明的情感倾向。")

    # 提供一个默认的URL供用户测试
    default_url = "https://www.federalreserve.gov/newsevents/pressreleases/monetary20230503a.htm"
    url = st.text_input("输入FOMC声明的URL:", default_url)

    if st.button("开始分析"):
        if not url.startswith("https://www.federalreserve.gov"):
            st.warning("请输入一个有效的美联储官网URL。")
        else:
            with st.spinner("正在爬取和分析文本..."):
                try:
                    # 调用后端API
                    api_url = "http://localhost:8000/analysis/nlp"
                    response = requests.post(api_url, json={"url": url})

                    if response.status_code == 200:
                        st.success("分析成功！")
                        result = response.json()
                        analysis_data = result['analysis'][0]

                        label = analysis_data['label'].capitalize()
                        score = analysis_data['score']

                        st.metric(label=f"情感倾向: {label}", value=f"{score:.2%}")
                        st.json(result)
                    else:
                        st.error(f"分析失败: {response.json().get('detail', '未知错误')}")

                except requests.exceptions.RequestException as e:
                    st.error(f"无法连接到后端服务: {e}")