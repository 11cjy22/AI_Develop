import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import os

# 计算MACD
def calculate_macd(data, close_col, fast_period=12, slow_period=26, signal_period=9):
    # 计算短期EMA
    data['EMA12'] = data[close_col].ewm(span=fast_period, adjust=False).mean()
    # 计算长期EMA
    data['EMA26'] = data[close_col].ewm(span=slow_period, adjust=False).mean()
    # 计算DIFF
    data['MACD_diff'] = data['EMA12'] - data['EMA26']
    # 计算DEA
    data['MACD_dea'] = data['MACD_diff'].ewm(span=signal_period, adjust=False).mean()
    # 计算MACD柱状图
    data['MACD_hist'] = 2 * (data['MACD_diff'] - data['MACD_dea'])
    return data

# 计算KDJ
def calculate_kdj(data, high_col, low_col, close_col, n=9):
    # 计算RSV
    data['RSV'] = (data[close_col] - data[low_col].rolling(window=n).min()) / \
                  (data[high_col].rolling(window=n).max() - data[low_col].rolling(window=n).min()) * 100
    # 计算K值
    data['KDJ_K'] = data['RSV'].ewm(alpha=1/3, adjust=False).mean()
    # 计算D值
    data['KDJ_D'] = data['KDJ_K'].ewm(alpha=1/3, adjust=False).mean()
    # 计算J值
    data['KDJ_J'] = 3 * data['KDJ_K'] - 2 * data['KDJ_D']
    return data

# 计算RSI
def calculate_rsi(data, close_col, period=14):
    delta = data[close_col].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    return data

# 计算BOLL布林带
def calculate_bollinger_bands(data, close_col, window=20):
    data['MA20'] = data[close_col].rolling(window=window).mean()
    data['STD20'] = data[close_col].rolling(window=window).std()
    data['BOLL_upper'] = data['MA20'] + 2 * data['STD20']
    data['BOLL_middle'] = data['MA20']
    data['BOLL_lower'] = data['MA20'] - 2 * data['STD20']
    return data

