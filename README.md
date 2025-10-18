# LangGraph Supply Chain Agent / LangGraph 供应链智能体

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0.0-green.svg)](https://github.com/langchain-ai/langgraph)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 项目简介 / Project Overview

这是一个基于 LangGraph 构建的智能供应链风险分析系统，能够自动分析供应链中断事件，评估影响，生成应对方案，并输出专业的响应报告。该系统采用多节点工作流设计，支持多种大语言模型，为供应链管理提供智能决策支持。

This is an intelligent supply chain risk analysis system built with LangGraph that can automatically analyze supply chain disruption events, assess impacts, generate response solutions, and output professional response reports. The system uses a multi-node workflow design and supports multiple large language models to provide intelligent decision support for supply chain management.

## 核心功能 / Core Features

### 🔍 智能事件分析 / Intelligent Event Analysis
- 自动分析供应链中断事件背景和严重性
- 集成实时搜索获取最新相关信息
- 提供专业的事件评估报告

### 📊 影响评估 / Impact Assessment
- 深度分析对全球电子消费品公司的具体影响
- 识别关键供应商、运输路线和潜在瓶颈
- 评估零部件和最终产品的短缺风险

### 💡 方案生成 / Solution Generation
- 智能生成多个可行的应对方案
- 自动进行成本效益和风险评估
- 支持方案修正和优化迭代

### 📋 专业报告 / Professional Reports
- 生成结构化的供应链响应报告
- 包含执行摘要、影响评估、方案分析和推荐行动计划
- 自动质量评估和评分

## 系统架构 / System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Event Input   │───▶│  Analyze Event  │───▶│  Assess Impact  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Generate Report │◀───│ Review & Decide │◀───│Brainstorm Solutions│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 工作流节点 / Workflow Nodes

1. **事件分析节点 (Analyze Event)**: 分析中断事件的背景和严重性
2. **影响评估节点 (Assess Impact)**: 评估对供应链的具体影响
3. **方案生成节点 (Brainstorm Solutions)**: 生成多个应对方案
4. **审查决策节点 (Review & Decide)**: 审查方案并做出决策
5. **报告合成节点 (Synthesize Report)**: 生成最终的专业报告

## 安装指南 / Installation Guide

### 环境要求 / Requirements
- Python 3.8+
- pip 包管理器

### 安装步骤 / Installation Steps

1. **克隆项目 / Clone the repository**
```bash
git clone <repository-url>
cd Langgraph_supplychian_agent
```

2. **安装依赖 / Install dependencies**
```bash
pip install -r requirements.txt
```

3. **安装可视化依赖 (可选) / Install visualization dependencies (optional)**
```bash
# Ubuntu/Debian
sudo apt-get install graphviz graphviz-dev
pip install pygraphviz

# macOS
brew install graphviz
pip install pygraphviz

# Windows
# 下载并安装 Graphviz: https://graphviz.org/download/
pip install pygraphviz
```

4. **配置环境变量 / Configure environment variables**
创建 `.env` 文件并配置相应的 API 密钥：
```bash
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Google Gemini
GOOGLE_API_KEY=your_google_api_key

# 本地模型 (可选)
LOCAL_LLM_API_URL=http://your-local-api-url
LOCAL_LLM_MODEL_NAME=your-model-name

# Tavily 搜索 (可选)
TAVILY_API_KEY=your_tavily_api_key
```

## 使用方法 / Usage

### 基本使用 / Basic Usage

```bash
# 使用 OpenAI GPT-4
python main.py --llm openai

# 使用 Google Gemini
python main.py --llm gemini

# 使用本地模型
python main.py --llm local

# 使用 DeepSeek (通过 Ollama)
python main.py --llm deepseek
```

### 支持的模型 / Supported Models

| 提供商 / Provider | 模型 / Model | 说明 / Description |
|------------------|-------------|-------------------|
| OpenAI | gpt-4-turbo-preview, gpt-3.5-turbo | 高质量分析，支持结构化输出 |
| Google | gemini-2.5-flash | 快速响应，成本效益高 |
| DeepSeek | deepseek-coder | 通过 Ollama 本地部署 |
| Local API | 自定义模型 | 支持自定义 API 端点 |

## 项目结构 / Project Structure

```
Langgraph_supplychian_agent/
├── main.py                 # 主程序入口
├── requirements.txt        # 项目依赖
├── .env                   # 环境变量配置
├── README.md              # 项目说明文档
├── supply_chain_workflow.png  # 工作流可视化图
└── src/                   # 源代码目录
    ├── __init__.py
    ├── graph_builder.py   # 图构建器
    ├── graph_nodes.py     # 节点定义
    └── llm_provider.py    # LLM 提供商
```

## 示例输出 / Example Output

系统会生成类似以下的专业供应链响应报告：

```
## 供应链中断事件响应报告：苏伊士运河集装箱船搁浅事件

**致：** 董事会及高级管理层
**发件人：** [您的姓名/商业顾问团队]
**日期：** 2023年10月27日
**主题：** 苏伊士运河集装箱船搁浅事件对全球供应链的影响评估及应对策略

### 1. 事件摘要 (Executive Summary)
[详细的事件背景和影响概述]

### 2. 详细影响评估 (Detailed Impact Assessment)
[对全球供应链和具体公司的深入影响分析]

### 3. 备选方案分析 (Alternative Solutions Analysis)
[多个可行的应对方案及其成本效益分析]

### 4. 最终推荐行动计划 (Recommended Action Plan)
[具体的实施步骤和时间框架]
```

## 技术特性 / Technical Features

### 🔄 智能工作流 / Intelligent Workflow
- 基于 LangGraph 的状态图工作流
- 支持条件分支和循环修正
- 自动化的节点间数据传递

### 🧠 多模型支持 / Multi-Model Support
- 支持多种主流 LLM 提供商
- 自动适配不同模型的结构化输出
- 智能选择最适合的模型进行不同任务

### 🔍 实时信息集成 / Real-time Information Integration
- 集成 Tavily 搜索获取最新信息
- 支持外部数据源接入
- 动态更新分析结果

### 📊 结构化输出 / Structured Output
- 使用 Pydantic 模型确保数据质量
- 自动化的 JSON 解析和验证
- 支持复杂的数据结构

## 配置说明 / Configuration

### 环境变量 / Environment Variables

| 变量名 / Variable | 说明 / Description | 必需 / Required |
|------------------|-------------------|----------------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | 使用 OpenAI 时必需 |
| `GOOGLE_API_KEY` | Google API 密钥 | 使用 Gemini 时必需 |
| `LOCAL_LLM_API_URL` | 本地模型 API 地址 | 使用本地模型时必需 |
| `LOCAL_LLM_MODEL_NAME` | 本地模型名称 | 使用本地模型时必需 |
| `TAVILY_API_KEY` | Tavily 搜索 API 密钥 | 可选，用于实时搜索 |

### 自定义配置 / Custom Configuration

您可以在 `src/llm_provider.py` 中修改模型参数：

```python
# 修改温度参数
temperature: float = 0.7

# 修改最大令牌数
max_tokens: int = 2048

# 修改 API 端点
api_url: str = "your-custom-api-endpoint"
```

## 故障排除 / Troubleshooting

### 常见问题 / Common Issues

1. **可视化图生成失败 / Graph visualization fails**
```bash
# 确保安装了 graphviz 系统库
sudo apt-get install graphviz graphviz-dev
pip install pygraphviz
```

2. **API 密钥错误 / API key errors**
```bash
# 检查 .env 文件中的 API 密钥是否正确
cat .env
```

3. **本地模型连接失败 / Local model connection fails**
```bash
# 检查本地 API 服务是否运行
curl -X POST http://your-api-url/v1/chat/completions
```

4. **依赖安装问题 / Dependency installation issues**
```bash
# 升级 pip 并重新安装
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## 贡献指南 / Contributing

我们欢迎社区贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证 / License

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。



**注意 / Note**: 本项目仅用于学习和研究目的。在生产环境中使用前，请确保充分测试和验证所有功能。
