import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import akshare as ak
from predict import predict_risk

# 设置页面配置
st.set_page_config(
    page_title="A 股风险预测系统",
    page_icon="📈",
    layout="centered"
)

# 页面标题
st.title("A 股风险预测系统")
st.subheader("基于 CNN-LSTM+Attention 混合模型的风险预测")

# 侧边栏 - 数据选择
st.sidebar.title("数据选择")
data_type = st.sidebar.selectbox("选择数据类型", ["黄金", "股票"])

# 股票选择
stock_symbol = "sh000300"  # 默认沪深300
if data_type == "股票":
    stock_option = st.sidebar.selectbox(
        "选择股票",
        ["沪深300 (sh000300)", "上证指数 (sh000001)", "深证成指 (sz399001)", "创业板指 (sz399006)"]
    )
    if stock_option == "沪深300 (sh000300)":
        stock_symbol = "sh000300"
    elif stock_option == "上证指数 (sh000001)":
        stock_symbol = "sh000001"
    elif stock_option == "深证成指 (sz399001)":
        stock_symbol = "sz399001"
    elif stock_option == "创业板指 (sz399006)":
        stock_symbol = "sz399006"

# 模型加载状态
model_loaded = False

# 加载模型按钮
if st.button("一键加载模型"):
    try:
        from tensorflow.keras.models import load_model
        import joblib
        
        # 加载模型和scaler
        model = load_model('models/best_model.h5')
        scaler = joblib.load('models/scaler.pkl')
        
        st.success("模型加载成功！")
        model_loaded = True
    except Exception as e:
        st.error(f"模型加载失败：{e}")

# 开始预测按钮
if st.button("开始预测"):
    with st.spinner("正在获取最新数据并预测..."):
        if data_type == "股票":
            # 显示当前预测的股票
            st.info(f"预测股票：{stock_option}")
            result = predict_risk(data_type="股票", stock_symbol=stock_symbol)
        else:
            # 显示当前预测的是黄金风险
            st.info("预测黄金市场风险")
            result = predict_risk(data_type="黄金")
        
        if result:
            # 展示预测结果
            st.success("预测完成！")
            
            # 风险概率
            risk_prob = result['risk_prob']
            st.metric(label="风险概率", value=f"{risk_prob:.2%}")
            
            # 预测结论
            prediction = "有风险" if result['risk_prediction'] == 1 else "安全"
            if prediction == "有风险":
                st.error(f"预测结论：{prediction}")
            else:
                st.success(f"预测结论：{prediction}")
            
            # 建议
            st.info(f"建议：{result['suggestion']}")
            
            # 原因分析
            st.markdown("### 原因分析")
            for i, reason in enumerate(result['reasons'], 1):
                st.markdown(f"{i}. {reason}")
        else:
            st.error("预测失败，请检查数据是否充足")

# 数据可视化
st.markdown("---")
st.subheader("数据可视化")

