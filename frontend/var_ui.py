# frontend/var_ui.py

import streamlit as st
import requests
import pandas as pd
import plotly.express as px


def show_var_simulation_page():
    st.markdown("此模块基于VAR模型，模拟一项政策冲击（如加息）对其他经济变量的动态影响。")
    st.info("注意：当前模型仅包含利率和通胀，结果可能存在'价格之谜'现象，仅供演示。")

    var_options = {
        "FEDFUNDS": "联邦基金利率",
        "INFLATION": "通胀率"
    }

    st.subheader("模拟参数设置")

    col1, col2 = st.columns(2)

    with col1:
        impulse_var = st.selectbox(
            "选择施加冲击的变量 (Impulse):",
            options=list(var_options.keys()),
            format_func=lambda key: var_options[key]
        )

    with col2:
        response_var = st.selectbox(
            "选择观察响应的变量 (Response):",
            options=list(var_options.keys()),
            format_func=lambda key: var_options[key],
            index=1
        )

    # --- 步骤 3: 添加 st.slider 来选择冲击大小 ---
    shock_size = st.slider(
        "选择冲击的大小 (百分点):",
        min_value=-1.0,
        max_value=1.0,
        value=0.25,  # 默认值为 +0.25 (模拟加息25个基点)
        step=0.05  # 每次调整的步长
    )

    steps = 12

    if st.button(f"模拟 {var_options[impulse_var]} ({shock_size:+.2f}%) 冲击对 {var_options[response_var]} 的影响"):
        with st.spinner("正在训练模型并进行模拟..."):
            try:
                api_url = "http://localhost:8000/simulate/var_irf"

                # --- 将 shock_size 添加到发送给后端的 payload 中 ---
                payload = {
                    "impulse": impulse_var,
                    "response": response_var,
                    "steps": steps,
                    "shock_size": shock_size  # 新增参数
                }
                response = requests.post(api_url, json=payload)

                if response.status_code == 200:
                    st.success("模拟成功！")
                    result = response.json()
                    df_irf = pd.DataFrame(result['data'])

                    impulse_name = var_options.get(result['impulse'], result['impulse'])
                    response_name = var_options.get(result['response'], result['response'])

                    chart_title = f"脉冲响应: {impulse_name} ({result['shock_size']:+.2f}%) 的一次冲击对 {response_name} 的影响"

                    fig = px.line(
                        df_irf,
                        x='step',
                        y='value',
                        title=chart_title,
                        labels={
                            "step": "冲击后的月份",
                            "value": f"{response_name} 的响应值 (百分点变化)"
                        }
                    )
                    fig.add_hline(y=0, line_dash="dash", line_color="grey")
                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(df_irf)
                else:
                    st.error(f"模拟失败: {response.json().get('detail', '未知错误')}")

            except requests.exceptions.RequestException as e:
                st.error(f"无法连接到后端服务: {e}")