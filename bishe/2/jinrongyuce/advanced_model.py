import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv1D, MaxPooling1D, LSTM, GRU, Dense, Flatten, Dropout, Attention, MultiHeadAttention, LayerNormalization, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau

# 创建 LSTM+Attention 模型（推荐使用）
def create_lstm_attention_model(input_shape):
    inputs = Input(shape=input_shape)
    
    # CNN 部分 - 提取短期波动特征
    x = Conv1D(filters=128, kernel_size=3, activation='relu', padding='same')(inputs)
    x = MaxPooling1D(pool_size=2)(x)
    x = Conv1D(filters=256, kernel_size=3, activation='relu', padding='same')(x)
    x = MaxPooling1D(pool_size=2)(x)
    
    # 双向 LSTM 部分 - 学习时间序列长期依赖
    x = Bidirectional(LSTM(256, return_sequences=True))(x)
    x = Bidirectional(LSTM(128, return_sequences=True))(x)
    
    # 多头 Attention 机制 - 自动关注重要时间步
    attention_output = MultiHeadAttention(num_heads=8, key_dim=64)(x, x)
    attention_output = LayerNormalization()(attention_output)
    
    # 展平
    x = Flatten()(attention_output)
    
    # 全连接层 + Dropout + 正则化 防止过拟合
    x = Dense(128, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.001))(x)
    x = Dropout(0.5)(x)
    x = Dense(64, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.001))(x)
    x = Dropout(0.4)(x)
    
    # 输出层 - 二分类（涨/跌）
    outputs = Dense(1, activation='sigmoid')(x)
    
    # 构建模型
    model = Model(inputs=inputs, outputs=outputs)
    
    # 编译模型
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy', 'precision', 'recall', 'auc']
    )
    
    return model

# 创建 GRU 模型（更快、更稳）
def create_gru_model(input_shape):
    inputs = Input(shape=input_shape)
    
    # CNN 部分
    x = Conv1D(filters=128, kernel_size=3, activation='relu', padding='same')(inputs)
    x = MaxPooling1D(pool_size=2)(x)
    
    # 双向 GRU 部分
    x = Bidirectional(GRU(256, return_sequences=True))(x)
    x = Bidirectional(GRU(128, return_sequences=True))(x)
    
    # Attention 机制
    attention_output = MultiHeadAttention(num_heads=8, key_dim=64)(x, x)
    attention_output = LayerNormalization()(attention_output)
    
    # 展平
    x = Flatten()(attention_output)
    
    # 全连接层 + Dropout + 正则化 防止过拟合
    x = Dense(128, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.001))(x)
    x = Dropout(0.5)(x)
    x = Dense(64, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.001))(x)
    x = Dropout(0.4)(x)
    
    # 输出层
    outputs = Dense(1, activation='sigmoid')(x)
    
    # 构建模型
    model = Model(inputs=inputs, outputs=outputs)
    
    # 编译模型
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy', 'precision', 'recall', 'auc']
    )
    
    return model

# 创建 Temporal Fusion Transformer 模型（金融预测最强之一）
def create_temporal_fusion_transformer_model(input_shape):
    inputs = Input(shape=input_shape)
    
    # CNN 部分
    x = Conv1D(filters=128, kernel_size=3, activation='relu', padding='same')(inputs)
    x = MaxPooling1D(pool_size=2)(x)
    
    # Transformer 编码器
    x = tf.keras.layers.MultiHeadAttention(num_heads=8, key_dim=64)(x, x)
    x = LayerNormalization()(x)
    x = tf.keras.layers.GlobalAveragePooling1D()(x)
    
    # 全连接层 + Dropout + 正则化 防止过拟合
    x = Dense(256, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.001))(x)
    x = Dropout(0.5)(x)
    x = Dense(128, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.001))(x)
    x = Dropout(0.4)(x)
    
    # 输出层
    outputs = Dense(1, activation='sigmoid')(x)
    
    # 构建模型
    model = Model(inputs=inputs, outputs=outputs)
    
    # 编译模型
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy', 'precision', 'recall', 'auc']
    )
    
    return model

# 创建股票模型（使用LSTM+Attention）
def create_stock_model():
    # 股票数据有更多特征
    return create_lstm_attention_model((30, 17))

# 创建黄金模型（使用GRU）
def create_gold_model():
    # 黄金数据特征较少
    return create_gru_model((30, 17))

# 创建联合模型（使用Transformer）
def create_combined_model():
    # 联合数据特征最多
    return create_temporal_fusion_transformer_model((30, 24))

if __name__ == "__main__":
    print("股票模型（LSTM+Attention）:")
    stock_model = create_stock_model()
    stock_model.summary()
    
    print("\n黄金模型（GRU）:")
    gold_model = create_gold_model()
    gold_model.summary()
    
    print("\n联合模型（Transformer）:")
    combined_model = create_combined_model()
    combined_model.summary()