import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
import joblib
import akshare as ak
from datetime import datetime

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

# 分析预测原因
def analyze_prediction(data, risk_prob, data_type="股票"):
    reasons = []
    
    if data_type == "股票":
        # 获取最新的数据
        latest = data.iloc[-1]
        close = latest['close_stock']
        ma5 = latest['MA5_stock']
        volatility = latest['volatility']
        
        # 计算价格变化
        price_change = (close - data['close_stock'].iloc[-5]) / data['close_stock'].iloc[-5] * 100
        
        # 分析价格趋势
        if price_change > 2:
            reasons.append(f"价格近期上涨{price_change:.2f}%，可能存在回调风险")
        elif price_change < -2:
            reasons.append(f"价格近期下跌{price_change:.2f}%，可能存在继续下跌风险")
        else:
            reasons.append(f"价格近期相对稳定，变化{price_change:.2f}%")
        
        # 分析均线
        if close < ma5:
            reasons.append(f"收盘价{close:.2f}低于5日均线{ma5:.2f}，短期趋势偏弱")
        else:
            reasons.append(f"收盘价{close:.2f}高于5日均线{ma5:.2f}，短期趋势偏强")
        
        # 分析波动率
        avg_volatility = data['volatility'].mean()
        if volatility > avg_volatility * 1.5:
            reasons.append(f"波动率{volatility:.2f}高于平均水平{avg_volatility:.2f}，市场波动较大")
        elif volatility < avg_volatility * 0.7:
            reasons.append(f"波动率{volatility:.2f}低于平均水平{avg_volatility:.2f}，市场相对稳定")
        else:
            reasons.append(f"波动率{volatility:.2f}处于正常水平")
        
        # 综合分析
        if risk_prob > 0.6:
            reasons.append("综合多个技术指标，市场存在较高的下跌风险")
        elif risk_prob > 0.4:
            reasons.append("综合多个技术指标，市场风险适中")
        else:
            reasons.append("综合多个技术指标，市场风险较低")
    
    elif data_type == "黄金":
        # 获取最新的数据
        latest = data.iloc[-1]
        close = latest['close_gold']
        ma5 = latest['MA5_gold']
        volatility = latest['volatility_gold']
        
        # 计算价格变化
        price_change = (close - data['close_gold'].iloc[-5]) / data['close_gold'].iloc[-5] * 100
        
        # 分析价格趋势
        if price_change > 2:
            reasons.append(f"价格近期上涨{price_change:.2f}%，可能存在回调风险")
        elif price_change < -2:
            reasons.append(f"价格近期下跌{price_change:.2f}%，可能存在继续下跌风险")
        else:
            reasons.append(f"价格近期相对稳定，变化{price_change:.2f}%")
        
        # 分析均线
        if close < ma5:
            reasons.append(f"收盘价{close:.2f}低于5日均线{ma5:.2f}，短期趋势偏弱")
        else:
            reasons.append(f"收盘价{close:.2f}高于5日均线{ma5:.2f}，短期趋势偏强")
        
        # 分析波动率
        avg_volatility = data['volatility_gold'].mean()
        if volatility > avg_volatility * 1.5:
            reasons.append(f"波动率{volatility:.2f}高于平均水平{avg_volatility:.2f}，市场波动较大")
        elif volatility < avg_volatility * 0.7:
            reasons.append(f"波动率{volatility:.2f}低于平均水平{avg_volatility:.2f}，市场相对稳定")
        else:
            reasons.append(f"波动率{volatility:.2f}处于正常水平")
        
        # 综合分析
        if risk_prob > 0.6:
            reasons.append("综合多个技术指标，黄金市场存在较高的下跌风险")
        elif risk_prob > 0.4:
            reasons.append("综合多个技术指标，黄金市场风险适中")
        else:
            reasons.append("综合多个技术指标，黄金市场风险较低")
    
    return reasons

# 加载最新股票数据
def load_latest_stock_data(stock_symbol="sh000300"):
    print(f"加载最新股票数据，股票代码：{stock_symbol}...")
    
    # 下载股票数据（最近90天）
    stock_data = ak.stock_zh_index_daily(symbol=stock_symbol).tail(90)
    
    # 转换日期格式
    stock_data['date'] = pd.to_datetime(stock_data['date'])
    
    # 重命名列
    stock_data = stock_data.rename(columns={
        'open': 'open_stock',
        'close': 'close_stock',
        'high': 'high_stock',
        'low': 'low_stock'
    })
    
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
    
    # 删除缺失值
    stock_data = stock_data.dropna()
    print(f"删除缺失值后共{len(stock_data)}条记录")
    print(f"数据日期范围：{stock_data['date'].min()} 到 {stock_data['date'].max()}")
    print(f"收盘价范围：{stock_data['close_stock'].min():.2f} 到 {stock_data['close_stock'].max():.2f}")
    
    return stock_data

# 加载最新黄金数据
def load_latest_gold_data():
    print("加载最新黄金数据...")
    
    # 下载黄金数据（最近90天）
    gold_data = ak.spot_golden_benchmark_sge().tail(90)
    
    # 重命名列
    gold_data = gold_data.rename(columns={'交易时间': 'date'})
    
    # 转换日期格式
    gold_data['date'] = pd.to_datetime(gold_data['date'])
    
    # 重命名列
    gold_data = gold_data.rename(columns={
        '早盘价': 'open_gold',
        '晚盘价': 'close_gold'
    })
    
    # 计算黄金的最高价和最低价
    gold_data['high_gold'] = gold_data[['open_gold', 'close_gold']].max(axis=1)
    gold_data['low_gold'] = gold_data[['open_gold', 'close_gold']].min(axis=1)
    
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
    
    # 删除缺失值
    gold_data = gold_data.dropna()
    print(f"删除缺失值后共{len(gold_data)}条记录")
    print(f"数据日期范围：{gold_data['date'].min()} 到 {gold_data['date'].max()}")
    print(f"收盘价范围：{gold_data['close_gold'].min():.2f} 到 {gold_data['close_gold'].max():.2f}")
    
    return gold_data