# 处理极端值
def handle_outliers(data, columns):
    for col in columns:
        if col in data.columns:
            Q1 = data[col].quantile(0.25)
            Q3 = data[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            data[col] = data[col].clip(lower=lower_bound, upper=upper_bound)
    return data

# 读取数据
def load_data():
    stock_data = pd.read_csv('data/沪深300数据.csv')
    gold_data = pd.read_csv('data/黄金数据.csv')
    return stock_data, gold_data

# 处理股票数据
def process_stock_data():
    print("开始处理股票数据...")
    stock_data, gold_data = load_data()
    
    # 确保日期格式正确
    stock_data['date'] = pd.to_datetime(stock_data['date'])
    
    # 重命名列
    stock_data = stock_data.rename(columns={
        'open': 'open_stock',
        'close': 'close_stock',
        'high': 'high_stock',
        'low': 'low_stock'
    })
    
    # 处理极端值
    price_columns = ['open_stock', 'close_stock', 'high_stock', 'low_stock']
    stock_data = handle_outliers(stock_data, price_columns)
    
    # 计算金融专业特征
    stock_data = calculate_macd(stock_data, 'close_stock')
    stock_data = calculate_kdj(stock_data, 'high_stock', 'low_stock', 'close_stock')
    stock_data = calculate_rsi(stock_data, 'close_stock')
    stock_data = calculate_bollinger_bands(stock_data, 'close_stock')
    
    # 计算5日均线
    stock_data['MA5_stock'] = stock_data['close_stock'].rolling(window=5).mean()
    
    # 计算20日波动率
    stock_data['volatility'] = stock_data['close_stock'].rolling(window=20).std()
    
    # 计算收益率
    stock_data['return'] = stock_data['close_stock'].pct_change()
    
    # 构建标签：次日涨跌（二分类）
    stock_data['next_day_return'] = (stock_data['close_stock'].shift(-1) - stock_data['close_stock']) / stock_data['close_stock']
    stock_data['label'] = (stock_data['next_day_return'] > 0).astype(int)  # 1表示涨，0表示跌
    
    # 删除缺失值
    stock_data = stock_data.dropna()
    print(f"股票数据删除缺失值后共{len(stock_data)}条记录")
    
    # 选择需要的特征列
    features = ['close_stock', 'open_stock', 'high_stock', 'low_stock',
                'MA5_stock', 'volatility', 'return',
                'MACD_diff', 'MACD_dea', 'MACD_hist',
                'KDJ_K', 'KDJ_D', 'KDJ_J',
                'RSI',
                'BOLL_upper', 'BOLL_middle', 'BOLL_lower']
    
    # 标准化（使用StandardScaler，更适合金融数据）
    scaler = StandardScaler()
    stock_data[features] = scaler.fit_transform(stock_data[features])
    
    # 保存最终数据
    stock_data.to_csv('data/股票数据_处理后.csv', index=False, encoding='utf-8-sig')
    print("股票数据处理完成，保存为 'data/股票数据_处理后.csv'")
    
    # 保存scaler用于预测
    import joblib
    os.makedirs('models', exist_ok=True)
    joblib.dump(scaler, 'models/stock_scaler.pkl')
    
    return stock_data

# 处理黄金数据
def process_gold_data():
    print("开始处理黄金数据...")
    stock_data, gold_data = load_data()
    
    # 确保日期格式正确
    gold_data['date'] = pd.to_datetime(gold_data['date'])
    
    # 重命名列
    gold_data = gold_data.rename(columns={
        '早盘价': 'open_gold',
        '晚盘价': 'close_gold'
    })
    
    # 计算黄金的最高价和最低价
    gold_data['high_gold'] = gold_data[['open_gold', 'close_gold']].max(axis=1)
    gold_data['low_gold'] = gold_data[['open_gold', 'close_gold']].min(axis=1)
    
    # 处理极端值
    price_columns = ['open_gold', 'close_gold', 'high_gold', 'low_gold']
    gold_data = handle_outliers(gold_data, price_columns)
    
    # 计算金融专业特征
    gold_data = calculate_macd(gold_data, 'close_gold')
    gold_data = calculate_kdj(gold_data, 'high_gold', 'low_gold', 'close_gold')
    gold_data = calculate_rsi(gold_data, 'close_gold')
    gold_data = calculate_bollinger_bands(gold_data, 'close_gold')
    
    # 计算5日均线
    gold_data['MA5_gold'] = gold_data['close_gold'].rolling(window=5).mean()
    
    # 计算20日波动率
    gold_data['volatility_gold'] = gold_data['close_gold'].rolling(window=20).std()
    
    # 计算收益率
    gold_data['return_gold'] = gold_data['close_gold'].pct_change()
    
    # 构建标签：次日涨跌（二分类）
    gold_data['next_day_return'] = (gold_data['close_gold'].shift(-1) - gold_data['close_gold']) / gold_data['close_gold']
    gold_data['label'] = (gold_data['next_day_return'] > 0).astype(int)  # 1表示涨，0表示跌
    
    # 删除缺失值
    gold_data = gold_data.dropna()
    print(f"黄金数据删除缺失值后共{len(gold_data)}条记录")
    
    # 选择需要的特征列
    features = ['close_gold', 'open_gold', 'high_gold', 'low_gold',
                'MA5_gold', 'volatility_gold', 'return_gold',
                'MACD_diff', 'MACD_dea', 'MACD_hist',
                'KDJ_K', 'KDJ_D', 'KDJ_J',
                'RSI',
                'BOLL_upper', 'BOLL_middle', 'BOLL_lower']
    
    # 标准化（使用StandardScaler，更适合金融数据）
    scaler = StandardScaler()
    gold_data[features] = scaler.fit_transform(gold_data[features])
    
    # 保存最终数据
    gold_data.to_csv('data/黄金数据_处理后.csv', index=False, encoding='utf-8-sig')
    print("黄金数据处理完成，保存为 'data/黄金数据_处理后.csv'")
    
    # 保存scaler用于预测
    import joblib
    os.makedirs('models', exist_ok=True)
    joblib.dump(scaler, 'models/gold_scaler.pkl')
    
    return gold_data

# 数据对齐与处理（股票+黄金联合数据）
def process_combined_data():
    print("开始处理联合数据...")
    stock_data, gold_data = load_data()
    
    # 确保日期格式正确
    stock_data['date'] = pd.to_datetime(stock_data['date'])
    gold_data['date'] = pd.to_datetime(gold_data['date'])
    
    # 按日期对齐
    merged_data = pd.merge(stock_data, gold_data, on='date', how='inner')
    print(f"数据对齐后共{len(merged_data)}条记录")
    
    # 重命名列并处理黄金数据
    merged_data = merged_data.rename(columns={
        'open': 'open_stock',
        'close': 'close_stock',
        'high': 'high_stock',
        'low': 'low_stock',
        '早盘价': 'open_gold',
        '晚盘价': 'close_gold'
    })
    
    # 计算黄金的最高价和最低价
    merged_data['high_gold'] = merged_data[['open_gold', 'close_gold']].max(axis=1)
    merged_data['low_gold'] = merged_data[['open_gold', 'close_gold']].min(axis=1)
    
    # 处理极端值
    price_columns = ['open_stock', 'close_stock', 'high_stock', 'low_stock',
                     'open_gold', 'close_gold', 'high_gold', 'low_gold']
    merged_data = handle_outliers(merged_data, price_columns)
    
    # 计算股票的金融专业特征
    merged_data = calculate_macd(merged_data, 'close_stock')
    merged_data = calculate_kdj(merged_data, 'high_stock', 'low_stock', 'close_stock')
    merged_data = calculate_rsi(merged_data, 'close_stock')
    merged_data = calculate_bollinger_bands(merged_data, 'close_stock')
    
    # 计算黄金的金融专业特征
    merged_data = calculate_macd(merged_data, 'close_gold')
    merged_data = calculate_kdj(merged_data, 'high_gold', 'low_gold', 'close_gold')
    merged_data = calculate_rsi(merged_data, 'close_gold')
    merged_data = calculate_bollinger_bands(merged_data, 'close_gold')
    
    # 计算5日均线
    merged_data['MA5_stock'] = merged_data['close_stock'].rolling(window=5).mean()
    merged_data['MA5_gold'] = merged_data['close_gold'].rolling(window=5).mean()
    
    # 计算20日波动率
    merged_data['volatility_stock'] = merged_data['close_stock'].rolling(window=20).std()
    merged_data['volatility_gold'] = merged_data['close_gold'].rolling(window=20).std()
    
    # 计算收益率
    merged_data['return_stock'] = merged_data['close_stock'].pct_change()
    merged_data['return_gold'] = merged_data['close_gold'].pct_change()
    
    # 构建标签：次日涨跌（二分类）
    merged_data['next_day_return'] = (merged_data['close_stock'].shift(-1) - merged_data['close_stock']) / merged_data['close_stock']
    merged_data['label'] = (merged_data['next_day_return'] > 0).astype(int)  # 1表示涨，0表示跌
    
    # 删除缺失值
    merged_data = merged_data.dropna()
    print(f"删除缺失值后共{len(merged_data)}条记录")
    
    # 选择需要的特征列
    features = ['close_stock', 'open_stock', 'high_stock', 'low_stock',
                'close_gold', 'open_gold', 'high_gold', 'low_gold',
                'MA5_stock', 'volatility_stock', 'return_stock',
                'MA5_gold', 'volatility_gold', 'return_gold',
                'MACD_diff', 'MACD_dea', 'MACD_hist',
                'KDJ_K', 'KDJ_D', 'KDJ_J',
                'RSI',
                'BOLL_upper', 'BOLL_middle', 'BOLL_lower']
    
    # 标准化（使用StandardScaler，更适合金融数据）
    scaler = StandardScaler()
    merged_data[features] = scaler.fit_transform(merged_data[features])
    
    # 保存最终数据
    merged_data.to_csv('data/合成后数据.csv', index=False, encoding='utf-8-sig')
    print("联合数据处理完成，保存为 'data/合成后数据.csv'")
    
    # 保存scaler用于预测
    import joblib
    os.makedirs('models', exist_ok=True)
    joblib.dump(scaler, 'models/combined_scaler.pkl')
    
    return merged_data

# 主函数
def process_data():
    print("开始数据处理...")
    process_stock_data()
    process_gold_data()
    process_combined_data()
    print("数据处理完成！")

if __name__ == "__main__":
    process_data()
