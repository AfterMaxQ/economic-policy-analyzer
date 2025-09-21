import datetime
from os import rename
from fastapi import FastAPI, HTTPException
import pandas_datareader.data as web
import pandas as pd

app = FastAPI(title="经济政策影响分析工具 API")

#配置
SUPPORTED_SERIES = {
    "fed_funds_rate": {
        "id": "FEDFUNDS",
        "name": "联邦基金利率"
    },
    "cpi": {
        "id": "CPIAUCSL",
        "name": "消费者价格指数(通胀)"
    },
    "treasury_10y": {
        "id": "DGS10",
        "name": "美国10年期国债收益率"
    },
    "unemployment_rate": {
        "id": "UNRATE",
        "name": "失业率"
    }
}

@app.get("/")
def read_root():
    """根路径接口，用于测试服务是否正常运行。"""
    return {"status": "ok", "message": "欢迎使用经济政策影响分析工具 API！"}


@app.get("/data/fred")
def get_fred_data():
    """
    获取FRED经济数据，并进行清洗。
    """
    try:
        start_date = datetime.datetime(2000,1,1)
        end_date = datetime.datetime.now()
        series_ids = [details['id'] for details in SUPPORTED_SERIES.values()]

        #获取FRED数据
        df_raw = web.DataReader(series_ids, 'fred', start_date, end_date)
        #数据清洗：向前填充和移除空值
        df_filled = df_raw.ffill()
        df_cleaned = df_filled.dropna()
        #重命名列，方便前端使用
        rename_map = {details["id"]:key for key, details in SUPPORTED_SERIES.items()}
        print("rename_map:\n", rename_map)
        df_cleaned = df_cleaned.rename(columns=rename_map)
        
        # 将索引转换为普通列，确保包含 'index' 列
        df_with_index = df_cleaned.reset_index()
        df_json = df_with_index.to_dict(orient='records')

        return {
            "data": df_json,
            "series_info": SUPPORTED_SERIES
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

get_fred_data()