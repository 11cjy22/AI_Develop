# A 股 + 黄金市场风险预测系统

基于深度学习的 A 股与黄金联动风险预测系统，使用 CNN-LSTM+Attention 混合模型，根据过去 30 天历史数据预测下一天是否出现大于 1.5% 的大跌风险，并提供可视化界面供用户操作。

## 项目功能

- 数据获取：使用 akshare 下载沪深300和黄金数据
- 数据处理：数据对齐、特征工程和标签构建
- 模型训练：使用 CNN-LSTM+Attention 混合模型进行训练
- 风险预测：预测下一天是否出现大跌风险
- 可视化界面：使用 Streamlit 开发的 Web 界面

## 文件结构

```
├── data/                 # 数据存储目录
├── models/               # 模型存储目录
├── data_download.py      # 数据下载脚本
├── data_process.py       # 数据处理脚本
├── model.py              # 模型结构脚本
├── train.py              # 模型训练脚本
├── predict.py            # 预测脚本
├── app.py                # Streamlit 可视化界面
└── README.md             # 使用说明
```

## 安装依赖

```bash
pip install -r requirements.txt
```

依赖包包括：
- akshare
- pandas
- numpy
- scikit-learn
- tensorflow
- streamlit
- joblib

## 使用步骤

1. **下载数据**
   ```bash
   python data_download.py
   ```

2. **处理数据**
   ```bash
   python data_process.py
   ```

3. **训练模型**
   ```bash
   python train.py
   ```

4. **启动可视化界面**
   ```bash
   streamlit run app.py
   ```

5. **使用界面**
   - 点击 "一键加载模型" 加载训练好的模型
   - 点击 "开始预测" 进行风险预测
   - 查看预测结果和建议

## 模型说明

- **模型结构**：CNN-LSTM+Attention 混合模型
  - CNN 提取短期波动特征
  - LSTM 学习时间序列长期依赖
  - Attention 自动关注重要时间步

- **特征工程**：
  - 股票数据：close_stock, open_stock, high_stock, low_stock
  - 黄金数据：close_gold, open_gold, high_gold, low_gold
  - 技术指标：MA5_stock, MA20_stock, volatility

- **标签定义**：
  - 次日跌幅 > 1.5% → label=1（风险）
  - 否则 → label=0（正常）

## 注意事项

- 确保网络连接正常，以便下载数据
- 首次运行需要下载数据和训练模型，可能需要较长时间
- 模型训练需要一定的计算资源，建议在具有 GPU 的环境下运行
- 预测结果仅供参考，不构成投资建议
