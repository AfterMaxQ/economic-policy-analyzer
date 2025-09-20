from fastapi import FastAPI

app = FastAPI(title="经济政策影响分析工具")

@app.get("/")
def read_root():
    """
    这是一个根路径接口，用于测试服务是否正常运行。
    """
    return {"status": "ok", "message": "欢迎使用经济政策影响分析工具 API！"}

