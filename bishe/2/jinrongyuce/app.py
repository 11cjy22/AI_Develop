import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import akshare as ak
from predict import predict_risk

# 页面配置
st.set_page_config(
    page_title="A股风险预测系统",
    page_icon="📈",
    layout="wide"
)

# 自定义样式
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        height: 3em;
        font-size: 16px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 初始化 session state
if 'model_loaded' not in st.session_state:
    st.session_state.model_loaded = False
if 'prediction_result' not in st.session_state:
    st.session_state.prediction_result = None
if 'predict_info' not in st.session_state:
    st.session_state.predict_info = None
if 'chart_data' not in st.session_state:
    st.session_state.chart_data = None
if 'chart_type' not in st.session_state:
    st.session_state.chart_type = None

# 主标题
st.title("📈 A 股风险预测系统")
st.markdown("基于 CNN-LSTM+Attention 混合模型的风险预测")
st.divider()

# 侧边栏
with st.sidebar:
    st.title("数据选择")
    data_type = st.selectbox("选择数据类型", ["黄金", "股票"])

    stock_symbol = "sh000300"
    stock_option = "沪深300"

    if data_type == "股票":
        stock_option = st.selectbox(
            "选择指数",
            ["沪深300", "上证指数", "深证成指", "创业板指"]
        )
        stock_map = {
            "沪深300": "sh000300",
            "上证指数": "sh000001",
            "深证成指": "sz399001",
            "创业板指": "sz399006"
        }
        stock_symbol = stock_map[stock_option]

# 模型区域
st.subheader("🔧 模型操作")

# 按钮 1：加载模型
if st.button("✅ 一键加载模型"):
    try:
        from tensorflow.keras.models import load_model
        import joblib
        model = load_model('models/best_model.h5')
        scaler = joblib.load('models/scaler.pkl')
        st.session_state.model_loaded = True
        st.success("模型加载成功！")
    except Exception as e:
        st.error(f"模型加载失败：{e}")

# 按钮 2：开始预测
if st.button("🚀 开始风险预测"):
    # 提示信息
    if data_type == "股票":
        msg = f"预测标的：{stock_option}"
    else:
        msg = "预测标的：黄金"

    st.session_state.predict_info = msg
    st.info(msg)

    # 预测
    with st.spinner("正在获取数据并预测..."):
        try:
            if data_type == "股票":
                res = predict_risk(data_type="股票", stock_symbol=stock_symbol)
            else:
                res = predict_risk(data_type="黄金")
            st.session_state.prediction_result = res
        except Exception as e:
            st.error(f"预测出错：{e}")
            st.session_state.prediction_result = None

# 预测结果直接展示在按钮下方
if st.session_state.prediction_result is not None:
    result = st.session_state.prediction_result

    st.success("✅ 预测完成")

    # 风险概率
    risk_prob = result['risk_prob']
    st.metric("风险概率", f"{risk_prob:.2%}")

    # 结论
    prediction = "有风险" if result['risk_prediction'] == 1 else "安全"
    if prediction == "有风险":
        st.error(f"预测结论：{prediction}")
    else:
        st.success(f"预测结论：{prediction}")

    # 建议
    st.info(f"投资建议：{result['suggestion']}")

    # 原因
    st.markdown("### 📊 原因分析")
    for i, reason in enumerate(result['reasons'], 1):
        st.markdown(f"{i}. {reason}")

st.divider()

# 数据可视化
st.subheader("📊 数据走势")

# 按钮 3：加载数据
if st.button("📥 加载历史走势数据"):
    with st.spinner("加载数据中..."):
        try:
            if data_type == "黄金":
                gold_data = ak.spot_golden_benchmark_sge()
                gold_data = gold_data.rename(columns={'交易时间': 'date'})
                gold_data['date'] = pd.to_datetime(gold_data['date'])
                gold_data = gold_data.tail(60)
                gold_data['MA5'] = gold_data['晚盘价'].rolling(5).mean()
                gold_data['MA20'] = gold_data['晚盘价'].rolling(20).mean()

                st.session_state.chart_data = gold_data
                st.session_state.chart_type = "黄金"

            else:
                stock_data = ak.stock_zh_index_daily(symbol=stock_symbol)
                stock_data['date'] = pd.to_datetime(stock_data['date'])
                stock_data = stock_data.tail(60)
                stock_data['MA5'] = stock_data['close'].rolling(5).mean()
                stock_data['MA20'] = stock_data['close'].rolling(20).mean()

                st.session_state.chart_data = stock_data
                st.session_state.chart_type = "股票"

            st.success("数据加载完成")
        except Exception as e:
            st.error(f"数据加载失败：{e}")

# 图表展示
if st.session_state.chart_data is not None:
    data = st.session_state.chart_data
    chart_type = st.session_state.chart_type

    fig = go.Figure()

    if chart_type == "黄金":
        fig.add_trace(go.Scatter(x=data['date'], y=data['晚盘价'], name='晚盘价'))
        fig.add_trace(go.Scatter(x=data['date'], y=data['MA5'], name='MA5', line=dict(dash='dash')))
        fig.add_trace(go.Scatter(x=data['date'], y=data['MA20'], name='MA20', line=dict(dash='dash')))
    else:
        fig.add_trace(go.Scatter(x=data['date'], y=data['close'], name='收盘价'))
        fig.add_trace(go.Scatter(x=data['date'], y=data['MA5'], name='MA5', line=dict(dash='dash')))
        fig.add_trace(go.Scatter(x=data['date'], y=data['MA20'], name='MA20', line=dict(dash='dash')))

    fig.update_layout(height=500, title="价格走势")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(data.tail(10), use_container_width=True)

st.divider()

# 底部说明
st.caption("本系统仅供学习参考，不构成投资建议 | 数据来源：akshare")