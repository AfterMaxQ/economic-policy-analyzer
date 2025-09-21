# frontend/app.py
import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# 应用标题和基本信息
st.title("经济政策影响分析工具")
st.sidebar.header("导航")

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

# 获取经济数据
st.header("宏观经济指标可视化")

if st.button("获取FRED经济数据"):
    try:
        with st.spinner("正在获取数据..."):
            response = requests.get("http://localhost:8000/data/fred")

            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data["data"])
                series_info = data["series_info"]

                # 显示数据信息
                st.subheader("获取的指标信息")
                st.json(series_info)

                # 选择要可视化的指标
                selected_series = st.selectbox(
                    "选择一个经济指标进行可视化",
                    list(series_info.keys()),
                    format_func=lambda x: f"{series_info[x]['name']} ({x})"
                )

                # 绘制图表
                if selected_series in df.columns:
                    df['index'] = pd.to_datetime(df['index'])
                    fig = px.line(df, x='index', y=selected_series,
                                  title=f"{series_info[selected_series]['name']} 趋势图")
                    fig.update_xaxes(title_text="日期")
                    fig.update_yaxes(title_text=series_info[selected_series]['name'])
                    st.plotly_chart(fig, use_container_width=True)

                # 显示原始数据
                st.subheader("原始数据")
                st.dataframe(df)
            else:
                st.error(f"获取数据失败: {response.status_code}")

    except requests.exceptions.RequestException as e:
        st.error(f"请求失败: {e}")
    except Exception as e:
        st.error(f"处理数据时出错: {e}")
