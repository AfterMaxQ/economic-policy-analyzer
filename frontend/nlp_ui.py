# frontend/nlp_ui.py

import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# ---------------------------------
#  新的实时分析 UI 函数
# ---------------------------------
def show_realtime_nlp_analyzer():
    """
    提供一个UI界面，用于对单个URL进行实时情感分析。
    """
    st.subheader("实时声明分析")
    st.markdown("输入一篇 FOMC 声明的 URL，立即获得其多维度政策倾向分析。")
    
    default_url = "https://www.federalreserve.gov/newsevents/pressreleases/monetary20230503a.htm"
    url = st.text_input("输入FOMC声明的URL:", default_url, key="realtime_url_input")

    if st.button("开始实时分析"):
        if not url.startswith("https://www.federalreserve.gov"):
            st.warning("请输入一个有效的美联储官网URL。")
        else:
            with st.spinner("正在爬取和分析文本..."):
                try:
                    # 调用我们新的实时分析API
                    api_url = "http://localhost:8000/analysis/nlp/realtime"
                    response = requests.post(api_url, json={"url": url})
                    
                    if response.status_code == 200:
                        st.success("实时分析成功！")
                        result = response.json()
                        
                        # --- 可视化倾向条 (与之前完全一样) ---
                        for item in result['analysis']:
                            neg_name = item['negative_name']
                            pos_name = item['positive_name']
                            neg_score = item['negative_score_percent']
                            pos_score = item['positive_score_percent']
                            
                            st.markdown(f"**{neg_name} vs. {pos_name}**")
                            st.markdown(
                                f"""
                                <div style="display: flex; align-items: center; border: 1px solid #444; border-radius: 5px; overflow: hidden;">
                                    <div style="width: {neg_score}%; background-color: #e50064; color: white; text-align: right; padding: 5px 10px; box-sizing: border-box;">
                                        {neg_score}%
                                    </div>
                                    <div style="width: {pos_score}%; background-color: #00b092; color: white; text-align: left; padding: 5px 10px; box-sizing: border-box;">
                                        {pos_score}%
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            st.text("")

                        with st.expander("查看实时分析的原始JSON结果"):
                            st.json(result)
                    else:
                        st.error(f"分析失败: {response.json().get('detail', '未知错误')}")
                
                except requests.exceptions.RequestException as e:
                    st.error(f"无法连接到后端服务: {e}")


# ---------------------------------
#  历史数据仪表盘函数 (保持不变)
# ---------------------------------
@st.cache_data
def load_fomc_history():
    """从后端API获取完整的FOMC分析历史数据。"""
    api_url = "http://localhost:8000/analysis/fomc/history"
    response = requests.get(api_url)
    response.raise_for_status()
    
    data = response.json()['data']
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    return df.set_index('date')


def show_nlp_analysis_page():
    """
    主页面函数，现在包含了历史仪表盘和实时分析两个部分。
    """
    # --- 历史仪表盘部分 ---
    st.subheader("历史仪表盘")
    st.markdown("此仪表盘展示了从2000年至今，历次FOMC会议声明的多维度情感分析结果。")

    try:
        with st.spinner("正在从后端加载分析历史..."):
            df_analysis = load_fomc_history()

        dimension_options = {
            "monetary_stance_positive_score": "货币立场 (鹰派倾向)",
            "economic_outlook_positive_score": "经济前景 (乐观倾向)"
        }
        selected_dimension = st.selectbox(
            "选择要可视化的分析维度:",
            options=list(dimension_options.keys()),
            format_func=lambda key: dimension_options[key]
        )

        fig = px.line(
            df_analysis, 
            y=selected_dimension,
            title=f"{dimension_options[selected_dimension]} 历史走势",
            labels={"date": "会议日期", selected_dimension: "倾向得分 (0-100)"},
            markers=True
        )
        fig.update_yaxes(range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("查看历史数据详情与声明原文"):
            st.dataframe(df_analysis)
            selected_date = st.selectbox(
                "选择会议日期以查看原文:",
                options=df_analysis.index.strftime('%Y-%m-%d').tolist()
            )
            if selected_date:
                st.text_area(
                    "声明原文",
                    value=df_analysis.loc[selected_date]['statement_text'],
                    height=300,
                    key="history_text_area"
                )

    except Exception as e:
        st.error(f"加载历史数据时出错: {e}")

    # --- 分割线 ---
    st.divider()

    # --- 调用新的实时分析UI函数 ---
    show_realtime_nlp_analyzer()