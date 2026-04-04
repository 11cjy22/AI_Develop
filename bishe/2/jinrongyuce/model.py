import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv1D, MaxPooling1D, LSTM, Dense, Attention, Flatten, Dropout

# 创建 CNN-LSTM+Attention 模型
def create_model(input_shape):
    # 输入层
    inputs = Input(shape=input_shape)
    
    # CNN 部分 - 提取短期波动特征
    x = Conv1D(filters=64, kernel_size=3, activation='relu', padding='same')(inputs)
    x = MaxPooling1D(pool_size=2)(x)
    x = Conv1D(filters=128, kernel_size=3, activation='relu', padding='same')(x)
    x = MaxPooling1D(pool_size=2)(x)
    
    # LSTM 部分 - 学习时间序列长期依赖
    x = LSTM(128, return_sequences=True)(x)
    x = LSTM(64, return_sequences=True)(x)
    
    # Attention 部分 - 自动关注重要时间步
    attention_output = Attention()([x, x])
    
    # 展平
    x = Flatten()(attention_output)
    
    # 全连接层
    x = Dense(64, activation='relu')(x)
    x = Dropout(0.5)(x)
    x = Dense(32, activation='relu')(x)
    
    # 输出层 - 二分类
    outputs = Dense(1, activation='sigmoid')(x)
    
    # 构建模型
    model = Model(inputs=inputs, outputs=outputs)
    
    # 编译模型
    model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
    
    return model

# 创建股票模型
def create_stock_model():
    # 股票数据有7个特征
    return create_model((30, 7))

# 创建黄金模型
def create_gold_model():
    # 黄金数据有7个特征
    return create_model((30, 7))

# 创建联合模型
def create_combined_model():
    # 联合数据有14个特征
    return create_model((30, 14))

if __name__ == "__main__":
    # 测试模型创建
    print("股票模型:")
    stock_model = create_stock_model()
    stock_model.summary()
    
    print("\n黄金模型:")
    gold_model = create_gold_model()
    gold_model.summary()
    
    print("\n联合模型:")
    combined_model = create_combined_model()
    combined_model.summary()
