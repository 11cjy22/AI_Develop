#!/bin/bash

echo "🚀 AI金融风险预测系统 - 快速启动"
echo "=================================="
echo ""

# 检查是否已有数据
if [ ! -f "data/合成后数据_改进版.csv" ]; then
    echo "📥 第一次运行，需要下载和处理数据..."
    echo ""
    
    echo "⏳ 步骤1/3: 下载数据（需要几分钟）..."
    python3 data_download_improved.py
    echo ""
    
    echo "⏳ 步骤2/3: 处理数据..."
    python3 data_process_improved.py
    echo ""
    
    echo "⏳ 步骤3/3: 训练模型（需要10-30分钟，取决于硬件）..."
    python3 train_improved.py
    echo ""
else
    echo "✅ 检测到已有数据和模型"
    echo ""
fi

echo "🎨 启动漂亮前端界面..."
echo "💡 提示: 浏览器会自动打开 http://localhost:8501"
echo ""

streamlit run app_beautiful.py
