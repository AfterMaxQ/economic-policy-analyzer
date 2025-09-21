# Economic Policy Impact Analyzer

经济政策影响分析工具 - 一个全栈Web应用，用于可视化、分析和模拟宏观经济政策对各项经济指标的影响。

## 项目概述

本项目是一个综合性的经济政策影响分析平台，旨在帮助用户：
- 可视化宏观经济指标趋势
- 分析经济政策对各项指标的影响
- 预测经济走势和政策效果

### 核心功能

1. **数据呈现**: 获取并展示来自FRED等权威机构的经济数据
2. **数据分析**: 通过计量经济模型分析政策冲击的影响
3. **数据预测**: 基于历史数据和模型进行未来趋势预测

## 技术栈

- **后端框架**: FastAPI
- **前端框架**: Streamlit
- **数据处理**: pandas
- **数据获取**: pandas-datareader (FRED), requests
- **可视化**: plotly
- **计量经济模型**: statsmodels (VAR等)
- **NLP与文本分析**: transformers, beautifulsoup4

## 项目结构
economic-policy-analyzer/ ├── backend/ # 后端API服务 │ ├── init.py │ └── main_api.py # FastAPI应用主入口 ├── frontend/ # 前端应用 │ ├── init.py │ ├── app.py # Streamlit应用主入口 │ └── app_show_data_ui.py # UI组件模块 ├── notebooks/ # Jupyter notebooks用于探索性分析 │ ├── 01-data-exploration.ipynb │ ├── 02-nlp-poc.ipynb │ └── 03-var-model-poc.ipynb ├── logs/ # 日志文件目录 ├── requirements.txt # 项目依赖 ├── project_requirements.json # 项目需求文档 ├── logger_setup.py # 日志配置模块 ├── git_commands.json # Git命令速查 └── README.md # 项目说明文档