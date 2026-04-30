import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.models import load_model
from model_improved import create_combined_model_improved
import os

# 构建时间窗口数据 - 联合
def create_combined_windows(data, window_size=30):
    X = []
    y = []
    features = ['close_stock', 'open_stock', 'high_stock', 'low_stock', 'volume_stock',
                'close_gold', 'open_gold', 'high_gold', 'low_gold',
                'MA5_stock', 'MA20_stock', 'volatility_stock',
                'MA5_gold', 'MA20_gold', 'volatility_gold']
    
    for i in range(len(data) - window_size):
        window = data[features].iloc[i:i+window_size].values
        label = data['label'].iloc[i+window_size]
        X.append(window)
        y.append(label)
    
    return np.array(X), np.array(y)

# 训练改进版联合模型
def train_improved_model():
    print("开始训练改进版联合模型...")
    
    # 读取数据
    data = pd.read_csv('data/合成后数据_改进版.csv')
    
    # 构建窗口数据
    X, y = create_combined_windows(data, window_size=30)
    print(f"构建窗口后，X 形状: {X.shape}, y 形状: {y.shape}")
    
    # 使用时间序列切分（前80%训练，后20%测试）
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    print(f"训练集大小: {len(X_train)}, 测试集大小: {len(X_test)}")
    
    # 计算类别权重（给风险样本更高权重）
    neg_count = np.sum(y_train == 0)
    pos_count = np.sum(y_train == 1)
    class_weights = {
        0: 1.0,
        1: neg_count / pos_count if pos_count > 0 else 1.0
    }
    print(f"类别权重: {class_weights}")
    print(f"训练集标签分布: 负样本={neg_count}, 正样本={pos_count}")
    
    # 创建模型
    model = create_combined_model_improved()
    
    # 回调函数
    early_stopping = EarlyStopping(
        monitor='val_loss',
        patience=15,
        restore_best_weights=True,
        verbose=1
    )
    
    checkpoint = ModelCheckpoint(
        'models/best_improved_model.h5',
        monitor='val_recall',
        save_best_only=True,
        mode='max',
        verbose=1
    )
    
    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=0.00001,
        verbose=1
    )
    
    # 训练模型
    history = model.fit(
        X_train, y_train,
        epochs=100,
        batch_size=32,
        validation_split=0.1,
        class_weight=class_weights,
        callbacks=[early_stopping, checkpoint, reduce_lr],
        verbose=1
    )
    
    # 加载最优模型
    model = load_model('models/best_improved_model.h5')
    
    # 在测试集上评估
    y_pred_prob = model.predict(X_test)
    y_pred = (y_pred_prob > 0.5).astype(int).flatten()
    
    # 计算评估指标
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)
    
    # 打印评估结果
    print("\n" + "="*60)
    print("改进版模型评估结果:")
    print("="*60)
    print(f"准确率 (Accuracy):     {accuracy:.4f}")
    print(f"精确率 (Precision):    {precision:.4f}")
    print(f"召回率 (Recall):       {recall:.4f}")
    print(f"F1 分数 (F1-Score):    {f1:.4f}")
    print("\n混淆矩阵:")
    print(cm)
    print("\n详细分类报告:")
    print(classification_report(y_test, y_pred, target_names=['正常', '风险']))
    print("="*60)
    
    # 保存最终模型
    os.makedirs('models', exist_ok=True)
    model.save('models/final_improved_model.h5')
    print("改进版模型训练完成并保存！")
    
    return model, history

if __name__ == "__main__":
    train_improved_model()
