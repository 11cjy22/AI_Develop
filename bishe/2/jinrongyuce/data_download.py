import akshare as ak
import pandas as pd
import os
from datetime import datetime

# 创建数据目录
os.makedirs('data', exist_ok=True)

# 下载沪深300指数数据
def download_stock_data():
    print("开始下载沪深300指数数据...")
    stock_data = ak.stock_zh_index_daily(symbol="sh000300")
    # 筛选时间范围
    start_date = datetime.strptime('2022-01-01', '%Y-%m-%d').date()
    end_date = datetime.strptime('2025-12-31', '%Y-%m-%d').date()
    stock_data = stock_data[(stock_data['date'] >= start_date) & (stock_data['date'] <= end_date)]
    # 保存为CSV
    stock_data.to_csv('data/沪深300数据.csv', index=False, encoding='utf-8-sig')
    print(f"沪深300数据下载完成，共{len(stock_data)}条记录")
    return stock_data

# 下载黄金数据
def download_gold_data():
    print("开始下载黄金数据...")
    gold_data = ak.spot_golden_benchmark_sge()
    # 重命名列
    gold_data = gold_data.rename(columns={'交易时间': 'date'})
    # 转换日期格式
    gold_data['date'] = pd.to_datetime(gold_data['date']).dt.date
    # 筛选时间范围
    start_date = datetime.strptime('2022-01-01', '%Y-%m-%d').date()
    end_date = datetime.strptime('2025-12-31', '%Y-%m-%d').date()
    gold_data = gold_data[(gold_data['date'] >= start_date) & (gold_data['date'] <= end_date)]
    # 保存为CSV
    gold_data.to_csv('data/黄金数据.csv', index=False, encoding='utf-8-sig')
    print(f"黄金数据下载完成，共{len(gold_data)}条记录")
    return gold_data

if __name__ == "__main__":
    print("数据下载开始...")
    stock_data = download_stock_data()
    gold_data = download_gold_data()
    print("数据下载完成！")
