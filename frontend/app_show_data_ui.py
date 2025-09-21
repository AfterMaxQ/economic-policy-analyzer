import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import datetime
import numpy as np


def show_home_page():
    """
    显示项目主页，介绍项目功能和目的
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


def show_fred_data():
    """
    显示FRED经济数据获取和可视化功能，支持动态日期范围和指标选择，并提供CSV下载
    """
    st.header("宏观经济指标表格查看与下载")

    # 指标映射：英文键名 -> 中文显示名（与后端SUPPORTED_SERIES保持一致）
    SERIES_MAPPING = {
        "fed_funds_rate": "联邦基金利率",
        "cpi": "消费者价格指数(CPI)",
        "treasury_10y": "美国10年期国债收益率",
        "unemployment_rate": "失业率"
    }

    # 指标选择器 - 支持多选
    selected_series_keys = st.multiselect(
        "选择经济指标",
        list(SERIES_MAPPING.keys()),
        default=["cpi", "unemployment_rate"],
        format_func=lambda x: SERIES_MAPPING[x]
    )

    # 日期范围选择器，添加唯一key避免ID冲突
    start_date = st.date_input("开始日期", datetime.date(2000, 1, 1), key="fred_start_date")
    end_date = st.date_input("结束日期", datetime.date.today(), key="fred_end_date")

    # 确保开始日期早于结束日期
    if start_date > end_date:
        st.error("错误：开始日期必须早于结束日期")

    # 获取数据按钮
    if st.button("获取并显示数据"):
        if not selected_series_keys:
            st.warning("请选择至少一个经济指标")
        elif start_date > end_date:
            st.error("错误：开始日期必须早于结束日期")
        else:
            try:
                with st.spinner("正在获取数据..."):
                    response = requests.get("http://localhost:8000/data/fred")

                    if response.status_code == 200:
                        data = response.json()
                        df = pd.DataFrame(data["data"])

                        # --- MODIFICATION 1: Validate for 'DATE' column ---
                        if 'DATE' not in df.columns:
                            st.error("数据格式错误：缺少 'DATE' 列")
                            return

                        # --- MODIFICATION 2: Convert 'DATE' column ---
                        df['DATE'] = pd.to_datetime(df['DATE'])

                        # --- MODIFICATION 3: Filter based on 'DATE' column ---
                        mask = (df['DATE'] >= pd.to_datetime(start_date)) & (df['DATE'] <= pd.to_datetime(end_date))
                        df = df.loc[mask]

                        # 如果没有数据，给出提示
                        if df.empty:
                            st.warning("所选日期范围内无数据")
                            return

                        # --- MODIFICATION 4: Keep 'DATE' column and selected series ---
                        columns_to_keep = ['DATE'] + selected_series_keys
                        df = df[columns_to_keep]

                        # 显示数据表格
                        st.subheader("经济指标数据")
                        st.dataframe(df)

                        # 绘制图表
                        if not df.empty:
                            # --- MODIFICATION 5: Melt data using 'DATE' as id_vars ---
                            df_melted = df.melt(id_vars=['DATE'], value_vars=selected_series_keys,
                                              var_name='series', value_name='value')

                            # 使用中文标签替换变量名
                            df_melted['series'] = df_melted['series'].map(SERIES_MAPPING)

                            # --- MODIFICATION 6: Plot using 'DATE' as the x-axis ---
                            fig = px.line(df_melted, x='DATE', y='value', color='series',
                                        title="经济指标趋势图")
                            fig.update_xaxes(title_text="日期")
                            fig.update_yaxes(title_text="数值")
                            st.plotly_chart(fig, use_container_width=True)

                        # 提供CSV下载功能
                        csv = df.to_csv(index=False, encoding='utf-8-sig')
                        st.download_button(
                            label="下载CSV文件",
                            data=csv,
                            file_name="fred_economic_data.csv",
                            mime="text/csv"
                        )
                    else:
                        st.error(f"获取数据失败: {response.status_code}")

            except requests.exceptions.RequestException as e:
                st.error(f"请求失败: {e}")
            except Exception as e:
                st.error(f"处理数据时出错: {e}")


def show_notebook_data():
    """
    显示模拟的notebook数据可视化功能
    """
    st.header("美国宏观经济指标动态折线图")

    # 读取notebook 01中的数据（模拟）
    # 这里我们模拟从notebook获取的数据
    notebook_data_info = {
        "gdp": "国内生产总值(GDP)",
        "inflation": "通胀率",
        "employment": "就业率",
        "consumer_spending": "消费者支出"
    }

    # 创建选择框让用户选择指标
    selected_notebook_series = st.selectbox(
        "选择一个宏观经济指标",
        list(notebook_data_info.keys()),
        format_func=lambda x: notebook_data_info[x]
    )

    # 添加日期范围选择器，使用唯一key避免ID冲突
    start_date = st.date_input("开始日期", datetime.date(2000, 1, 1), key="notebook_start_date")
    end_date = st.date_input("结束日期", datetime.date.today(), key="notebook_end_date")

    # 确保开始日期早于结束日期
    if start_date > end_date:
        st.error("错误：开始日期必须早于结束日期")
    else:
        # 模拟从notebook获取数据并绘图
        # 在实际应用中，这里应该从notebook 01中读取真实数据
        if st.button("显示指标趋势图"):
            # 模拟数据
            # 根据选择的日期范围生成数据
            date_range = pd.date_range(start_date, end_date, freq='M')
            periods = len(date_range) if len(date_range) > 0 else 100
            values = np.cumsum(np.random.randn(periods)) + 100

            # 创建数据框
            chart_data = pd.DataFrame({
                'date': date_range[:periods],
                'value': values
            })

            # 绘制图表
            fig = px.line(chart_data, x='date', y='value',
                          title=f'{notebook_data_info[selected_notebook_series]} 趋势图')
            fig.update_xaxes(title_text="日期")
            fig.update_yaxes(title_text="数值")
            st.plotly_chart(fig, use_container_width=True)


def show_indicator_data():
    """
    显示宏观经济指标动态分析功能，并根据所选指标动态更新Y轴单位。
    """
    st.header("宏观经济指标动态分析")

    # --- 步骤 1: 丰富指标信息，增加 'unit' 字段 ---
    indicator_info = {
        "gdp": {
            "name": "国内生产总值(GDP)",
            "unit": "十亿美元"
        },
        "inflation": {
            "name": "通胀率",
            "unit": "百分比 (%)"
        },
        "employment": {
            "name": "就业率",
            "unit": "百分比 (%)"
        },
        "consumer_spending": {
            "name": "消费者支出",
            "unit": "十亿美元"
        }
    }

    # 创建选择框让用户选择指标 (key)
    # format_func 用于在下拉菜单中显示中文名
    selected_series_key = st.selectbox(
        "选择一个宏观经济指标",
        list(indicator_info.keys()),
        format_func=lambda key: indicator_info[key]["name"]
    )

    # 获取选中指标的完整信息
    selected_indicator_details = indicator_info[selected_series_key]

    # 添加日期范围选择器，使用唯一key避免ID冲突
    start_date = st.date_input("开始日期", datetime.date(2000, 1, 1), key="indicator_start_date")
    end_date = st.date_input("结束日期", datetime.date.today(), key="indicator_end_date")

    # 确保开始日期早于结束日期
    if start_date > end_date:
        st.error("错误：开始日期必须早于结束日期")
    else:
        # 在实际应用中，这里应该从真实数据源读取数据
        if st.button("显示指标趋势图", key="indicator_button"):  # 给按钮也加一个key
            # 模拟数据
            date_range = pd.date_range(start_date, end_date, freq='M')
            periods = len(date_range) if len(date_range) > 0 else 100

            # 根据单位模拟不同尺度的数据
            if selected_indicator_details["unit"] == "十亿美元":
                values = np.cumsum(np.random.randn(periods)) + 15000  # GDP/支出的量级
            else:
                values = np.cumsum(np.random.randn(periods) * 0.1) + 5  # 利率/失业率的量级

            chart_data = pd.DataFrame({
                'date': date_range[:periods],
                'value': values
            })

            # --- 步骤 2: 动态更新图表标题和Y轴标签 ---
            fig = px.line(
                chart_data,
                x='date',
                y='value',
                title=f'{selected_indicator_details["name"]} 趋势图'
            )
            fig.update_xaxes(title_text="日期")
            # 从字典中读取单位并设置为Y轴标题
            fig.update_yaxes(title_text=selected_indicator_details["unit"])

            st.plotly_chart(fig, use_container_width=True)


def test_backend_connection():
    """
    测试与后端API的连接
    """

    # 测试后端连接
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            st.success("成功连接到后端API")
            st.json(response.json())
        else:
            st.error(f"后端返回状态码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"无法连接到后端: {e}")