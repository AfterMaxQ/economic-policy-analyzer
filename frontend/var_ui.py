# frontend/var_ui.py

import streamlit as st
import requests
import pandas as pd
import plotly.express as px


def show_var_simulation_page():
    st.markdown("此模块基于VAR模型，模拟一项政策冲击（如加息）对其他经济变量的动态影响。")
    st.info("注意：当前模型仅包含利率和通胀，结果可能存在'价格之谜'现象，仅供演示。")

    # 模拟参数（未来可以做成可选项）
    impulse_var = "FEDFUNDS"
    response_var = "INFLATION"
    steps = 12

    if st.button(f"模拟 {impulse_var} 冲击对 {response_var} 的影响"):
        with st.spinner("正在训练模型并进行模拟..."):
            try:
                # 调用后端API
                api_url = "http://localhost:8000/simulate/var_irf"
                payload = {
                    "impulse": impulse_var,
                    "response": response_var,
                    "steps": steps
                }
                response = requests.post(api_url, json=payload)

                if response.status_code == 200:
                    st.success("模拟成功！")
                    result = response.json()
                    df_irf = pd.DataFrame(result['data'])

                    # 绘制图表
                    fig = px.line(
                        df_irf,
                        x='step',
                        y='value',
                        title=f"脉冲响应: {result['impulse']} → {result['response']}",
                        labels={"step": "冲击后的月份", "value": "响应值"}
                    )
                    fig.add_hline(y=0, line_dash="dash", line_color="grey")
                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(df_irf)
                else:
                    st.error(f"模拟失败: {response.json().get('detail', '未知错误')}")

            except requests.exceptions.RequestException as e:
                st.error(f"无法连接到后端服务: {e}")