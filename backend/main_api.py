# backend/main_api.py

import datetime
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas_datareader.data as web
import pandas as pd
import numpy as np
from statsmodels.tsa.api import VAR
from transformers import pipeline
import requests
from bs4 import BeautifulSoup
import uvicorn
from backend.nlp_config import POLICY_DIMENSIONS # 导入我们的新配置

app = FastAPI(title="经济政策影响分析工具 API")

# --全局变量和缓存--
sentiment_analyzer = pipeline("sentiment-analysis", model="ProsusAI/finbert")
var_model_result = None
# --- 步骤 1: 创建全局变量来缓存数据 ---
fomc_analysis_df = None

# --配置--
SUPPORTED_SERIES_IDS = ["FEDFUNDS", "CPILFESL"]


# --API 端点--
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
    """
    接收URL，爬取文本，并进行多维度的政策倾向分析。
    """
    url = url_item.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required.")
    
    try:
        # 1. 爬取文本 (代码不变)
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        article_div = soup.find('div', id='article')
        if not article_div:
            raise HTTPException(status_code=404, detail="Could not find article content.")
        
        statement_text = article_div.get_text().lower() # 转换为小写，方便匹配
        
        # 2. 进行多维度分析
        analysis_results = []
        for dim_key, dim_info in POLICY_DIMENSIONS.items():
            
            # 找到与该维度相关的句子
            relevant_sentences = []
            for sentence in statement_text.split('.'): # 按句子分割
                if any(keyword in sentence for keyword in dim_info["keywords"]):
                    relevant_sentences.append(sentence)

            if not relevant_sentences:
                # 如果没有找到相关句子，则认为是中性
                score_positive = 50
            else:
                # 对所有相关句子进行情感分析
                # 我们这里使用 FinBERT，它能返回 'positive', 'negative', 'neutral'
                sentiments = sentiment_analyzer(relevant_sentences)
                
                # 3. 计算得分
                positive_score = sum(s['score'] for s in sentiments if s['label'] == 'positive')
                negative_score = sum(s['score'] for s in sentiments if s['label'] == 'negative')
                
                total_score = positive_score + negative_score
                if total_score == 0:
                    score_positive = 50 # 避免除以零
                else:
                    # 将得分转换为百分比
                    score_positive = (positive_score / total_score) * 100
            
            analysis_results.append({
                "dimension": dim_key,
                "positive_name": dim_info["positive_name"],
                "negative_name": dim_info["negative_name"],
                "positive_score_percent": round(score_positive),
                "negative_score_percent": round(100 - score_positive)
            })

        return {"url": url, "analysis": analysis_results}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


@app.post("/simulate/var_irf")
def get_var_irf(request_data: dict):
    global var_model_result

    steps = request_data.get("steps", 12)
    impulse = request_data.get("impulse", "FEDFUNDS")
    response_var = request_data.get("response", "INFLATION")
    shock_size = request_data.get("shock_size", 1.0)

    try:
        if var_model_result is None:
            print("Training VAR model for the first time...")
            start_date = datetime.datetime(2000, 1, 1)
            end_date = datetime.datetime.now()

            df = web.DataReader(SUPPORTED_SERIES_IDS, 'fred', start_date, end_date)
            df_monthly = df.ffill().resample('MS').first()

            df_monthly['INFLATION'] = np.log(df_monthly['CPILFESL']).diff() * 100
            df_monthly = df_monthly.dropna()

            model_data = df_monthly[['FEDFUNDS', 'INFLATION']]
            model = VAR(model_data)
            var_model_result = model.fit(2)
            print("VAR model trained and cached.")

        irf = var_model_result.irf(periods=steps)

        impulse_idx = var_model_result.names.index(impulse)
        response_idx = var_model_result.names.index(response_var)

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


# --- 步骤 2: 使用 FastAPI 的启动事件来加载数据 ---
@app.on_event("startup")
def load_data_on_startup():
    """
    在 FastAPI 服务器启动时，执行此函数一次，将数据加载到内存中。
    """
    global fomc_analysis_df
    
    analysis_file_path = os.path.join("data", "fomc_analysis.csv")
    print(f"服务器启动：正在从 '{analysis_file_path}' 加载分析数据...")
    
    if not os.path.exists(analysis_file_path):
        print(f"警告：分析文件 '{analysis_file_path}' 未找到。历史数据接口将不可用。")
        # 创建一个空的 DataFrame，以避免后续代码出错
        fomc_analysis_df = pd.DataFrame() 
    else:
        fomc_analysis_df = pd.read_csv(analysis_file_path)
        print("分析数据加载成功，已缓存到内存。")


# --- 步骤 3: 修改 API 接口，让它从缓存中读取数据 ---
@app.get("/analysis/fomc/history")
def get_fomc_analysis_history():
    """
    从内存缓存中直接读取并返回所有 FOMC 会议的历史分析数据。
    """
    global fomc_analysis_df
    
    if fomc_analysis_df is None or fomc_analysis_df.empty:
        raise HTTPException(
            status_code=404, 
            detail="分析数据尚未加载或文件为空。请检查服务器启动日志。"
        )
    
    # 直接从内存中的 DataFrame 转换，速度极快
    results = fomc_analysis_df.to_dict(orient='records')
    return {"data": results}


@app.post("/analysis/nlp/realtime") # 使用新的、更明确的路径
def analyze_single_fomc_statement(url_item: dict):
    """
    接收一个包含单个FOMC声明URL的请求，实时爬取文本并进行多维度的政策倾向分析。
    """
    url = url_item.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required.")
    
    try:
        # 1. 爬取文本
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        article_div = soup.find('div', id='article')
        if not article_div:
            raise HTTPException(status_code=404, detail="Could not find article content on the page.")
        
        statement_text = article_div.get_text().lower()
        
        # 2. 进行多维度分析 (逻辑与脚本中的一致)
        analysis_results = []
        for dim_key, dim_info in POLICY_DIMENSIONS.items():
            relevant_sentences = []
            for sentence in statement_text.split('.'):
                if any(keyword in sentence for keyword in dim_info["keywords"]):
                    relevant_sentences.append(sentence)

            if not relevant_sentences:
                score_positive = 50
            else:
                sentiments = sentiment_analyzer(relevant_sentences)
                positive_score = sum(s['score'] for s in sentiments if s['label'] == 'positive')
                negative_score = sum(s['score'] for s in sentiments if s['label'] == 'negative')
                total_score = positive_score + negative_score
                score_positive = (positive_score / total_score) * 100 if total_score > 0 else 50
            
            analysis_results.append({
                "dimension": dim_key,
                "positive_name": dim_info["positive_name"],
                "negative_name": dim_info["negative_name"],
                "positive_score_percent": round(score_positive),
                "negative_score_percent": round(100 - score_positive)
            })

        return {"url": url, "analysis": analysis_results}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An error occurred during real-time analysis: {e}")


if __name__ == "__main__":
    uvicorn.run("main_api:app", host="127.0.0.1", port=8000, reload=True)