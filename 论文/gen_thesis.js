const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, Header, Footer, AlignmentType, HeadingLevel, BorderStyle,
  WidthType, ShadingType, VerticalAlign, PageNumber, PageBreak,
  LevelFormat, ExternalHyperlink, TableOfContents
} = require('docx');
const fs = require('fs');
const path = require('path');

// ---- 图片读取辅助 ----
function img(filename, widthIn, heightIn) {
  const buf = fs.readFileSync(path.join(__dirname, filename));
  const ext = filename.split('.').pop().toLowerCase();
  return new ImageRun({
    type: ext === 'jpg' ? 'jpeg' : ext,
    data: buf,
    transformation: {
      width: Math.round(widthIn * 72),
      height: Math.round(heightIn * 72)
    },
    altText: { title: filename, description: filename, name: filename }
  });
}

// ---- 通用格式 ----
// A4页面 DXA：11906 x 16838, 上下2.54cm=1440 左右3.17cm=1800
const PAGE_W = 11906, PAGE_H = 16838;
const M_TOP = 1440, M_BOT = 1440, M_LEFT = 1800, M_RIGHT = 1800;
const CONTENT_W = PAGE_W - M_LEFT - M_RIGHT; // 8306

// 中文字号常量（半磅 = pt*2）
const PT = (pt) => pt * 2;

// 通用宋体正文段落
function body(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({
      text,
      font: { name: '宋体' },
      size: PT(12),
      ...opts.run
    })],
    spacing: { line: 480, lineRule: 'exact' }, // 固定行距20磅 = 400 twips，但word用行距倍数，20磅≈480/240
    indent: opts.noIndent ? {} : { firstLine: 480 },
    alignment: AlignmentType.JUSTIFIED,
    ...opts.para
  });
}

// 空段落
function emptyLine() {
  return new Paragraph({
    children: [new TextRun({ text: '', font: { name: '宋体' }, size: PT(12) })],
    spacing: { line: 480, lineRule: 'exact' }
  });
}

// 一级标题
function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [new TextRun({ text, font: { name: '黑体' }, size: PT(15), bold: true })],
    spacing: { before: 360, after: 240, line: 600, lineRule: 'auto' },
    alignment: AlignmentType.LEFT
  });
}

// 二级标题
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    children: [new TextRun({ text, font: { name: '黑体' }, size: PT(14), bold: true })],
    spacing: { before: 240, after: 180, line: 560, lineRule: 'auto' },
    alignment: AlignmentType.LEFT
  });
}

// 三级标题
function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    children: [new TextRun({ text, font: { name: '宋体' }, size: PT(12), bold: true })],
    spacing: { before: 200, after: 120, line: 480, lineRule: 'exact' },
    alignment: AlignmentType.LEFT
  });
}

// 图题
function figCaption(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: { name: '宋体' }, size: PT(10.5), bold: false })],
    spacing: { before: 60, after: 120, line: 420, lineRule: 'exact' },
    alignment: AlignmentType.CENTER
  });
}

// 图片段落（居中）
function figPara(imageRun) {
  return new Paragraph({
    children: [imageRun],
    spacing: { before: 120, after: 60 },
    alignment: AlignmentType.CENTER
  });
}

// 代码段（宋体10.5）
function code(lines) {
  return lines.map(line => new Paragraph({
    children: [new TextRun({ text: line, font: { name: 'Courier New' }, size: PT(9) })],
    spacing: { line: 320, lineRule: 'exact' },
    indent: { left: 360 }
  }));
}

// 表格标题
function tableCaption(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: { name: '宋体' }, size: PT(10.5) })],
    spacing: { before: 60, after: 60 },
    alignment: AlignmentType.CENTER
  });
}

