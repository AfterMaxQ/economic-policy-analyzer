import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import datetime


# --- 页面函数 ---

def show_home_page():
    """
    显示项目主页，介绍项目功能和目的。
    """
    st.title("经济政策影响分析工具")
    st.markdown("""
    ## 项目概述
    本项目是一个综合性的经济政策影响分析平台，旨在帮助用户：
    - 可视化宏观经济指标趋势
    - 分析经济政策对各项指标的影响
    - 预测经济走势和政策效果
    ## 核心功能
    1. **数据呈现**: 获取并展示来自FRED等权威机构的经济数据
    2. **数据分析**: 通过计量经济模型分析政策冲击的影响
    3. **数据预测**: 基于历史数据和模型进行未来趋势预测
    ## 数据来源
    - [FRED](https://fred.stlouisfed.org/) (Federal Reserve Economic Data)
    - 美联储官方网站
    """)


def show_data_explorer_page():
    st.header("宏观经济数据浏览器")

    # 前端配置，包含所有信息
    INDICATOR_INFO = {
        "gdp": {"name": "国内生产总值(GDP)", "unit": "十亿美元"},
        "cpiaucsl": {"name": "消费者价格指数(CPI)", "unit": "指数"},
        "fedfunds": {"name": "联邦基金利率", "unit": "百分比 (%)"},
        "unrate": {"name": "失业率", "unit": "百分比 (%)"},
        "dgs10": {"name": "美国10年期国债收益率", "unit": "百分比 (%)"}
    }

    st.sidebar.header("图表选项")

    selected_keys = st.sidebar.multiselect(
        "选择指标",
        options=list(INDICATOR_INFO.keys()),
        default=["gdp", "fedfunds"],
        format_func=lambda key: INDICATOR_INFO[key]["name"]
    )

    start_date = st.sidebar.date_input("开始日期", datetime.date(2000, 1, 1))
    end_date = st.sidebar.date_input("结束日期", datetime.date.today())

    if start_date > end_date:
        st.sidebar.error("错误：开始日期必须早于结束日期")
        return

    if not selected_keys:
        st.warning("请在左侧边栏选择至少一个经济指标。")
    else:
        try:
            @st.cache_data
            def get_fred_data_from_backend():
                response = requests.get("http://localhost:8000/data/fred")
                response.raise_for_status()
                api_response = response.json()
                df = pd.DataFrame(api_response["data"])
                df['DATE'] = pd.to_datetime(df['DATE'])
                return df.set_index('DATE')

            df_full = get_fred_data_from_backend()

            df_filtered = df_full[start_date:end_date]

            df_display = df_filtered[selected_keys]

            st.subheader("数据预览")
            st.dataframe(df_display)

            st.subheader("图表可视化")
            df_melted = df_display.reset_index().melt(
                id_vars=['DATE'],
                value_vars=selected_keys,
                var_name='series_key',
                value_name='value'
            )
            df_melted['指标名称'] = df_melted['series_key'].map(lambda k: INDICATOR_INFO[k]['name'])

            fig = px.line(df_melted, x='DATE', y='value', color='指标名称', title="经济指标趋势对比")
            fig.update_xaxes(title_text="日期")
            fig.update_yaxes(title_text="数值", tickformat=',')
            st.plotly_chart(fig, use_container_width=True)

            csv = df_display.to_csv(encoding='utf-8-sig')
            st.download_button("下载数据 (CSV)", csv, "economic_data.csv", "text/csv")

        except requests.exceptions.RequestException as e:
            st.error(f"无法连接后端。错误: {e}")
        except Exception as e:
            st.error(f"处理数据时发生错误: {e}")


def test_backend_connection():
    """测试与后端API的连接。"""
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            st.success("成功连接到后端API。")
        else:
            st.error(f"后端连接测试失败，状态码: {response.status_code}")
    except requests.exceptions.RequestException:
        st.error("无法连接到后端API，请确认服务已在 http://localhost:8000 运行。")