import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, Attention, Dropout, LayerNormalization

# 创建简化版 LSTM+Attention 模型（去掉CNN，减少复杂度）
def create_improved_model(input_shape):
    # 输入层
    inputs = Input(shape=input_shape)
    
    # LSTM 部分 - 减少层数和units
    x = LSTM(64, return_sequences=True)(inputs)
    x = LayerNormalization()(x)  # 添加归一化
    x = Dropout(0.3)(x)
    
    x = LSTM(32, return_sequences=True)(x)
    x = LayerNormalization()(x)
    x = Dropout(0.3)(x)
    
    # Attention 部分
    attention_output = Attention()([x, x])
    
    # 取最后一个时间步
    x = tf.keras.layers.Lambda(lambda x: x[:, -1, :])(attention_output)
    
    # 全连接层
    x = Dense(32, activation='relu')(x)
    x = Dropout(0.3)(x)
    x = Dense(16, activation='relu')(x)
    
    # 输出层 - 二分类
    outputs = Dense(1, activation='sigmoid')(x)
    
    # 构建模型
    model = Model(inputs=inputs, outputs=outputs)
    
    # 编译模型
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                  loss='binary_crossentropy',
                  metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()])
    
    return model

# 创建改进的联合模型（15个特征）
def create_combined_model_improved():
    return create_improved_model((30, 15))

if __name__ == "__main__":
    # 测试模型创建
    print("改进版联合模型:")
    model = create_combined_model_improved()
    model.summary()