# 预测股票风险
def predict_stock_risk(stock_symbol="sh000300"):
    print(f"开始股票风险预测，股票代码：{stock_symbol}...")
    
    # 加载模型
    model = load_model('models/best_stock_model.h5')
    
    # 加载scaler
    scaler = joblib.load('models/stock_scaler.pkl')
    
    # 加载最新数据
    data = load_latest_stock_data(stock_symbol)
    
    # 选择需要的特征列
    features = ['close_stock', 'open_stock', 'high_stock', 'low_stock',
                'MA5_stock', 'volatility', 'return',
                'MACD_diff', 'MACD_dea', 'MACD_hist',
                'KDJ_K', 'KDJ_D', 'KDJ_J',
                'RSI',
                'BOLL_upper', 'BOLL_middle', 'BOLL_lower']
    
    # 确保有足够的数据
    if len(data) < 30:
        print("数据不足30天，无法预测")
        return None
    
    # 提取最后30天的数据作为预测样本
    latest_window = data[features].tail(30).values
    
    # 标准化
    latest_window_scaled = scaler.transform(latest_window)
    
    # 重塑为模型输入格式
    latest_window_scaled = latest_window_scaled.reshape(1, 30, 17)
    
    # 预测
    risk_prob = model.predict(latest_window_scaled)[0][0]
    risk_prediction = 1 if risk_prob > 0.5 else 0
    
    # 分析预测原因
    reasons = analyze_prediction(data, risk_prob, data_type="股票")
    
    # 生成建议
    if risk_prediction == 1:
        suggestion = "建议：市场存在大跌风险，建议减少仓位或采取对冲措施"
    else:
        suggestion = "建议：市场风险较低，可以正常持有或适当增加仓位"
    
    # 打印预测结果
    print(f"\n预测结果：")
    print(f"风险概率：{risk_prob:.2%}")
    print(f"预测结论：{'有风险' if risk_prediction == 1 else '安全'}")
    print(f"建议：{suggestion}")
    print("原因分析：")
    for reason in reasons:
        print(f"- {reason}")
    
    # 返回结果
    return {
        'risk_prob': risk_prob,
        'risk_prediction': risk_prediction,
        'suggestion': suggestion,
        'reasons': reasons,
        'data': data
    }

# 预测黄金风险
def predict_gold_risk():
    print("开始黄金风险预测...")
    
    # 加载模型
    model = load_model('models/best_gold_model.h5')
    
    # 加载scaler
    scaler = joblib.load('models/gold_scaler.pkl')
    
    # 加载最新数据
    data = load_latest_gold_data()
    
    # 选择需要的特征列
    features = ['close_gold', 'open_gold', 'high_gold', 'low_gold',
                'MA5_gold', 'volatility_gold', 'return_gold',
                'MACD_diff', 'MACD_dea', 'MACD_hist',
                'KDJ_K', 'KDJ_D', 'KDJ_J',
                'RSI',
                'BOLL_upper', 'BOLL_middle', 'BOLL_lower']
    
    # 确保有足够的数据
    if len(data) < 30:
        print("数据不足30天，无法预测")
        return None
    
    # 提取最后30天的数据作为预测样本
    latest_window = data[features].tail(30).values
    
    # 标准化
    latest_window_scaled = scaler.transform(latest_window)
    
    # 重塑为模型输入格式
    latest_window_scaled = latest_window_scaled.reshape(1, 30, 17)
    
    # 预测
    risk_prob = model.predict(latest_window_scaled)[0][0]
    risk_prediction = 1 if risk_prob > 0.5 else 0
    
    # 分析预测原因
    reasons = analyze_prediction(data, risk_prob, data_type="黄金")
    
    # 生成建议
    if risk_prediction == 1:
        suggestion = "建议：黄金市场存在大跌风险，建议减少仓位或采取对冲措施"
    else:
        suggestion = "建议：黄金市场风险较低，可以正常持有或适当增加仓位"
    
    # 打印预测结果
    print(f"\n预测结果：")
    print(f"风险概率：{risk_prob:.2%}")
    print(f"预测结论：{'有风险' if risk_prediction == 1 else '安全'}")
    print(f"建议：{suggestion}")
    print("原因分析：")
    for reason in reasons:
        print(f"- {reason}")
    
    # 返回结果
    return {
        'risk_prob': risk_prob,
        'risk_prediction': risk_prediction,
        'suggestion': suggestion,
        'reasons': reasons,
        'data': data
    }

# 预测风险（根据数据类型）
def predict_risk(data_type="股票", stock_symbol="sh000300"):
    if data_type == "股票":
        return predict_stock_risk(stock_symbol)
    elif data_type == "黄金":
        return predict_gold_risk()
    else:
        print("不支持的数据类型")
        return None

if __name__ == "__main__":
    # 测试股票预测
    print("\n测试股票预测：")
    predict_stock_risk()
    
    # 测试黄金预测
    print("\n测试黄金预测：")
    predict_gold_risk()
