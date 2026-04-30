import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import os

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
    
    # 计算5日均线
    stock_data['MA5_stock'] = stock_data['close_stock'].rolling(window=5).mean()
    
    # 计算20日均线
    stock_data['MA20_stock'] = stock_data['close_stock'].rolling(window=20).mean()
    
    # 计算20日波动率
    stock_data['volatility'] = stock_data['close_stock'].rolling(window=20).std()
    
    # 构建标签：次日跌幅 > 1.5% → label=1
    stock_data['next_day_return'] = (stock_data['close_stock'].shift(-1) - stock_data['close_stock']) / stock_data['close_stock']
    stock_data['label'] = (stock_data['next_day_return'] < -0.015).astype(int)
    
    # 删除缺失值
    stock_data = stock_data.dropna()
    print(f"股票数据删除缺失值后共{len(stock_data)}条记录")
    
    # 选择需要的特征列
    features = ['close_stock', 'open_stock', 'high_stock', 'low_stock',
                'MA5_stock', 'MA20_stock', 'volatility']
    
    # 归一化
    scaler = MinMaxScaler()
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
    
    # 计算5日均线
    gold_data['MA5_gold'] = gold_data['close_gold'].rolling(window=5).mean()
    
    # 计算20日均线
    gold_data['MA20_gold'] = gold_data['close_gold'].rolling(window=20).mean()
    
    # 计算20日波动率
    gold_data['volatility_gold'] = gold_data['close_gold'].rolling(window=20).std()
    
    # 构建标签：次日跌幅 > 1.5% → label=1
    gold_data['next_day_return'] = (gold_data['close_gold'].shift(-1) - gold_data['close_gold']) / gold_data['close_gold']
    gold_data['label'] = (gold_data['next_day_return'] < -0.015).astype(int)
    
    # 删除缺失值
    gold_data = gold_data.dropna()
    print(f"黄金数据删除缺失值后共{len(gold_data)}条记录")
    
    # 选择需要的特征列
    features = ['close_gold', 'open_gold', 'high_gold', 'low_gold',
                'MA5_gold', 'MA20_gold', 'volatility_gold']
    
    # 归一化
    scaler = MinMaxScaler()
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
    
    # 计算5日均线
    merged_data['MA5_stock'] = merged_data['close_stock'].rolling(window=5).mean()
    merged_data['MA5_gold'] = merged_data['close_gold'].rolling(window=5).mean()
    
    # 计算20日均线
    merged_data['MA20_stock'] = merged_data['close_stock'].rolling(window=20).mean()
    merged_data['MA20_gold'] = merged_data['close_gold'].rolling(window=20).mean()
    
    # 计算20日波动率
    merged_data['volatility_stock'] = merged_data['close_stock'].rolling(window=20).std()
    merged_data['volatility_gold'] = merged_data['close_gold'].rolling(window=20).std()
    
    # 构建标签：次日跌幅 > 1.5% → label=1
    merged_data['next_day_return'] = (merged_data['close_stock'].shift(-1) - merged_data['close_stock']) / merged_data['close_stock']
    merged_data['label'] = (merged_data['next_day_return'] < -0.015).astype(int)
    
    # 删除缺失值
    merged_data = merged_data.dropna()
    print(f"删除缺失值后共{len(merged_data)}条记录")
    
    # 选择需要的特征列
    features = ['close_stock', 'open_stock', 'high_stock', 'low_stock',
                'close_gold', 'open_gold', 'high_gold', 'low_gold',
                'MA5_stock', 'MA20_stock', 'volatility_stock',
                'MA5_gold', 'MA20_gold', 'volatility_gold']
    
    # 归一化
    scaler = MinMaxScaler()
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
