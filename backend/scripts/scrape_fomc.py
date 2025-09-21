# backend/scripts/scrape_fomc.py

from FedTools import MonetaryPolicyCommittee
import os
import pandas as pd
from transformers import pipeline
# 确保我们的配置文件可以被导入
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.nlp_config import POLICY_DIMENSIONS

# --- 配置 ---
RAW_DATA_FILE = os.path.join("../../data", "fomc_statements_raw.csv")
ANALYSIS_OUTPUT_FILE = os.path.join("../../data", "fomc_analysis.csv")


def fetch_and_save_raw_data():
    """
    使用 FedTools 获取原始声明数据并保存。
    此版本确保返回的 DataFrame 列名是统一的。
    """
    print("步骤 1/2: 使用 FedTools 获取所有FOMC会议声明...")

    if os.path.exists(RAW_DATA_FILE):
        print(f"原始数据文件 '{RAW_DATA_FILE}' 已存在，直接读取。")
        df = pd.read_csv(RAW_DATA_FILE)
    else:
        fomc = MonetaryPolicyCommittee(start_year=2000)
        df = fomc.find_statements()
        df = df.reset_index()
        os.makedirs(os.path.dirname(RAW_DATA_FILE), exist_ok=True)
        # 保存前不重命名，保持原始列名
        df.to_csv(RAW_DATA_FILE, index=False, encoding='utf-8-sig')
        print(f"爬取完成！原始数据已保存到: {RAW_DATA_FILE}")

    # --- 解决方案：统一在这里进行重命名 ---
    # 无论数据是新爬取的还是从文件读取的，都在这里确保列名正确
    if 'index' in df.columns:
        df = df.rename(columns={'index': 'date'})
    if 'FOMC_Statements' in df.columns:
        df = df.rename(columns={'FOMC_Statements': 'statement_text'})
    elif 'statements' in df.columns:
        df = df.rename(columns={'statements': 'statement_text'})

    # 确保关键列存在
    if 'date' not in df.columns or 'statement_text' not in df.columns:
        raise ValueError("无法在原始数据中找到 'date' 或 'statement_text' 列。")

    print(f"总共获取了 {len(df)} 条声明。")
    return df


def analyze_statements(df):
    """
    对包含声明文本的 DataFrame 进行多维度情感分析。
    (此函数保持上次修改后的版本，无需改动)
    """
    print("\n步骤 2/2: 正在加载NLP模型并进行多维度情感分析...")

    sentiment_analyzer = pipeline("sentiment-analysis", model="ProsusAI/finbert")

    analysis_records = []

    if 'statement_text' not in df.columns:
        raise ValueError("传入的 DataFrame 中缺少 'statement_text' 列。")

    for row in df.itertuples(index=False, name=None):
        row_dict = dict(zip(df.columns, row))
        statement_text = str(row_dict.get('statement_text', '')).lower()
        date = row_dict.get('date')

        if not statement_text: continue

        print(f"  - 正在分析 {date} 的声明...")

        record = {"date": date}
        for dim_key, dim_info in POLICY_DIMENSIONS.items():
            relevant_sentences = [s for s in statement_text.split('.') if
                                  any(keyword in s for keyword in dim_info["keywords"])]
            if not relevant_sentences:
                score_positive = 50
            else:
                relevant_sentences = relevant_sentences[:20]
                relevant_sentences = [s[:512] for s in relevant_sentences]
                sentiments = sentiment_analyzer(relevant_sentences)
                positive_score = sum(s['score'] for s in sentiments if s['label'] == 'positive')
                negative_score = sum(s['score'] for s in sentiments if s['label'] == 'negative')
                total_score = positive_score + negative_score
                score_positive = (positive_score / total_score) * 100 if total_score > 0 else 50
            record[f"{dim_key}_positive_score"] = round(score_positive)
        analysis_records.append(record)

    return pd.DataFrame(analysis_records)


def main():
    """
    主函数，执行数据获取和分析的完整流程。
    """
    # 步骤 1: 获取原始数据，现在返回的 raw_df 列名已经是统一的了
    raw_df = fetch_and_save_raw_data()

    # 步骤 2: 对原始数据进行分析
    analysis_df = analyze_statements(raw_df)

    # --- 解决方案：这里的 raw_df 已经包含了正确的列名 ---
    # 现在这行代码可以正常工作了
    final_df = pd.merge(raw_df[['date', 'statement_text']], analysis_df, on='date')

    # 保存最终的分析结果
    final_df.to_csv(ANALYSIS_OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print(f"\n分析完成！所有结果已保存到: {ANALYSIS_OUTPUT_FILE}")
    print("最终数据预览:")
    print(final_df.head())


if __name__ == "__main__":
    main()