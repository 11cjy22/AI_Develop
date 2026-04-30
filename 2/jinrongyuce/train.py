import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.models import load_model
from model import create_stock_model, create_gold_model, create_combined_model
import os

# 构建时间窗口数据 - 股票
def create_stock_windows(data, window_size=30):
    X = []
    y = []
    features = ['close_stock', 'open_stock', 'high_stock', 'low_stock',
                'MA5_stock', 'MA20_stock', 'volatility']
    
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
                'MA5_gold', 'MA20_gold', 'volatility_gold']
    
    for i in range(len(data) - window_size):
        window = data[features].iloc[i:i+window_size].values
        label = data['label'].iloc[i+window_size]
        X.append(window)
        y.append(label)
    
    return np.array(X), np.array(y)

# 构建时间窗口数据 - 联合
def create_combined_windows(data, window_size=30):
    X = []
    y = []
    features = ['close_stock', 'open_stock', 'high_stock', 'low_stock',
                'close_gold', 'open_gold', 'high_gold', 'low_gold',
                'MA5_stock', 'MA20_stock', 'volatility_stock',
                'MA5_gold', 'MA20_gold', 'volatility_gold']
    
    for i in range(len(data) - window_size):
        window = data[features].iloc[i:i+window_size].values
        label = data['label'].iloc[i+window_size]
        X.append(window)
        y.append(label)
    
    return np.array(X), np.array(y)

# 训练股票模型
def train_stock_model():
    print("开始训练股票模型...")
    
    # 读取数据
    data = pd.read_csv('data/股票数据_处理后.csv')
    
    # 构建窗口数据
    X, y = create_stock_windows(data, window_size=30)
    print(f"构建窗口后，X 形状: {X.shape}, y 形状: {y.shape}")
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"训练集大小: {len(X_train)}, 测试集大小: {len(X_test)}")
    
    # 计算类别权重
    class_weights = {0: 1, 1: len(y_train) / sum(y_train) if sum(y_train) > 0 else 1}  # 给风险样本更高的权重
    print(f"股票数据类别权重: {class_weights}")
    
    # 创建模型
    model = create_stock_model()
    
    # 早停机制
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    
    # 保存最优模型
    checkpoint = ModelCheckpoint('models/best_stock_model.h5', monitor='val_accuracy', save_best_only=True, mode='max')
    
    # 训练模型
    history = model.fit(X_train, y_train, 
                        epochs=100, 
                        batch_size=32, 
                        validation_split=0.1, 
                        class_weight=class_weights,
                        callbacks=[early_stopping, checkpoint])
    
    # 加载最优模型
    model = load_model('models/best_stock_model.h5')
    
    # 在测试集上评估
    y_pred = (model.predict(X_test) > 0.5).astype(int).flatten()
    
    # 计算评估指标
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)  # 风险识别率
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    
    # 打印评估结果
    print("\n股票模型评估结果:")
    print(f"准确率: {accuracy:.4f}")
    print(f"风险识别率: {recall:.4f}")
    print(f"精确率: {precision:.4f}")
    print(f"F1 分数: {f1:.4f}")
    print("混淆矩阵:")
    print(cm)
    
    # 保存最终模型
    os.makedirs('models', exist_ok=True)
    model.save('models/final_stock_model.h5')
    print("股票模型训练完成并保存！")
    
    return model

# 训练黄金模型
def train_gold_model():
    print("开始训练黄金模型...")
    
    # 读取数据
    data = pd.read_csv('data/黄金数据_处理后.csv')
    
    # 构建窗口数据
    X, y = create_gold_windows(data, window_size=30)
    print(f"构建窗口后，X 形状: {X.shape}, y 形状: {y.shape}")
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"训练集大小: {len(X_train)}, 测试集大小: {len(X_test)}")
    
    # 计算类别权重
    class_weights = {0: 1, 1: len(y_train) / sum(y_train) if sum(y_train) > 0 else 1}  # 给风险样本更高的权重
    print(f"黄金数据类别权重: {class_weights}")
    
    # 创建模型
    model = create_gold_model()
    
    # 早停机制
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    
    # 保存最优模型
    checkpoint = ModelCheckpoint('models/best_gold_model.h5', monitor='val_accuracy', save_best_only=True, mode='max')
    
    # 训练模型
    history = model.fit(X_train, y_train, 
                        epochs=100, 
                        batch_size=32, 
                        validation_split=0.1, 
                        class_weight=class_weights,
                        callbacks=[early_stopping, checkpoint])
    
    # 加载最优模型
    model = load_model('models/best_gold_model.h5')
    
    # 在测试集上评估
    y_pred = (model.predict(X_test) > 0.5).astype(int).flatten()
    
    # 计算评估指标
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)  # 风险识别率
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    
    # 打印评估结果
    print("\n黄金模型评估结果:")
    print(f"准确率: {accuracy:.4f}")
    print(f"风险识别率: {recall:.4f}")
    print(f"精确率: {precision:.4f}")
    print(f"F1 分数: {f1:.4f}")
    print("混淆矩阵:")
    print(cm)
    
    # 保存最终模型
    os.makedirs('models', exist_ok=True)
    model.save('models/final_gold_model.h5')
    print("黄金模型训练完成并保存！")
    
    return model

# 训练联合模型
def train_combined_model():
    print("开始训练联合模型...")
    
    # 读取数据
    data = pd.read_csv('data/合成后数据.csv')
    
    # 构建窗口数据
    X, y = create_combined_windows(data, window_size=30)
    print(f"构建窗口后，X 形状: {X.shape}, y 形状: {y.shape}")
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"训练集大小: {len(X_train)}, 测试集大小: {len(X_test)}")
    
    # 计算类别权重
    class_weights = {0: 1, 1: len(y_train) / sum(y_train) if sum(y_train) > 0 else 1}  # 给风险样本更高的权重
    print(f"联合数据类别权重: {class_weights}")
    
    # 创建模型
    model = create_combined_model()
    
    # 早停机制
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    
    # 保存最优模型
    checkpoint = ModelCheckpoint('models/best_combined_model.h5', monitor='val_accuracy', save_best_only=True, mode='max')
    
    # 训练模型
    history = model.fit(X_train, y_train, 
                        epochs=100, 
                        batch_size=32, 
                        validation_split=0.1, 
                        class_weight=class_weights,
                        callbacks=[early_stopping, checkpoint])
    
    # 加载最优模型
    model = load_model('models/best_combined_model.h5')
    
    # 在测试集上评估
    y_pred = (model.predict(X_test) > 0.5).astype(int).flatten()
    
    # 计算评估指标
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)  # 风险识别率
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    
    # 打印评估结果
    print("\n联合模型评估结果:")
    print(f"准确率: {accuracy:.4f}")
    print(f"风险识别率: {recall:.4f}")
    print(f"精确率: {precision:.4f}")
    print(f"F1 分数: {f1:.4f}")
    print("混淆矩阵:")
    print(cm)
    
    # 保存最终模型
    os.makedirs('models', exist_ok=True)
    model.save('models/final_combined_model.h5')
    print("联合模型训练完成并保存！")
    
    return model

# 主函数
def train_model():
    print("开始训练所有模型...")
    train_stock_model()
    train_gold_model()
    train_combined_model()
    print("所有模型训练完成！")

if __name__ == "__main__":
    train_model()
