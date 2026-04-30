import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import os

# 读取数据
def load_data():
    stock_data = pd.read_csv('data/沪深300数据.csv')
    gold_data = pd.read_csv('data/黄金数据.csv')
    return stock_data, gold_data

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
        'volume': 'volume_stock',  # 添加成交量
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
    
    # 构建标签：降低阈值到1%，增加正样本数量
    merged_data['next_day_return'] = (merged_data['close_stock'].shift(-1) - merged_data['close_stock']) / merged_data['close_stock']
    merged_data['label'] = (merged_data['next_day_return'] < -0.01).astype(int)  # 改为1%
    
    # 删除缺失值
    merged_data = merged_data.dropna()
    print(f"删除缺失值后共{len(merged_data)}条记录")
    
    # 打印标签分布
    print(f"\n标签分布:")
    print(merged_data['label'].value_counts())
    print(f"正样本比例: {merged_data['label'].sum() / len(merged_data) * 100:.2f}%")
    
    # 选择需要的特征列（添加成交量）
    features = ['close_stock', 'open_stock', 'high_stock', 'low_stock', 'volume_stock',
                'close_gold', 'open_gold', 'high_gold', 'low_gold',
                'MA5_stock', 'MA20_stock', 'volatility_stock',
                'MA5_gold', 'MA20_gold', 'volatility_gold']
    
    # 归一化
    scaler = MinMaxScaler()
    merged_data[features] = scaler.fit_transform(merged_data[features])
    
    # 保存最终数据
    merged_data.to_csv('data/合成后数据_改进版.csv', index=False, encoding='utf-8-sig')
    print("联合数据处理完成，保存为 'data/合成后数据_改进版.csv'")
    
    # 保存scaler用于预测
    import joblib
    os.makedirs('models', exist_ok=True)
    joblib.dump(scaler, 'models/combined_scaler_improved.pkl')
    
    return merged_data

# 主函数
def process_data():
    print("开始数据处理...")
    process_combined_data()
    print("数据处理完成！")

if __name__ == "__main__":
    process_data()