# 加载并显示数据
if st.button("加载数据"):
    with st.spinner("正在加载数据..."):
        if data_type == "黄金":
            # 加载黄金数据
            gold_data = ak.spot_golden_benchmark_sge()
            gold_data = gold_data.rename(columns={'交易时间': 'date'})
            gold_data['date'] = pd.to_datetime(gold_data['date'])
            gold_data = gold_data.tail(60)  # 显示最近60天数据
            
            # 计算移动平均线
            gold_data['MA5'] = gold_data['晚盘价'].rolling(window=5).mean()
            gold_data['MA20'] = gold_data['晚盘价'].rolling(window=20).mean()
            
            # 使用 Plotly 创建交互式图表
            fig = go.Figure()
            
            # 添加收盘价
            fig.add_trace(go.Scatter(
                x=gold_data['date'],
                y=gold_data['晚盘价'],
                mode='lines+markers',
                name='晚盘价',
                line=dict(color='blue', width=2),
                marker=dict(size=4),
                hovertemplate='<b>日期</b>: %{x}<br><b>早盘价</b>: %{customdata[0]:.2f}<br><b>晚盘价</b>: %{y:.2f}<br><b>5日均线</b>: %{customdata[1]:.2f}<br><b>20日均线</b>: %{customdata[2]:.2f}<extra></extra>',
                customdata=np.column_stack([gold_data['早盘价'], gold_data['MA5'], gold_data['MA20']])
            ))
            
            # 添加开盘价
            fig.add_trace(go.Scatter(
                x=gold_data['date'],
                y=gold_data['早盘价'],
                mode='lines+markers',
                name='早盘价',
                line=dict(color='green', width=2),
                marker=dict(size=4),
                hovertemplate='<b>日期</b>: %{x}<br><b>早盘价</b>: %{y:.2f}<br><b>晚盘价</b>: %{customdata[0]:.2f}<br><b>5日均线</b>: %{customdata[1]:.2f}<br><b>20日均线</b>: %{customdata[2]:.2f}<extra></extra>',
                customdata=np.column_stack([gold_data['晚盘价'], gold_data['MA5'], gold_data['MA20']])
            ))
            
            # 添加5日均线
            fig.add_trace(go.Scatter(
                x=gold_data['date'],
                y=gold_data['MA5'],
                mode='lines',
                name='5日均线',
                line=dict(color='orange', width=1, dash='dash'),
                hovertemplate='<b>日期</b>: %{x}<br><b>早盘价</b>: %{customdata[0]:.2f}<br><b>晚盘价</b>: %{customdata[1]:.2f}<br><b>5日均线</b>: %{y:.2f}<br><b>20日均线</b>: %{customdata[2]:.2f}<extra></extra>',
                customdata=np.column_stack([gold_data['早盘价'], gold_data['晚盘价'], gold_data['MA20']])
            ))
            
            # 添加20日均线
            fig.add_trace(go.Scatter(
                x=gold_data['date'],
                y=gold_data['MA20'],
                mode='lines',
                name='20日均线',
                line=dict(color='red', width=1, dash='dash'),
                hovertemplate='<b>日期</b>: %{x}<br><b>早盘价</b>: %{customdata[0]:.2f}<br><b>晚盘价</b>: %{customdata[1]:.2f}<br><b>5日均线</b>: %{customdata[2]:.2f}<br><b>20日均线</b>: %{y:.2f}<extra></extra>',
                customdata=np.column_stack([gold_data['早盘价'], gold_data['晚盘价'], gold_data['MA5']])
            ))
            
            fig.update_layout(
                title='黄金价格走势',
                xaxis_title='日期',
                yaxis_title='价格',
                hovermode='closest',
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=16,
                    font_family="Arial",
                    bordercolor="black",
                    align="left"
                ),
                margin=dict(l=30, r=30, t=50, b=30),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                width=1600,
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 显示数据表格
            st.subheader("数据详情")
            st.dataframe(gold_data.tail(10))
        else:
            # 加载股票数据
            stock_data = ak.stock_zh_index_daily(symbol=stock_symbol)
            stock_data['date'] = pd.to_datetime(stock_data['date'])
            stock_data = stock_data.tail(60)  # 显示最近60天数据
            
            # 计算移动平均线
            stock_data['MA5'] = stock_data['close'].rolling(window=5).mean()
            stock_data['MA20'] = stock_data['close'].rolling(window=20).mean()
            
            # 使用 Plotly 创建交互式图表
            fig = go.Figure()
            
            # 添加收盘价
            fig.add_trace(go.Scatter(
                x=stock_data['date'],
                y=stock_data['close'],
                mode='lines+markers',
                name='收盘价',
                line=dict(color='blue', width=2),
                marker=dict(size=4),
                hovertemplate='<b>日期</b>: %{x}<br><b>收盘价</b>: %{y:.2f}<br><b>5日均线</b>: %{customdata[0]:.2f}<br><b>20日均线</b>: %{customdata[1]:.2f}<extra></extra>',
                customdata=np.column_stack([stock_data['MA5'], stock_data['MA20']])
            ))
            
            # 添加5日均线
            fig.add_trace(go.Scatter(
                x=stock_data['date'],
                y=stock_data['MA5'],
                mode='lines',
                name='5日均线',
                line=dict(color='orange', width=1, dash='dash'),
                hovertemplate='<b>日期</b>: %{x}<br><b>收盘价</b>: %{customdata[0]:.2f}<br><b>5日均线</b>: %{y:.2f}<br><b>20日均线</b>: %{customdata[1]:.2f}<extra></extra>',
                customdata=np.column_stack([stock_data['close'], stock_data['MA20']])
            ))
            
            # 添加20日均线
            fig.add_trace(go.Scatter(
                x=stock_data['date'],
                y=stock_data['MA20'],
                mode='lines',
                name='20日均线',
                line=dict(color='red', width=1, dash='dash'),
                hovertemplate='<b>日期</b>: %{x}<br><b>收盘价</b>: %{customdata[0]:.2f}<br><b>5日均线</b>: %{customdata[1]:.2f}<br><b>20日均线</b>: %{y:.2f}<extra></extra>',
                customdata=np.column_stack([stock_data['close'], stock_data['MA5']])
            ))
            
            fig.update_layout(
                title=f'{stock_option} 价格走势',
                xaxis_title='日期',
                yaxis_title='价格',
                hovermode='closest',
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=16,
                    font_family="Arial",
                    bordercolor="black",
                    align="left"
                ),
                margin=dict(l=20, r=20, t=40, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                width=1600,
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 显示数据表格
            st.subheader("数据详情")
            st.dataframe(stock_data.tail(10))

# 风险分析解释
st.markdown("---")
st.subheader("风险分析")

# 为什么会降？
st.markdown("### 为什么会降？")
st.markdown("1. **市场情绪**：当市场整体情绪悲观时，投资者会大量抛售股票，导致股价下跌")
st.markdown("2. **经济数据**：如GDP、CPI、PPI等经济数据不佳，会影响投资者信心")
st.markdown("3. **政策变化**：宏观经济政策、行业政策的变化可能对市场产生负面影响")
st.markdown("4. **外部冲击**：国际市场波动、地缘政治风险等外部因素可能传导至A股")
st.markdown("5. **技术面**：股价突破重要支撑位，技术指标发出卖出信号")

# 为什么不会降？
st.markdown("### 为什么不会降？")
st.markdown("1. **基本面支撑**：公司业绩良好，估值合理，有基本面支撑")
st.markdown("2. **政策利好**：政府出台刺激经济、支持资本市场的政策")
st.markdown("3. **资金流入**：北向资金、机构资金持续流入，提供流动性支持")
st.markdown("4. **技术面**：股价在重要支撑位企稳，技术指标发出买入信号")
st.markdown("5. **市场情绪**：市场整体情绪乐观，投资者信心充足")

# 页面底部信息
st.markdown("---")
st.markdown("### 系统说明")
st.markdown("- 使用 CNN-LSTM+Attention 混合模型")
st.markdown("- 根据过去 30 天历史数据预测")
st.markdown("- 预测下一天是否出现大于 1.5% 的大跌风险")
st.markdown("- 数据来源：akshare")