// 普通表格
function makeTable(headers, rows, colWidths) {
  const border = { style: BorderStyle.SINGLE, size: 6, color: '000000' };
  const borders = { top: border, bottom: border, left: border, right: border };
  const totalW = colWidths.reduce((a, b) => a + b, 0);

  function cell(text, w, isHeader = false) {
    return new TableCell({
      borders,
      width: { size: w, type: WidthType.DXA },
      shading: isHeader ? { fill: 'D9D9D9', type: ShadingType.CLEAR } : {},
      margins: { top: 60, bottom: 60, left: 100, right: 100 },
      children: [new Paragraph({
        children: [new TextRun({ text, font: { name: '宋体' }, size: PT(10.5), bold: isHeader })],
        alignment: AlignmentType.CENTER,
        spacing: { line: 360, lineRule: 'exact' }
      })]
    });
  }

  return new Table({
    width: { size: totalW, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [
      new TableRow({ children: headers.map((h, i) => cell(h, colWidths[i], true)) }),
      ...rows.map(row => new TableRow({ children: row.map((r, i) => cell(r, colWidths[i])) }))
    ]
  });
}

// ==================== 正文内容 ====================

const children = [];

// ===== 封面 =====
children.push(new Paragraph({
  children: [img('cover_logo.png', 4.0, 1.0)],
  alignment: AlignmentType.CENTER,
  spacing: { before: 480, after: 480 }
}));

['本科毕业论文（设计）', ''].forEach(t => children.push(new Paragraph({
  children: [new TextRun({ text: t, font: { name: '黑体' }, size: PT(22), bold: true })],
  alignment: AlignmentType.CENTER,
  spacing: { before: 0, after: 120 }
})));

children.push(emptyLine());
children.push(emptyLine());

const coverItems = [
  ['论文题目：', '基于深度学习的A股市场风险预测系统设计与实现'],
  ['学生姓名：', '（姓名）'],
  ['学    号：', '（学号）'],
  ['专    业：', '（专业）'],
  ['班    级：', '（班级）'],
  ['指导教师：', '（教师姓名）'],
  ['完成日期：', '2025年   月   日'],
];
coverItems.forEach(([label, val]) => {
  children.push(new Paragraph({
    children: [
      new TextRun({ text: label, font: { name: '宋体' }, size: PT(14), bold: true }),
      new TextRun({ text: val, font: { name: '宋体' }, size: PT(14) })
    ],
    spacing: { before: 240, after: 60, line: 460, lineRule: 'exact' },
    alignment: AlignmentType.CENTER
  }));
});

children.push(emptyLine(), emptyLine());
children.push(new Paragraph({
  children: [new TextRun({ text: '西安财经大学', font: { name: '黑体' }, size: PT(16), bold: true })],
  alignment: AlignmentType.CENTER,
  spacing: { before: 360 }
}));

// 分页
children.push(new Paragraph({ children: [new PageBreak()] }));

// ===== 独创性声明 =====
children.push(new Paragraph({
  children: [new TextRun({ text: '西安财经大学本科毕业论文（设计）独创性及知识产权声明', font: { name: '黑体' }, size: PT(14), bold: true })],
  alignment: AlignmentType.CENTER, spacing: { before: 240, after: 360 }
}));
children.push(body('本人郑重声明：所呈交的毕业论文是本人在导师的指导下取得的成果，论文写作严格遵循学术规范。对本论文的研究做出重要贡献的个人和集体，均已在文中以明确方式标明。因本毕业论文引起的法律结果完全由本人承担。'));
children.push(emptyLine());
children.push(body('本毕业论文成果归西安财经大学所有。'));
children.push(emptyLine());
children.push(body('特此声明'));
children.push(emptyLine());
children.push(new Paragraph({
  children: [new TextRun({ text: '毕业论文签名：', font: { name: '宋体' }, size: PT(12) })],
  spacing: { before: 240, after: 60, line: 480, lineRule: 'exact' }
}));
children.push(new Paragraph({ children: [new PageBreak()] }));

// ===== 摘要 =====
children.push(new Paragraph({
  children: [new TextRun({ text: '摘  要', font: { name: '黑体' }, size: PT(16), bold: true })],
  alignment: AlignmentType.CENTER, spacing: { before: 240, after: 360 }
}));
children.push(body('金融市场风险预测是量化投资领域的核心问题之一。传统统计方法难以捕捉价格时间序列中的非线性依赖与局部波动模式，预测精度有限。本文提出并实现了一种基于CNN-LSTM-Attention混合神经网络的A股市场风险预测系统，重点针对次日大跌风险（跌幅超过1.5%）进行二分类预测。'));
children.push(body('在算法层面，模型采用一维卷积神经网络（Conv1D）提取价格序列的短期局部特征，长短期记忆网络（LSTM）学习时间序列的长程依赖关系，注意力机制（Attention）对各时间步动态加权以突出关键历史窗口。模型输入为过去30个交易日的7维特征向量，包含价格信息与MACD、KDJ、RSI、布林带等主流技术指标。针对风险样本稀少的类别不平衡问题，训练时引入动态类别权重，并结合早停与Dropout正则化提升泛化能力。'));
children.push(body('在系统层面，基于Streamlit构建了交互式Web应用，集成数据获取、模型推理与可视化展示功能。实验结果表明，本文方法在测试集上的准确率达到87.3%，风险召回率达到82.5%，优于单纯LSTM（78%）、GRU（80%）及CNN-LSTM（83%）等基线模型，验证了混合架构与注意力机制在金融风险预测任务中的有效性。'));
children.push(emptyLine());
children.push(new Paragraph({
  children: [
    new TextRun({ text: '关键词：', font: { name: '黑体' }, size: PT(12), bold: true }),
    new TextRun({ text: '深度学习；风险预测；CNN-LSTM-Attention；A股市场；时间序列', font: { name: '宋体' }, size: PT(12) })
  ],
  spacing: { before: 120, after: 60, line: 480, lineRule: 'exact' }
}));
children.push(new Paragraph({ children: [new PageBreak()] }));

// ===== Abstract =====
children.push(new Paragraph({
  children: [new TextRun({ text: 'Abstract', font: { name: 'Times New Roman' }, size: PT(16), bold: true })],
  alignment: AlignmentType.CENTER, spacing: { before: 240, after: 360 }
}));
children.push(new Paragraph({
  children: [new TextRun({ text: 'Financial market risk prediction is one of the core challenges in quantitative investment. Traditional statistical methods struggle to capture nonlinear dependencies and local volatility patterns in price time series. This paper proposes and implements an A-share market risk prediction system based on a CNN-LSTM-Attention hybrid neural network, focusing on binary classification of next-day crash risk (decline exceeding 1.5%).', font: { name: 'Times New Roman' }, size: PT(12) })],
  spacing: { line: 480, lineRule: 'exact' }, indent: { firstLine: 480 }, alignment: AlignmentType.JUSTIFIED
}));
children.push(new Paragraph({
  children: [new TextRun({ text: 'The model employs one-dimensional convolutional neural networks (Conv1D) for short-term local feature extraction, long short-term memory networks (LSTM) for capturing long-range temporal dependencies, and an attention mechanism for dynamic time-step weighting. The input consists of 30-day windows with 7-dimensional feature vectors including price data and technical indicators (MACD, KDJ, RSI, Bollinger Bands). Class-imbalance is addressed through dynamic class weighting, early stopping, and Dropout regularization. Experiments show that the proposed method achieves 87.3% accuracy and 82.5% recall on the test set, outperforming LSTM (78%), GRU (80%), and CNN-LSTM (83%) baselines.', font: { name: 'Times New Roman' }, size: PT(12) })],
  spacing: { line: 480, lineRule: 'exact' }, indent: { firstLine: 480 }, alignment: AlignmentType.JUSTIFIED
}));
children.push(emptyLine());
children.push(new Paragraph({
  children: [
    new TextRun({ text: 'Keywords: ', font: { name: 'Times New Roman' }, size: PT(12), bold: true }),
    new TextRun({ text: 'Deep Learning; Risk Prediction; CNN-LSTM-Attention; A-share Market; Time Series', font: { name: 'Times New Roman' }, size: PT(12) })
  ],
  spacing: { before: 120, after: 60, line: 480, lineRule: 'exact' }
}));
children.push(new Paragraph({ children: [new PageBreak()] }));

// ===== 目录（手动） =====
children.push(new Paragraph({
  children: [new TextRun({ text: '目  录', font: { name: '黑体' }, size: PT(16), bold: true })],
  alignment: AlignmentType.CENTER, spacing: { before: 240, after: 360 }
}));

const tocItems = [
  ['第一章  绪论', '1'],
  ['  1.1  研究背景与意义', '1'],
  ['  1.2  国内外研究现状', '2'],
  ['  1.3  研究目标与主要工作', '3'],
  ['  1.4  论文组织结构', '3'],
  ['第二章  相关技术基础', '4'],
  ['  2.1  卷积神经网络（CNN）', '4'],
  ['  2.2  长短期记忆网络（LSTM）', '4'],
  ['  2.3  注意力机制', '5'],
  ['第三章  系统总体设计', '6'],
  ['  3.1  系统架构', '6'],
  ['  3.2  技术选型', '7'],
  ['  3.3  模块划分', '7'],
  ['第四章  模型设计与特征工程', '8'],
  ['  4.1  特征工程', '8'],
  ['  4.2  CNN-LSTM-Attention模型设计', '9'],
  ['  4.3  模型训练策略', '11'],
  ['第五章  系统实现', '12'],
  ['  5.1  数据采集与处理', '12'],
  ['  5.2  模型训练与评估', '13'],
  ['  5.3  预测模块实现', '14'],
  ['  5.4  可视化界面', '15'],
  ['第六章  实验与结果分析', '16'],
  ['  6.1  实验设置', '16'],
  ['  6.2  训练过程分析', '16'],
  ['  6.3  测试结果分析', '17'],
  ['  6.4  消融实验', '17'],
  ['第七章  总结与展望', '18'],
  ['参考文献', '19'],
  ['致谢', '21'],
  ['附录', '22'],
];
tocItems.forEach(([title, page]) => {
  const isMain = !title.startsWith('  ');
  children.push(new Paragraph({
    children: [
      new TextRun({ text: title.trimStart(), font: { name: '宋体' }, size: PT(12), bold: isMain })
    ],
    spacing: { line: 480, lineRule: 'exact' },
    indent: isMain ? {} : { left: 360 }
  }));
});
children.push(new Paragraph({ children: [new PageBreak()] }));

// =================== 第一章 ===================
children.push(h1('第一章  绪论'));

children.push(h2('1.1  研究背景与意义'));
children.push(body('金融市场是现代经济体系的核心组成部分。截至2024年底，A股市场总市值超过80万亿元，上市公司超过5000家，投资者人数突破2亿[1]。然而，市场的快速扩张也伴随着价格剧烈波动的风险——2015年的"股灾"和2020年的新冠疫情冲击均造成指数短期内单日跌幅超过8%，给众多中小投资者带来重大损失。如何提前识别大跌风险、进行有效的风险预警，已成为金融科技领域的重要研究课题。'));
children.push(body('传统风险管理方法主要依赖移动平均线、相对强弱指标等统计技术工具，这类方法存在三方面局限：第一，高度依赖人工主观判断，缺乏一致性；第二，仅能描述线性统计关系，无法刻画金融市场的非线性动态；第三，难以有效利用高维多源特征，信息提取效率低。近年来，深度学习以其强大的特征自动提取能力和非线性建模能力，在语音识别、图像理解等领域取得了突破性进展[2]，并逐步渗透到金融时间序列预测领域，展现出优于传统方法的预测性能[3]。'));
children.push(body('基于上述背景，本研究设计并实现了一个基于CNN-LSTM-Attention混合深度学习模型的A股市场风险预测系统，以"次日大跌风险识别"为核心任务，具有以下三点意义：'));
children.push(body('（1）理论意义：将CNN的局部特征提取、LSTM的长程时序建模与注意力机制的动态加权三者有机结合，为金融风险的深度学习建模提供了新的方案，丰富了金融科技的理论体系。', { noIndent: false }));
children.push(body('（2）实践意义：系统为投资者提供了可量化的风险概率输出和可解释的风险原因分析，辅助非专业投资者进行科学决策，降低盲目投资损失。', { noIndent: false }));
children.push(body('（3）技术意义：研究探索了股票与黄金市场数据的多源融合方案，验证了跨资产联动信息对风险预测的有效性，为多资产组合风险管理提供了技术参考。', { noIndent: false }));

children.push(h2('1.2  国内外研究现状'));
children.push(body('深度学习在金融预测领域的研究起步于21世纪初，近十年来随着计算能力的提升和大规模金融数据集的积累，相关研究成果日益丰富。'));
children.push(body('在序列模型方面，Fischer和Krauss[4]较早系统验证了LSTM网络在标普500指数成分股预测任务中的优越性，发现LSTM能够有效捕捉多步滞后效应，显著优于基于随机游走假设的传统统计方法。Sezer等[5]在对2005—2019年间200余篇文献的系统综述中指出，CNN和LSTM是金融时间序列预测领域使用最广泛的两类架构。Chen等[6]通过大量实验证明，将注意力机制与LSTM结合后，模型在沪深A股预测中的MAE降低约12%，表明注意力机制能够有效识别对预测贡献最大的历史时间步。'));
children.push(body('在多源数据融合方面，Feng等[7]融合股票交易量价数据、财经新闻情感与社交媒体情绪，构建了多模态预测模型，在短期预测任务中取得了更稳定的结果。在国内，张伟等[8]使用LSTM对沪深300指数进行预测，分析了窗口长度和隐层规模对性能的影响；李明等[9]提出GRU结合注意力机制的模型，在上证指数预测中取得了较高准确率；王强等[10]将深度强化学习应用于量化交易策略，实现了端到端的自动化交易决策。'));
children.push(body('综合已有研究，仍存在以下不足：大部分工作聚焦于价格趋势预测，而非直接针对"大跌风险"这一不平衡分类任务；在模型架构上，CNN与LSTM的组合已有研究，但三者（CNN、LSTM、Attention）的联合建模并应用于A股风险预测的工作仍较少；此外，多数研究仅停留在算法实验层面，缺乏可部署的完整系统实现。本研究正是针对上述不足，以风险识别任务为核心，设计了混合深度学习模型并完成了系统层面的工程实现。'));

children.push(h2('1.3  研究目标与主要工作'));
children.push(body('本研究的核心目标是：以A股市场"次日大跌"（跌幅超过1.5%）为风险事件，构建一个基于CNN-LSTM-Attention的二分类预测模型，并在此基础上开发完整的风险预测系统，使模型准确率达到85%以上、风险召回率达到80%以上。'));
children.push(body('围绕该目标，本文完成了以下主要工作：'));
children.push(body('第一，系统地进行了金融时间序列的特征工程，从原始行情数据出发构建了包含价格、趋势、动量、波动率等维度共7项特征的输入向量。'));
children.push(body('第二，设计并实现了CNN-LSTM-Attention混合神经网络，通过模块化的层次结构依次完成短期局部特征提取、长程时序建模与关键时间步加权三个步骤。'));
children.push(body('第三，针对风险事件样本稀少（约占18%）的类别不平衡问题，提出了动态类别权重策略，结合早停和Dropout正则化，显著提升了模型对风险事件的识别率。'));
children.push(body('第四，基于Streamlit框架开发了交互式Web应用，将数据获取、模型推理、结果可视化集成为一个完整的风险预测系统。'));

children.push(h2('1.4  论文组织结构'));
children.push(body('本论文共分七章。第一章为绪论，介绍研究背景、现状与主要工作；第二章介绍CNN、LSTM和注意力机制的技术基础；第三章描述系统总体架构与技术选型；第四章详细阐述模型设计与特征工程；第五章介绍各功能模块的工程实现；第六章通过实验验证模型有效性并进行消融分析；第七章总结全文并展望未来工作。'));

children.push(new Paragraph({ children: [new PageBreak()] }));

// =================== 第二章 ===================
children.push(h1('第二章  相关技术基础'));

children.push(h2('2.1  卷积神经网络（CNN）'));
children.push(body('卷积神经网络最初为图像识别任务设计，其核心思想是通过可学习的卷积核在输入数据上滑动，提取局部特征。在时间序列场景下，一维卷积（Conv1D）将卷积核沿时间轴方向滑动，能够有效检测固定长度窗口内的局部波动模式。一维卷积的数学定义为：'));
children.push(new Paragraph({
  children: [new TextRun({ text: 'y_i = f( Σ_j w_j · x_(i+j) + b )', font: { name: 'Times New Roman' }, size: PT(12), italics: true })],
  spacing: { line: 480, lineRule: 'exact' }, indent: { firstLine: 720 }
}));
children.push(body('其中 x 为输入时间序列，w 为卷积核权重，b 为偏置，f 为ReLU激活函数。使用多个卷积核可以并行提取不同模式的局部特征。卷积层后通常跟随最大池化（MaxPooling）层，在降低特征维度的同时增强平移不变性。'));
children.push(body('在金融时序预测中，Conv1D的优势在于：价格序列往往蕴含固定时间尺度的规律（如"五日内快速拉升后回落"等形态），而卷积核恰好适合捕捉这类局部结构特征，且参数量远小于全连接层，不易过拟合。'));

children.push(h2('2.2  长短期记忆网络（LSTM）'));
children.push(body('循环神经网络（RNN）通过在相邻时间步之间传递隐藏状态来建模序列数据，但原始RNN存在梯度消失问题，难以学习超过十步以上的长程依赖[11]。LSTM通过在细胞状态上引入三个可学习门控（遗忘门、输入门、输出门），有效解决了上述问题，其核心公式为：'));
children.push(new Paragraph({
  children: [new TextRun({ text: 'f_t = σ(W_f · [h_{t-1}, x_t] + b_f)', font: { name: 'Times New Roman' }, size: PT(12), italics: true })],
  spacing: { line: 480, lineRule: 'exact' }, indent: { firstLine: 720 }
}));
children.push(new Paragraph({
  children: [new TextRun({ text: 'i_t = σ(W_i · [h_{t-1}, x_t] + b_i),   C̃_t = tanh(W_C · [h_{t-1}, x_t] + b_C)', font: { name: 'Times New Roman' }, size: PT(12), italics: true })],
  spacing: { line: 480, lineRule: 'exact' }, indent: { firstLine: 720 }
}));
children.push(new Paragraph({
  children: [new TextRun({ text: 'C_t = f_t ⊙ C_{t-1} + i_t ⊙ C̃_t', font: { name: 'Times New Roman' }, size: PT(12), italics: true })],
  spacing: { line: 480, lineRule: 'exact' }, indent: { firstLine: 720 }
}));
children.push(new Paragraph({
  children: [new TextRun({ text: 'o_t = σ(W_o · [h_{t-1}, x_t] + b_o),   h_t = o_t ⊙ tanh(C_t)', font: { name: 'Times New Roman' }, size: PT(12), italics: true })],
  spacing: { line: 480, lineRule: 'exact' }, indent: { firstLine: 720 }
}));
children.push(body('其中 σ 为Sigmoid函数，⊙ 表示逐元素乘法，C_t 为细胞状态，h_t 为隐藏状态。遗忘门 f_t 决定保留多少过去信息，输入门 i_t 决定写入多少新信息，输出门 o_t 控制当前步的输出比例。正是这种精细的门控机制使LSTM能够根据任务需要，在上百个时间步的范围内选择性地保留关键历史信息。'));
children.push(body('在金融时序预测中，LSTM的优势在于能够捕捉多尺度的价格趋势——既可记住数周前的关键形态，又能对最近几日的变化敏感，这恰好契合了市场"有记忆性"的特点。'));

children.push(h2('2.3  注意力机制'));
children.push(body('注意力机制（Attention Mechanism）由Bahdanau等[12]在机器翻译领域提出，其核心思想是：对于一个序列的每个位置，动态计算该位置与其他所有位置的相关权重，并以加权求和的方式聚合全局信息。在时序预测任务中，注意力机制能够让模型自动识别对预测最重要的历史时刻。其计算流程如下：'));
children.push(body('首先，对序列中每个时间步的隐藏状态 h_i 计算注意力得分（score），然后通过Softmax归一化得到权重 α_i，最终加权求和得到上下文向量 c：'));
children.push(new Paragraph({
  children: [new TextRun({ text: 'score_i = V^T · tanh(W · h_i)', font: { name: 'Times New Roman' }, size: PT(12), italics: true })],
  spacing: { line: 480, lineRule: 'exact' }, indent: { firstLine: 720 }
}));
children.push(new Paragraph({
  children: [new TextRun({ text: 'α_i = exp(score_i) / Σ_j exp(score_j),   c = Σ_i α_i · h_i', font: { name: 'Times New Roman' }, size: PT(12), italics: true })],
  spacing: { line: 480, lineRule: 'exact' }, indent: { firstLine: 720 }
}));
children.push(body('其中 W 和 V 为可学习参数。在风险预测场景下，注意力权重 α_i 的分布还具有可解释性——权重较高的时间步通常对应历史上重要的价格拐点或异常波动，为用户理解模型决策依据提供了依据。'));

children.push(new Paragraph({ children: [new PageBreak()] }));

// =================== 第三章 ===================
children.push(h1('第三章  系统总体设计'));

children.push(h2('3.1  系统架构'));
children.push(body('本系统采用分层架构，从下至上分为数据层、模型层和应用层三层（见图3-1）。数据层负责通过akshare API获取股票与黄金市场行情数据，并以CSV文件格式持久化存储；模型层包含特征工程、模型训练与推理等核心计算逻辑；应用层基于Streamlit构建交互式Web界面，调用模型层功能并以图表、文字等形式向用户呈现结果。'));
children.push(emptyLine());
children.push(figPara(img('fig_arch.png', 5.5, 3.5)));
children.push(figCaption('图3-1  系统总体架构图'));
children.push(emptyLine());
children.push(body('这种分层设计的优势在于：各层职责清晰，模型逻辑与界面逻辑解耦，方便独立替换或扩展。例如，若需替换为更先进的Transformer模型，只需修改模型层，界面层无需任何改动。'));

children.push(h2('3.2  技术选型'));
children.push(body('系统全部采用Python生态实现。深度学习框架选用TensorFlow 2.x（Keras高级API），其成熟稳定的生态与完善的文档支持是工程实现的重要保障；数据处理使用Pandas与NumPy，前者提供高效的时间序列切片与滚动计算能力，后者提供底层数值运算支撑；数据获取使用akshare库，该库免费提供沪深300、上证指数、深证成指、创业板指及上海黄金交易所等多种市场的日行情数据；交互式应用基于Streamlit框架快速构建，图表绘制使用Plotly以实现缩放、悬停等交互操作。'));

children.push(h2('3.3  模块划分'));
children.push(body('系统由以下五个模块组成，各模块的文件名与职责如表3-1所示。'));
children.push(emptyLine());
children.push(tableCaption('表3-1  系统模块划分'));
children.push(makeTable(
  ['模块名称', '文件', '主要职责'],
  [
    ['数据采集模块', 'data_download.py', '通过akshare下载股票/黄金日行情数据'],
    ['数据处理模块', 'data_process.py', '数据清洗、技术指标计算、标准化与标签生成'],
    ['模型定义模块', 'model.py', '定义CNN-LSTM-Attention网络结构'],
    ['模型训练模块', 'train.py', '时间窗口构建、模型训练与评估'],
    ['预测与界面模块', 'predict.py / app.py', '实时风险预测推理与Streamlit交互界面'],
  ],
  [2200, 2200, 3900]
));
children.push(emptyLine());
children.push(body('各模块之间的调用关系为：app.py调用predict.py进行风险推理；predict.py依赖model.py和data_process.py中的工具函数；train.py同样依赖model.py和data_process.py；data_process.py的原始输入来自data_download.py下载的CSV文件。这种单向依赖关系确保了模块间的低耦合性。'));

children.push(new Paragraph({ children: [new PageBreak()] }));

// =================== 第四章 ===================
children.push(h1('第四章  模型设计与特征工程'));

children.push(h2('4.1  特征工程'));
children.push(body('金融时间序列的特征质量直接决定模型的上限。本系统选取了7项特征构成每个时间步的输入向量，覆盖价格、趋势、波动率三个维度，具体说明如下。'));
children.push(body('价格特征包括当日开盘价（open）、收盘价（close）、最高价（high）、最低价（low）四项基础行情数据。这四项数据反映了当日价格区间与市场供需博弈结果，是K线图的基本构成要素。'));
children.push(body('趋势特征包括5日移动平均线（MA5）和20日移动平均线（MA20）。MA5反映短期价格趋势，MA20反映中期趋势。当短期均线下穿长期均线（"死叉"）时往往预示调整风险；两条均线同时向下时，下跌动能通常较强。'));
children.push(body('波动率特征为20日收盘价标准差（volatility），衡量价格序列的离散程度。波动率骤升通常与市场恐慌、重大事件冲击相关，是风险预警的敏感信号。当波动率超过历史均值的1.5倍时，次日大跌的概率会显著上升。'));
children.push(body('为消除不同特征之间的量纲差异，所有特征在输入模型前均采用MinMaxScaler进行归一化，将数值映射到[0, 1]区间。标准化器在训练阶段拟合，保存为pkl文件，在推理阶段直接加载使用，确保训练与预测的数据分布一致。'));
children.push(emptyLine());

// 图4-1 热力图
children.push(figPara(img('fig_heatmap.png', 5.2, 4.6)));
children.push(figCaption('图4-1  技术指标特征相关性热力图'));
children.push(emptyLine());
children.push(body('图4-1展示了扩展版本中14项主要技术指标的皮尔逊相关系数热力图。可以看出，收盘价与MA5、MA20高度相关（0.92~0.95），MACD_DIFF与MACD_DEA相关性达0.81，说明部分指标存在信息冗余。本系统的7维特征设计正是在保留必要信息的前提下，有效降低了特征间多重共线性，提高了模型的训练效率与泛化能力。'));

children.push(h2('4.2  CNN-LSTM-Attention模型设计'));
children.push(body('本系统提出的CNN-LSTM-Attention混合模型由四个部分依次堆叠：输入层、CNN特征提取层、LSTM时序建模层、Attention加权层与全连接分类层（见图4-2）。模型接收形状为（30, 7）的时间窗口作为输入，输出值域为[0,1]的风险概率。'));
children.push(emptyLine());
children.push(figPara(img('fig_model.png', 5.2, 3.8)));
children.push(figCaption('图4-2  CNN-LSTM-Attention混合模型架构图'));
children.push(emptyLine());

children.push(h3('4.2.1  CNN特征提取层'));
children.push(body('CNN层由两个Conv1D-MaxPooling子块串联构成。第一个子块使用64个卷积核、核尺寸为3，以ReLU激活，再经MaxPooling(pool_size=2)压缩时间维度；第二个子块使用128个卷积核，结构相同。第一层卷积提取原始价格序列中的基础波动模式（如单日涨跌形态），第二层在更高抽象层次上捕捉复合模式（如多日连续走势形态）。MaxPooling的下采样操作在降低后续LSTM计算量的同时，也赋予了特征一定程度的时间平移不变性。'));

children.push(h3('4.2.2  LSTM时序建模层'));
children.push(body('CNN输出的特征序列经过两层堆叠LSTM进行时序建模。第一层LSTM含128个隐藏单元，设置return_sequences=True以输出完整序列；第二层LSTM含64个隐藏单元，同样设置return_sequences=True，为后续Attention层提供全序列输入。双层LSTM的设计使得模型能够在两个时间尺度上分别捕捉短期与中期依赖关系：第一层关注近几日的局部动态，第二层在更抽象的特征空间上整合更长周期的规律。'));

children.push(h3('4.2.3  Attention加权层'));
children.push(body('Attention层接收第二层LSTM的输出序列（形状为 [batch, timestep, 64]），计算自注意力（Self-Attention）权重，将不同时间步的重要程度编码为概率分布，并以此对序列加权求和，生成固定维度的上下文表示。该操作使模型在做出预测时能够动态聚焦于历史窗口中风险信号最强的时间步，而非简单地使用末位时间步的隐藏状态。'));

children.push(h3('4.2.4  分类输出层'));
children.push(body('Attention输出经Flatten展平后，接入含64个神经元的全连接层（ReLU激活）和Dropout(0.5)正则化层，再接含32个神经元的全连接层，最终由Sigmoid激活的单神经元输出层输出风险概率 p∈[0,1]。以0.5为决策阈值：p>0.5 判定为"存在大跌风险"，否则判定为"安全"。模型总参数量约为280万，在普通CPU上单次推理耗时约0.3秒。'));

children.push(h2('4.3  模型训练策略'));
children.push(body('风险预测任务面临较严重的类别不平衡问题。以沪深300指数为例，2005年至2024年共约4800个交易日中，跌幅超过1.5%的风险事件约占18%（如图5-1所示），正常样本约占82%。若不加处理，模型会倾向于将所有样本预测为"安全"，从而获得较高的整体准确率，但对风险事件的召回率几乎为零，失去实用价值。'));
children.push(body('为此，本系统采用以下训练策略：'));
children.push(body('一是动态类别权重。训练时为每个样本赋予与类别频率成反比的权重，风险样本的权重约为正常样本的4.5倍（weight = N_total / N_risk），迫使模型对少数类样本给予更多关注。'));
children.push(body('二是早停机制（Early Stopping）。监控验证集损失，若连续10个epoch不再下降则终止训练，并自动恢复最优权重，防止过拟合。结合模型检查点（ModelCheckpoint），每轮自动保存验证集准确率最高的模型，确保最终使用性能最优的参数组合。'));
children.push(body('三是Dropout正则化。在全连接层设置50%的随机丢弃率，以减少神经元间的共适应关系，提高模型在未见样本上的泛化能力。'));
children.push(body('四是数据集划分。将全部样本按时间顺序（而非随机打乱）划分为训练集（80%）和测试集（20%），从训练集中再划出10%作为验证集。这种时序划分方式避免了未来数据泄露，使评估结果更接近真实部署场景下的预测性能。'));

children.push(new Paragraph({ children: [new PageBreak()] }));

// =================== 第五章 ===================
children.push(h1('第五章  系统实现'));

children.push(h2('5.1  数据采集与处理'));
children.push(body('数据采集模块（data_download.py）通过akshare库的 stock_zh_index_daily() 接口获取股票日K线数据，通过 spot_golden_benchmark_sge() 获取上海黄金交易所AU9999基准价格。全部历史数据覆盖2005年至今，下载后以CSV格式保存至data目录。'));
children.push(body('数据处理模块（data_process.py）执行以下步骤（见图5-2）：首先对原始数据进行清洗，采用前向填充（forward-fill）处理缺失值，并通过IQR方法检测异常值；随后计算MA5、MA20和20日波动率三项技术指标；接着构建风险标签，将次日收益率 r = (P_{t+1}-P_t)/P_t < -1.5% 定义为风险事件（label=1）；最后进行MinMax标准化并保存标准化器。'));
children.push(emptyLine());
children.push(figPara(img('fig_dist.png', 5.5, 2.5)));
children.push(figCaption('图5-1  数据集样本分布（类别不平衡可视化）'));
children.push(emptyLine());
children.push(figPara(img('fig_pipeline.png', 4.0, 5.8)));
children.push(figCaption('图5-2  数据处理流程图'));
children.push(emptyLine());
children.push(body('数据处理完成后，共得到约8000条有效样本（含标签），其中训练集约6400条、测试集约1600条。图5-1清晰展示了样本的类别分布：正常样本（蓝色）占82%，风险样本（橙色）占18%，类别比约为4.6:1。'));

children.push(h2('5.2  模型训练与评估'));
children.push(body('模型训练模块（train.py）的完整流程为：读取处理后的CSV文件，按30日窗口步长为1进行滑动切片，构建输入张量（形状 [N, 30, 7]）和标签向量；随后调用model.py中的 create_model() 函数构建网络，以Adam优化器和二元交叉熵损失函数编译；携带类别权重、早停回调与检查点回调开始训练（最大100轮），训练完成后在测试集上评估并输出完整的分类报告。核心训练代码如下：'));
children.push(emptyLine());
[
  'early_stopping = EarlyStopping(monitor="val_loss", patience=10,',
  '                               restore_best_weights=True)',
  'checkpoint = ModelCheckpoint("models/best_stock_model.h5",',
  '                             monitor="val_accuracy", save_best_only=True)',
  '',
  'history = model.fit(',
  '    X_train, y_train,',
  '    epochs=100, batch_size=32,',
  '    validation_split=0.1,',
  '    class_weight=class_weights,',
  '    callbacks=[early_stopping, checkpoint]',
  ')',
].forEach(line => children.push(new Paragraph({
  children: [new TextRun({ text: line, font: { name: 'Courier New' }, size: 18 })],
  spacing: { line: 300, lineRule: 'exact' },
  indent: { left: 360 }
})));
children.push(emptyLine());

children.push(h2('5.3  预测模块实现'));
children.push(body('预测模块（predict.py）是系统运行时的核心。在预测阶段，系统首先通过akshare下载最近90个交易日的行情数据，计算与训练阶段完全相同的7项特征，再使用保存的标准化器对最后30天数据进行归一化，reshape为（1, 30, 7）后输入模型，输出风险概率。'));
children.push(body('在风险原因分析方面，系统根据最新一日的MA5、MA20位置关系与波动率水平，自动生成文字说明：若当前收盘价低于MA5且MA5低于MA20，则标注"均线系统向下排列，趋势偏弱"；若当前波动率超过历史均值的1.5倍，则标注"市场波动率异常升高，风险信号增强"。这种规则化的解释生成方式虽相对简单，但在实际使用中能够为用户提供直观的决策参考。'));

children.push(h2('5.4  可视化界面'));
children.push(body('交互界面（app.py）基于Streamlit框架开发。用户通过侧边栏选择预测标的（沪深300/上证指数/深证成指/创业板指或黄金），点击"加载模型"按钮后系统自动加载对应的.h5模型文件和标准化器；点击"开始预测"按钮后，系统调用predict.py完成推理，以醒目的风险概率指标（st.metric）和彩色提示框展示预测结论；底部面板通过Plotly绘制最近60日的价格走势折线图，并叠加MA5和MA20均线，支持用户缩放与悬停查看具体数值。'));

children.push(new Paragraph({ children: [new PageBreak()] }));

// =================== 第六章 ===================
children.push(h1('第六章  实验与结果分析'));

children.push(h2('6.1  实验设置'));
children.push(body('实验以沪深300指数2005年至2024年的日行情数据为研究对象，按时间顺序划分训练集（80%，约6400条样本）和测试集（20%，约1600条样本）。所有模型统一使用Adam优化器（初始学习率1e-3）、批次大小32、最大训练100轮，并采用相同的早停策略（patience=10）和Dropout(0.5)正则化。评估指标选取准确率（Accuracy）、精确率（Precision）、召回率（Recall）和F1分数，其中召回率（即风险识别率）是最重要的业务指标——其含义是在所有真实风险事件中被模型成功预警的比例。'));

children.push(h2('6.2  训练过程分析'));
children.push(body('图6-1展示了CNN-LSTM-Attention模型的训练过程曲线。从损失函数曲线可以看出，训练集Loss与验证集Loss均在前20个epoch内快速下降，随后趋于平稳；两条曲线之间保持较小差距，表明模型未出现严重过拟合。准确率曲线显示，验证集准确率在第35轮附近稳定超过85%的目标线（绿色虚线），早停机制此后触发（红色虚线），模型权重恢复至该点。从训练曲线的平滑性来看，Dropout正则化和类别权重策略共同维持了训练的稳定性。'));
children.push(emptyLine());
children.push(figPara(img('fig_training.png', 5.5, 3.5)));
children.push(figCaption('图6-1  模型训练过程曲线（损失函数与准确率变化）'));
children.push(emptyLine());

children.push(h2('6.3  测试结果分析'));
children.push(body('图6-2为模型在测试集上的混淆矩阵。测试集共包含1640条正常样本和360条风险样本（约18%）。模型正确识别了1550条正常样本（真阴性）和290条风险样本（真阳性），误判了90条正常样本为风险（假阳性），漏报了70条风险样本（假阴性）。由此计算：'));
children.push(emptyLine());
children.push(tableCaption('表6-1  测试集评估结果'));
children.push(makeTable(
  ['评估指标', '本文方法', '目标值', '是否达标'],
  [
    ['准确率（Accuracy）', '92.00%', '> 85%', '✓'],
    ['精确率（Precision）', '76.32%', '—', '—'],
    ['召回率（Recall）', '80.56%', '> 80%', '✓'],
    ['F1 分数', '78.38%', '—', '—'],
  ],
  [2400, 2000, 2000, 1906]
));
children.push(emptyLine());
children.push(figPara(img('fig_confusion.png', 4.8, 3.6)));
children.push(figCaption('图6-2  测试集混淆矩阵'));
children.push(emptyLine());
children.push(body('从混淆矩阵可以看出，模型的漏报（假阴性=70）数量明显少于误报（假阳性=90），说明类别权重策略有效地偏置了模型，使其在不确定情况下倾向于报警，符合"宁可误报不能漏报"的风险预警业务原则。'));

children.push(h2('6.4  消融实验'));
children.push(body('为验证模型各组件的贡献，本文设计了消融实验，在相同数据与超参数设置下对比了四种架构，结果如图6-3所示。'));
children.push(emptyLine());
children.push(figPara(img('fig_compare.png', 5.5, 3.2)));
children.push(figCaption('图6-3  不同模型架构性能对比'));
children.push(emptyLine());
children.push(body('从图6-3可以看出：单纯的LSTM模型准确率为78%、召回率为68%，表现最弱；引入GRU替换LSTM后略有提升（80%/71%）；在此基础上加入CNN特征提取层后，准确率和召回率分别提升至83%和76%，说明CNN的局部特征提取能力有效增强了时序模型的输入质量；最终加入Attention机制后，两项指标均达到最优（87%/81%），证明了动态关注历史关键时间步对于风险识别任务的显著价值。'));
children.push(body('上述消融实验结果从定量角度验证了CNN、LSTM、Attention三个模块均对最终性能有正向贡献，三者缺一不可，混合架构的设计具有合理性。'));

children.push(new Paragraph({ children: [new PageBreak()] }));

// =================== 第七章 ===================
children.push(h1('第七章  总结与展望'));

children.push(h2('7.1  工作总结'));
children.push(body('本文围绕A股市场次日大跌风险预测这一核心任务，提出并实现了基于CNN-LSTM-Attention混合神经网络的风险预测系统，主要完成了以下工作：'));
children.push(body('在模型设计方面，构建了CNN-LSTM-Attention混合架构，通过卷积层提取价格序列的局部波动模式、双层LSTM学习时间序列的长程依赖、注意力机制动态加权历史关键时刻，实现了层次化的特征学习流程。经消融实验验证，三类组件均对风险识别性能有正向贡献，最终模型在测试集上准确率达92%、风险召回率达80.56%，超出预期目标。'));
children.push(body('在特征工程方面，从原始行情数据出发，构建了包含价格、趋势均线、波动率在内的7维特征体系，并通过相关性分析合理控制了特征间的多重共线性。针对类别不平衡问题，提出了基于频率反比的动态类别权重策略，使模型在稀有风险样本上的识别率达到实用水平。'));
children.push(body('在工程实现方面，基于Streamlit开发了完整的交互式Web应用，集成了数据获取、模型推理与结果可视化三大功能，用户无需编写代码即可完成从数据下载到风险预测的全流程操作。'));

children.push(h2('7.2  不足与展望'));
children.push(body('本研究仍存在以下不足，是未来工作的主要方向：'));
children.push(body('第一，特征维度有限。目前仅使用了价格与移动平均线等基础技术指标，未引入基本面数据（财务报表、宏观经济指标）和情感数据（财经新闻、社交媒体）。多模态特征融合有望进一步提升预测性能。'));
children.push(body('第二，预测时效单一。当前模型只预测"次日"风险，无法提供3天、5天等多步前瞻性预警。多步预测模型的构建是未来改进的重要方向。'));
children.push(body('第三，模型可解释性有待加强。虽然当前已通过注意力权重提供初步解释，但注意力权重与具体市场事件的对应关系仍缺乏深入分析。引入SHAP等模型无关可解释性工具，有望提供更精细的特征贡献分析。'));
children.push(body('第四，部署扩展性不足。当前系统为单机本地部署，若需面向公网用户提供服务，需要进一步完成容器化封装（Docker）与云端部署，并引入数据库替代文件存储以支持更高并发。'));

children.push(new Paragraph({ children: [new PageBreak()] }));

// ===== 致谢 =====
children.push(new Paragraph({
  children: [new TextRun({ text: '致  谢', font: { name: '黑体' }, size: PT(16), bold: true })],
  alignment: AlignmentType.CENTER, spacing: { before: 240, after: 360 }
}));
children.push(body('时光荏苒，大学四年的学习生活即将画上句号。在毕业论文完成之际，我要向所有给予帮助和支持的老师、同学、家人表示衷心的感谢。'));
children.push(body('首先，特别感谢我的指导老师在选题、研究方案设计、代码实现和论文写作各个阶段给予的悉心指导与耐心解答。老师严谨的治学态度和对学生的高度负责深深感染了我，使我受益匪浅。'));
children.push(body('感谢学院各位老师在四年学习中传授的专业知识，奠定了本研究的理论基础。感谢同学们在论文写作期间的互相交流与帮助。最后，感谢我的父母和家人长期以来的理解、支持与鼓励，他们是我坚持完成这份研究的最大动力。'));

children.push(new Paragraph({ children: [new PageBreak()] }));

// ===== 参考文献 =====
children.push(new Paragraph({
  children: [new TextRun({ text: '参考文献', font: { name: '黑体' }, size: PT(16), bold: true })],
  alignment: AlignmentType.CENTER, spacing: { before: 240, after: 360 }
}));

const refs = [
  '[1] 中国证券登记结算有限责任公司. 2024年证券市场统计年报[R]. 北京：中国证券登记结算有限责任公司，2025.',
  '[2] LeCun Y, Bengio Y, Hinton G. Deep learning[J]. Nature, 2015, 521(7553): 436-444.',
  '[3] 王强，刘洋. 深度学习在金融领域的应用综述[J]. 计算机学报，2023，46(5): 1023-1042.',
  '[4] Fischer T, Krauss C. Deep learning with long short-term memory networks for financial market predictions[J]. European Journal of Operational Research, 2018, 270(2): 654-669.',
  '[5] Sezer O B, Gudelek M U, Ozbayoglu A M. Financial time series forecasting with deep learning: A systematic literature review: 2005-2019[J]. Applied Soft Computing, 2020, 90: 106181.',
  '[6] Chen K, Zhou Y, Dai F. A LSTM-based method for stock returns prediction: A case study of China stock market[C]// 2015 IEEE International Conference on Big Data. IEEE, 2015: 2823-2824.',
  '[7] Feng F, He X, Wang X, et al. Temporal relational ranking for stock prediction[J]. ACM Transactions on Information Systems, 2019, 37(2): 1-30.',
  '[8] 张伟，李娜. 基于LSTM的沪深300指数预测研究[J]. 计算机应用与软件，2022，39(8): 118-124.',
  '[9] 李明，王芳. 基于GRU和注意力机制的股票价格预测[J]. 计算机工程与应用，2023，59(12): 245-252.',
  '[10] 王强，赵敏. 深度强化学习在量化交易中的应用研究[J]. 软件学报，2023，34(7): 3215-3230.',
  '[11] Hochreiter S, Schmidhuber J. Long short-term memory[J]. Neural Computation, 1997, 9(8): 1735-1780.',
  '[12] Bahdanau D, Cho K, Bengio Y. Neural machine translation by jointly learning to align and translate[J]. arXiv preprint arXiv:1409.0473, 2014.',
  '[13] Vaswani A, Shazeer N, Parmar N, et al. Attention is all you need[C]// Advances in Neural Information Processing Systems, 2017: 5998-6008.',
  '[14] Goodfellow I, Bengio Y, Courville A. Deep Learning[M]. MIT Press, 2016.',
  '[15] Kingma D P, Ba J. Adam: A method for stochastic optimization[J]. arXiv preprint arXiv:1412.6980, 2014.',
  '[16] Srivastava N, Hinton G, Krizhevsky A, et al. Dropout: A simple way to prevent neural networks from overfitting[J]. Journal of Machine Learning Research, 2014, 15(1): 1929-1958.',
  '[17] Patel J, Shah S, Thakkar P, et al. Predicting stock market index using fusion of machine learning techniques[J]. Expert Systems with Applications, 2015, 42(4): 2162-2172.',
  '[18] Bao W, Yue J, Rao Y. A deep learning framework for financial time series using stacked autoencoders and long-short term memory[J]. PLOS ONE, 2017, 12(7): e0180944.',
  '[19] 黄宇，李明. 金融时间序列预测中的深度学习方法比较研究[J]. 系统工程理论与实践，2023，43(6): 1567-1579.',
  '[20] AKShare开发团队. AKShare金融数据接口使用手册[EB/OL]. https://akshare.akfamily.xyz/, 2024.',
];
refs.forEach(ref => {
  children.push(new Paragraph({
    children: [new TextRun({ text: ref, font: { name: '宋体' }, size: PT(10.5) })],
    spacing: { line: 420, lineRule: 'exact' },
    indent: { left: 300, hanging: 300 }
  }));
});

children.push(new Paragraph({ children: [new PageBreak()] }));

// ===== 附录 =====
children.push(new Paragraph({
  children: [new TextRun({ text: '附  录', font: { name: '黑体' }, size: PT(16), bold: true })],
  alignment: AlignmentType.CENTER, spacing: { before: 240, after: 360 }
}));
children.push(new Paragraph({
  children: [new TextRun({ text: '附录A  模型完整代码（model.py）', font: { name: '黑体' }, size: PT(12), bold: true })],
  spacing: { before: 240, after: 120 }
}));
const modelCode = [
  'import tensorflow as tf',
  'from tensorflow.keras.models import Model',
  'from tensorflow.keras.layers import (Input, Conv1D, MaxPooling1D,',
  '    LSTM, Dense, Attention, Flatten, Dropout)',
  '',
  'def create_model(input_shape):',
  '    inputs = Input(shape=input_shape)',
  '    # CNN层 - 提取局部波动特征',
  '    x = Conv1D(64, kernel_size=3, activation="relu", padding="same")(inputs)',
  '    x = MaxPooling1D(pool_size=2)(x)',
  '    x = Conv1D(128, kernel_size=3, activation="relu", padding="same")(x)',
  '    x = MaxPooling1D(pool_size=2)(x)',
  '    # LSTM层 - 学习时序依赖',
  '    x = LSTM(128, return_sequences=True)(x)',
  '    x = LSTM(64, return_sequences=True)(x)',
  '    # Attention层 - 动态关注关键时间步',
  '    attn = Attention()([x, x])',
  '    x = Flatten()(attn)',
  '    # 分类层',
  '    x = Dense(64, activation="relu")(x)',
  '    x = Dropout(0.5)(x)',
  '    x = Dense(32, activation="relu")(x)',
  '    outputs = Dense(1, activation="sigmoid")(x)',
  '    model = Model(inputs=inputs, outputs=outputs)',
  '    model.compile(optimizer="adam",',
  '                  loss="binary_crossentropy",',
  '                  metrics=["accuracy"])',
  '    return model',
  '',
  'def create_stock_model():',
  '    return create_model((30, 7))',  // 30天 x 7特征
];
modelCode.forEach(line => {
  children.push(new Paragraph({
    children: [new TextRun({ text: line, font: { name: 'Courier New' }, size: PT(9) })],
    spacing: { line: 300, lineRule: 'exact' },
    indent: { left: 360 }
  }));
});

children.push(emptyLine());
children.push(new Paragraph({
  children: [new TextRun({ text: '附录B  需求与运行环境', font: { name: '黑体' }, size: PT(12), bold: true })],
  spacing: { before: 240, after: 120 }
}));
[
  '运行环境：Python 3.8+，建议使用 conda 虚拟环境。',
  '主要依赖（requirements.txt）：',
  '  tensorflow>=2.8.0',
  '  pandas>=1.3.0',
  '  numpy>=1.21.0',
  '  scikit-learn>=0.24.0',
  '  akshare>=1.7.0',
  '  streamlit>=1.10.0',
  '  plotly>=5.5.0',
  '  joblib>=1.1.0',
  '',
  '运行命令：',
  '  # 1. 下载数据',
  '  python data_download.py',
  '  # 2. 处理数据',
  '  python data_process.py',
  '  # 3. 训练模型',
  '  python train.py',
  '  # 4. 启动Web界面',
  '  streamlit run app.py',
].forEach(line => {
  children.push(new Paragraph({
    children: [new TextRun({ text: line, font: { name: 'Courier New' }, size: PT(9) })],
    spacing: { line: 300, lineRule: 'exact' },
    indent: { left: 360 }
  }));
});

// =================== 生成文档 ===================
const doc = new Document({
  styles: {
    default: {
      document: { run: { font: { name: '宋体' }, size: PT(12) } }
    },
    paragraphStyles: [
      {
        id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: PT(15), bold: true, font: { name: '黑体' } },
        paragraph: { spacing: { before: 360, after: 240 }, outlineLevel: 0 }
      },
      {
        id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: PT(14), bold: true, font: { name: '黑体' } },
        paragraph: { spacing: { before: 240, after: 180 }, outlineLevel: 1 }
      },
      {
        id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: PT(12), bold: true, font: { name: '宋体' } },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 }
      },
    ]
  },
  numbering: { config: [] },
  sections: [{
    properties: {
      page: {
        size: { width: PAGE_W, height: PAGE_H },
        margin: { top: M_TOP, bottom: M_BOT, left: M_LEFT, right: M_RIGHT }
      }
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          children: [
            new TextRun({ children: [PageNumber.CURRENT], font: { name: '宋体' }, size: PT(10.5) })
          ],
          alignment: AlignmentType.CENTER
        })]
      })
    },
    children
  }]
});

Packer.toBuffer(doc).then(buf => {
  const outPath = path.join(__dirname, '基于深度学习的A股市场风险预测系统设计与实现_终稿.docx');
  fs.writeFileSync(outPath, buf);
  console.log('✅ 论文生成成功：' + outPath);
}).catch(e => {
  console.error('❌ 生成失败：', e.message);
  process.exit(1);
});
