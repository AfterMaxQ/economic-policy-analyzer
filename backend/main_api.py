# backend/main_api.py

import datetime
from fastapi import FastAPI, HTTPException
import pandas_datareader.data as web
import pandas as pd

app = FastAPI(title="经济政策影响分析工具 API")

# 配置，现在只包含FRED ID
SUPPORTED_SERIES_IDS = [
    "GDP",
    "CPIAUCSL",
    "FEDFUNDS",
    "UNRATE",
    "DGS10"
]


@app.get("/")
def read_root():
    """根路径接口，用于测试服务是否正常运行。"""
    return {"status": "ok", "message": "欢迎使用经济政策影响分析工具 API！"}


@app.get("/data/fred")
def get_fred_data():
    """
    获取所有预定义的 FRED 经济数据，并进行清洗。
    """
    try:
        start_date = datetime.datetime(2000, 1, 1)
        end_date = datetime.datetime.now()

        # 获取FRED数据
        df_raw = web.DataReader(SUPPORTED_SERIES_IDS, 'fred', start_date, end_date)
        # 数据清洗：向前填充和移除空值
        df_filled = df_raw.ffill()
        df_cleaned = df_filled.dropna()

        # --- 修改：将列名统一转换为小写，作为JSON的key ---
        df_cleaned.columns = [col.lower() for col in df_cleaned.columns]

        df_json = df_cleaned.reset_index().to_dict(orient='records')

        return {
            "data": df_json,
            "series_ids": [col.lower() for col in SUPPORTED_SERIES_IDS]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))