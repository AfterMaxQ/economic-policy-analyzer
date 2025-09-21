# backend/main_api.py

import datetime
from fastapi import FastAPI, HTTPException
# --- 步骤 1: 导入 CORSMiddleware ---
from fastapi.middleware.cors import CORSMiddleware
import pandas_datareader.data as web
import pandas as pd
import numpy as np
from statsmodels.tsa.api import VAR
from transformers import pipeline
import requests
from bs4 import BeautifulSoup
import uvicorn

# --- 创建 FastAPI 应用 ---
app = FastAPI(title="经济政策影响分析工具 API")

# --- 步骤 2: 添加 CORS 中间件配置 ---
# 定义允许访问你的API的前端源
origins = [
    "http://localhost",
    "http://localhost:8501",  # Streamlit 默认端口
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许访问的源
    allow_credentials=True,  # 是否支持 cookie
    allow_methods=["*"],  # 允许所有方法 (GET, POST, etc.)
    allow_headers=["*"],  # 允许所有请求头
)


# --- 全局变量和缓存 ---
sentiment_analyzer = pipeline("sentiment-analysis", model="ProsusAI/finbert")
var_model_results = None

# --- 配置 ---
SUPPORTED_SERIES_IDS = ["FEDFUNDS", "CPILFESL"]


# --- API 端点 ---
@app.get("/")
def read_root():
    return {"status": "ok", "message": "欢迎使用经济政策影响分析工具 API！"}


@app.get("/data/fred/all")
def get_all_fred_data():
    all_series_ids = ["GDP", "CPIAUCSL", "FEDFUNDS", "UNRATE", "DGS10"]
    try:
        start_date = datetime.datetime(2000, 1, 1)
        end_date = datetime.datetime.now()
        df_raw = web.DataReader(all_series_ids, 'fred', start_date, end_date)
        df_filled = df_raw.ffill()
        df_cleaned = df_filled.dropna()
        df_cleaned.columns = [col.lower() for col in df_cleaned.columns]
        df_json = df_cleaned.reset_index().to_dict(orient='records')
        return {
            "data": df_json,
            "series_ids": [col.lower() for col in all_series_ids]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analysis/nlp")
def analyze_fomc_statement(url_item: dict):
    url = url_item.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required.")

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        article_div = soup.find('div', id='article')
        if not article_div:
            raise HTTPException(status_code=404, detail="Could not find article content on the page.")

        statement_text = article_div.get_text()
        truncated_text = statement_text[:1024]
        result = sentiment_analyzer(truncated_text)
        return {"url": url, "analysis": result}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch URL: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during analysis: {e}")


@app.post("/simulate/var_irf")
def get_var_irf(request_data: dict):
    global var_model_results

    steps = request_data.get("steps", 12)
    impulse = request_data.get("impulse", "FEDFUNDS")
    response_var = request_data.get("response", "INFLATION")
    shock_size = request_data.get("shock_size", 1.0)

    try:
        if var_model_results is None:
            print("Training VAR model for the first time...")
            start_date = datetime.datetime(2000, 1, 1)
            end_date = datetime.datetime.now()

            df = web.DataReader(SUPPORTED_SERIES_IDS, 'fred', start_date, end_date)
            df_monthly = df.ffill().resample('MS').first()

            df_monthly['INFLATION'] = np.log(df_monthly['CPILFESL']).diff() * 100
            df_monthly = df_monthly.dropna()

            model_data = df_monthly[['FEDFUNDS', 'INFLATION']]
            model = VAR(model_data)
            var_model_results = model.fit(2)
            print("VAR model trained and cached.")

        irf = var_model_results.irf(periods=steps)

        impulse_idx = var_model_results.names.index(impulse)
        response_idx = var_model_results.names.index(response_var)

        irf_values = irf.irfs[:, response_idx, impulse_idx]

        scaled_irf_values = irf_values * shock_size
        irf_data = [{"step": i, "value": val} for i, val in enumerate(scaled_irf_values)]

        return {
            "impulse": impulse,
            "response": response_var,
            "steps": steps,
            "shock_size": shock_size,
            "data": irf_data
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An error occurred during VAR simulation: {e}")


if __name__ == "__main__":
    uvicorn.run("main_api:app", host="127.0.0.1", port=8000, reload=True)