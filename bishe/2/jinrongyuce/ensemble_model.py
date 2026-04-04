import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from tensorflow.keras.models import load_model
import xgboost as xgb
import lightgbm as lgb
import joblib
import os

# 加载数据
def load_processed_data():
    stock_data = pd.read_csv('data/股票数据_处理后.csv')
    gold_data = pd.read_csv('data/黄金数据_处理后.csv')
    combined_data = pd.read_csv('data/合成后数据.csv')
    return stock_data, gold_data, combined_data

# 构建时间窗口数据 - 股票
def create_stock_windows(data, window_size=30):
    X = []
    y = []
    features = ['close_stock', 'open_stock', 'high_stock', 'low_stock',
                'MA5_stock', 'volatility', 'return',
                'MACD_diff', 'MACD_dea', 'MACD_hist',
                'KDJ_K', 'KDJ_D', 'KDJ_J',
                'RSI',
                'BOLL_upper', 'BOLL_middle', 'BOLL_lower']
    
    for i in range(len(data) - window_size):
        window = data[features].iloc[i:i+window_size].values
        label = data['label'].iloc[i+window_size]
        X.append(window)
        y.append(label)
    
    return np.array(X), np.array(y)

# 构建时间窗口数据 - 黄金
def create_gold_windows(data, window_size=30):
    X = []
    y = []
    features = ['close_gold', 'open_gold', 'high_gold', 'low_gold',
                'MA5_gold', 'volatility_gold', 'return_gold',
                'MACD_diff', 'MACD_dea', 'MACD_hist',
                'KDJ_K', 'KDJ_D', 'KDJ_J',
                'RSI',
                'BOLL_upper', 'BOLL_middle', 'BOLL_lower']
    
    for i in range(len(data) - window_size):
        window = data[features].iloc[i:i+window_size].values
        label = data['label'].iloc[i+window_size]
        X.append(window)
        y.append(label)
    
    return np.array(X), np.array(y)

# 提取LSTM模型的特征
def extract_lstm_features(model, X):
    # 创建特征提取模型
    feature_extractor = load_model(model, compile=False)
    # 提取倒数第二层的特征
    feature_model = tf.keras.Model(inputs=feature_extractor.input,
                                  outputs=feature_extractor.layers[-3].output)
    # 提取特征
    features = feature_model.predict(X)
    return features

# 训练LSTM+XGBoost集成模型
def train_lstm_xgboost_model(data_type="股票"):
    print(f"开始训练LSTM+XGBoost集成模型...")
    
    # 加载数据
    stock_data, gold_data, combined_data = load_processed_data()
    
    if data_type == "股票":
        data = stock_data
        create_windows = create_stock_windows
        lstm_model_path = 'models/best_stock_model.h5'
        xgb_model_path = 'models/ensemble_stock_xgboost.model'
    elif data_type == "黄金":
        data = gold_data
        create_windows = create_gold_windows
        lstm_model_path = 'models/best_gold_model.h5'
        xgb_model_path = 'models/ensemble_gold_xgboost.model'
    else:
        print("不支持的数据类型")
        return None
    
    # 构建窗口数据
    X, y = create_windows(data, window_size=30)
    print(f"构建窗口后，X 形状: {X.shape}, y 形状: {y.shape}")
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"训练集大小: {len(X_train)}, 测试集大小: {len(X_test)}")
    
    # 提取LSTM特征
    print("提取LSTM特征...")
    X_train_features = extract_lstm_features(lstm_model_path, X_train)
    X_test_features = extract_lstm_features(lstm_model_path, X_test)
    print(f"提取特征后，X_train 形状: {X_train_features.shape}, X_test 形状: {X_test_features.shape}")
    
    # 训练XGBoost模型
    print("训练XGBoost模型...")
    xgb_model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
    xgb_model.fit(X_train_features, y_train)
    
    # 保存模型
    os.makedirs('models', exist_ok=True)
    joblib.dump(xgb_model, xgb_model_path)
    print(f"XGBoost模型保存为: {xgb_model_path}")
    
    # 评估模型
    y_pred = xgb_model.predict(X_test_features)
    
    # 计算评估指标
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    
    # 打印评估结果
    print(f"\nLSTM+XGBoost集成模型评估结果:")
    print(f"准确率: {accuracy:.4f}")
    print(f"精确率: {precision:.4f}")
    print(f"召回率: {recall:.4f}")
    print(f"F1 分数: {f1:.4f}")
    print("混淆矩阵:")
    print(cm)
    
    return xgb_model

# 训练LSTM+LightGBM集成模型
def train_lstm_lightgbm_model(data_type="股票"):
    print(f"开始训练LSTM+LightGBM集成模型...")
    
    # 加载数据
    stock_data, gold_data, combined_data = load_processed_data()
    
    if data_type == "股票":
        data = stock_data
        create_windows = create_stock_windows
        lstm_model_path = 'models/best_stock_model.h5'
        lgb_model_path = 'models/ensemble_stock_lightgbm.model'
    elif data_type == "黄金":
        data = gold_data
        create_windows = create_gold_windows
        lstm_model_path = 'models/best_gold_model.h5'
        lgb_model_path = 'models/ensemble_gold_lightgbm.model'
    else:
        print("不支持的数据类型")
        return None
    
    # 构建窗口数据
    X, y = create_windows(data, window_size=30)
    print(f"构建窗口后，X 形状: {X.shape}, y 形状: {y.shape}")
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"训练集大小: {len(X_train)}, 测试集大小: {len(X_test)}")
    
    # 提取LSTM特征
    print("提取LSTM特征...")
    X_train_features = extract_lstm_features(lstm_model_path, X_train)
    X_test_features = extract_lstm_features(lstm_model_path, X_test)
    print(f"提取特征后，X_train 形状: {X_train_features.shape}, X_test 形状: {X_test_features.shape}")
    
    # 训练LightGBM模型
    print("训练LightGBM模型...")
    lgb_model = lgb.LGBMClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
    lgb_model.fit(X_train_features, y_train)
    
    # 保存模型
    os.makedirs('models', exist_ok=True)
    joblib.dump(lgb_model, lgb_model_path)
    print(f"LightGBM模型保存为: {lgb_model_path}")
    
    # 评估模型
    y_pred = lgb_model.predict(X_test_features)
    
    # 计算评估指标
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    
    # 打印评估结果
    print(f"\nLSTM+LightGBM集成模型评估结果:")
    print(f"准确率: {accuracy:.4f}")
    print(f"精确率: {precision:.4f}")
    print(f"召回率: {recall:.4f}")
    print(f"F1 分数: {f1:.4f}")
    print("混淆矩阵:")
    print(cm)
    
    return lgb_model

# 主函数
def train_ensemble_models():
    print("开始训练所有集成模型...")
    
    # 训练股票集成模型
    print("\n===== 训练股票集成模型 =====")
    train_lstm_xgboost_model(data_type="股票")
    train_lstm_lightgbm_model(data_type="股票")
    
    # 训练黄金集成模型
    print("\n===== 训练黄金集成模型 =====")
    train_lstm_xgboost_model(data_type="黄金")
    train_lstm_lightgbm_model(data_type="黄金")
    
    print("所有集成模型训练完成！")

if __name__ == "__main__":
    import tensorflow as tf
    train_ensemble_models()
