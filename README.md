# 🎯 SkillMatch

> 轻量级AI Agent技能智能发现、匹配与编排引擎CLI工具

[English](#english) | [繁體中文](#繁體中文)

## 🎉 项目介绍

SkillMatch 是一款零依赖、纯Python实现的AI Agent技能智能发现与匹配引擎。它帮助开发者快速找到最适合其AI编码助手（Claude Code、Cursor、Copilot等）的技能插件，通过TF-IDF+BM25混合语义匹配算法，实现精准的技能推荐。

**解决的核心痛点：**
- AI Agent技能生态分散，缺乏统一的发现和搜索入口
- 技能安全性难以评估，安装前缺乏风险预判
- 不同Agent框架的技能格式不统一，管理困难

**自研差异化亮点：**
- 🚫 **零外部依赖** - 纯Python标准库实现，无需安装任何第三方包
- 🧠 **智能语义匹配** - TF-IDF + BM25混合算法，支持自然语言查询
- 🛡️ **7维安全验证** - 文件写入、命令执行、网络请求等全方位风险检测
- 🎨 **ANSI彩色TUI** - 零依赖的终端交互界面
- 🔌 **多框架支持** - Claude Code、Cursor、Copilot、自定义框架

## ✨ 核心特性

- **🔍 智能搜索** - 基于TF-IDF+BM25混合算法的语义匹配，支持自然语言查询
- **📦 22个内置技能** - 涵盖代码审查、测试生成、文档编写、重构、安全扫描等场景
- **🛡️ 安全验证** - 7类风险模式检测，自动评估技能安全等级
- **⚡ 零依赖** - 纯Python标准库，Python 3.8+即装即用
- **🎨 TUI界面** - ANSI彩色终端交互界面，直观易用
- **📋 完整CLI** - 8个子命令覆盖搜索、安装、管理、验证全流程
- **🔄 多框架适配** - 支持Claude Code、Cursor、Copilot及自定义Agent框架
- **💾 持久化存储** - 本地注册表管理，技能数据安全可靠

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- 无需任何第三方依赖

### 安装

```bash
# 从PyPI安装（推荐）
pip install skillmatch

# 或从源码安装
git clone https://github.com/gitstq/SkillMatch.git
cd SkillMatch
pip install .
```

### 快速使用

```bash
# 初始化配置
skillmatch init

# 搜索技能
skillmatch search "code review" --top 5

# 按框架过滤搜索
skillmatch search "testing" --framework claude --top 10

# 安装技能
skillmatch install code-review

# 查看已安装技能
skillmatch list

# 查看技能详情
skillmatch info code-review

# 验证技能安全性
skillmatch validate ./my-skill/

# 导出技能注册表
skillmatch export --format json
```

## 📖 详细使用指南

### 搜索技能

```bash
# 基础搜索 - 使用自然语言描述需求
skillmatch search "help me write better tests"

# 限制结果数量
skillmatch search "database optimization" --top 3

# 按框架过滤
skillmatch search "api design" --framework cursor

# 按标签过滤
skillmatch search "security" --tag security

# 组合过滤
skillmatch search "code quality" --framework claude --tag review --top 5
```

### 管理技能

```bash
# 列出所有可用技能（含未安装）
skillmatch list --all

# 列出已安装技能
skillmatch list

# 安装技能
skillmatch install code-review

# 从GitHub安装
skillmatch install https://github.com/user/skill-repo

# 查看技能详情
skillmatch info code-review

# 卸载技能
skillmatch remove code-review
```

### 安全验证

```bash
# 验证本地技能目录
skillmatch validate ./my-custom-skill/

# 验证会输出风险等级和建议
# 风险等级: safe / low / medium / high
```

### 导出与分享

```bash
# 导出为JSON
skillmatch export --format json > my-skills.json

# 导出为YAML
skillmatch export --format yaml > my-skills.yaml
```

## 💡 设计思路与迭代规划

### 设计理念

SkillMatch 的核心设计理念是**让AI Agent技能的发现和管理像包管理器一样简单**。我们参考了npm、pip等成熟包管理器的设计模式，结合AI Agent技能的特殊性（安全性要求高、框架适配多样），打造了一个专为AI编码Agent设计的技能管理工具。

### 技术选型

| 技术 | 选型 | 原因 |
|------|------|------|
| 语言 | Python 3.8+ | AI生态主流语言，开发者熟悉度高 |
| 匹配算法 | TF-IDF + BM25 | 经典信息检索算法，零依赖实现 |
| 存储格式 | JSON | 轻量级、可读性强、标准库原生支持 |
| 终端UI | ANSI转义码 | 零依赖实现彩色终端界面 |

### 后续迭代计划

- [ ] 🌐 在线技能市场（社区贡献技能共享）
- [ ] 🔗 MCP协议支持（与Model Context Protocol集成）
- [ ] 📊 技能使用统计分析
- [ ] 🔄 自动更新机制
- [ ] 🧪 技能沙箱运行环境
- [ ] 📦 技能打包与分发格式标准化

## 📦 打包与部署指南

### 作为CLI工具使用

```bash
# 安装后直接使用
pip install skillmatch
skillmatch --version
```

### 作为Python库使用

```python
from skillmatch import SkillMatcher, SkillRegistry

# 创建匹配器
matcher = SkillMatcher()

# 搜索技能
results = matcher.search("code review", top_k=5)
for result in results:
    print(f"{result.skill.name}: {result.score:.4f}")

# 管理注册表
registry = SkillRegistry()
registry.list_skills()
```

### 开发模式

```bash
git clone https://github.com/gitstq/SkillMatch.git
cd SkillMatch
pip install -e .

# 运行测试
python -m unittest discover tests/ -v
```

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

**提交规范：** 遵循 Angular 提交规范
- `feat:` 新增功能
- `fix:` 修复问题
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具变更

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源。

---

# 繁體中文

# 🎯 SkillMatch

> 輕量級 AI Agent 技能智慧發現、匹配與編排引擎 CLI 工具

[简体中文](#-skillmatch) | [English](#english)

## 🎉 專案介紹

SkillMatch 是一款零依賴、純 Python 實作的 AI Agent 技能智慧發現與匹配引擎。它幫助開發者快速找到最適合其 AI 編碼助手（Claude Code、Cursor、Copilot 等）的技能外掛，透過 TF-IDF+BM25 混合語義匹配演算法，實現精準的技能推薦。

**解決的核心痛點：**
- AI Agent 技能生態分散，缺乏統一的發現和搜尋入口
- 技能安全性難以評估，安裝前缺乏風險預判
- 不同 Agent 框架的技能格式不統一，管理困難

**自研差異化亮點：**
- 🚫 **零外部依賴** - 純 Python 標準庫實作，無需安裝任何第三方套件
- 🧠 **智慧語義匹配** - TF-IDF + BM25 混合演算法，支援自然語言查詢
- 🛡️ **7 維安全驗證** - 檔案寫入、命令執行、網路請求等全方位風險檢測
- 🎨 **ANSI 彩色 TUI** - 零依賴的終端互動介面
- 🔌 **多框架支援** - Claude Code、Cursor、Copilot、自訂框架

## ✨ 核心特性

- **🔍 智慧搜尋** - 基於 TF-IDF+BM25 混合演算法的語義匹配，支援自然語言查詢
- **📦 22 個內建技能** - 涵蓋程式碼審查、測試生成、文件撰寫、重構、安全掃描等場景
- **🛡️ 安全驗證** - 7 類風險模式檢測，自動評估技能安全等級
- **⚡ 零依賴** - 純 Python 標準庫，Python 3.8+ 即裝即用
- **🎨 TUI 介面** - ANSI 彩色終端互動介面，直觀易用
- **📋 完整 CLI** - 8 個子命令涵蓋搜尋、安裝、管理、驗證全流程
- **🔄 多框架適配** - 支援 Claude Code、Cursor、Copilot 及自訂 Agent 框架
- **💾 持久化儲存** - 本地註冊表管理，技能資料安全可靠

## 🚀 快速開始

### 環境需求

- Python 3.8 或更高版本
- 無需任何第三方依賴

### 安裝

```bash
# 從 PyPI 安裝（推薦）
pip install skillmatch

# 或從原始碼安裝
git clone https://github.com/gitstq/SkillMatch.git
cd SkillMatch
pip install .
```

### 快速使用

```bash
# 初始化設定
skillmatch init

# 搜尋技能
skillmatch search "code review" --top 5

# 按框架過濾搜尋
skillmatch search "testing" --framework claude --top 10

# 安裝技能
skillmatch install code-review

# 查看已安裝技能
skillmatch list

# 查看技能詳情
skillmatch info code-review

# 驗證技能安全性
skillmatch validate ./my-skill/

# 匯出技能註冊表
skillmatch export --format json
```

## 📖 詳細使用指南

### 搜尋技能

```bash
# 基礎搜尋 - 使用自然語言描述需求
skillmatch search "help me write better tests"

# 限制結果數量
skillmatch search "database optimization" --top 3

# 按框架過濾
skillmatch search "api design" --framework cursor

# 按標籤過濾
skillmatch search "security" --tag security

# 組合過濾
skillmatch search "code quality" --framework claude --tag review --top 5
```

### 管理技能

```bash
# 列出所有可用技能（含未安裝）
skillmatch list --all

# 列出已安裝技能
skillmatch list

# 安裝技能
skillmatch install code-review

# 從 GitHub 安裝
skillmatch install https://github.com/user/skill-repo

# 查看技能詳情
skillmatch info code-review

# 解除安裝技能
skillmatch remove code-review
```

### 安全驗證

```bash
# 驗證本地技能目錄
skillmatch validate ./my-custom-skill/

# 驗證會輸出風險等級和建議
# 風險等級: safe / low / medium / high
```

### 匯出與分享

```bash
# 匯出為 JSON
skillmatch export --format json > my-skills.json

# 匯出為 YAML
skillmatch export --format yaml > my-skills.yaml
```

## 💡 設計思路與迭代規劃

### 設計理念

SkillMatch 的核心設計理念是**讓 AI Agent 技能的發現和管理像套件管理器一樣簡單**。我們參考了 npm、pip 等成熟套件管理器的設計模式，結合 AI Agent 技能的特殊性（安全性要求高、框架適配多樣），打造了一個專為 AI 編碼 Agent 設計的技能管理工具。

### 技術選型

| 技術 | 選型 | 原因 |
|------|------|------|
| 語言 | Python 3.8+ | AI 生態主流語言，開發者熟悉度高 |
| 匹配演算法 | TF-IDF + BM25 | 經典資訊檢索演算法，零依賴實作 |
| 儲存格式 | JSON | 輕量級、可讀性強、標準庫原生支援 |
| 終端 UI | ANSI 跳脫碼 | 零依賴實作彩色終端介面 |

### 後續迭代計畫

- [ ] 🌐 線上技能市場（社群貢獻技能共享）
- [ ] 🔗 MCP 協議支援（與 Model Context Protocol 整合）
- [ ] 📊 技能使用統計分析
- [ ] 🔄 自動更新機制
- [ ] 🧪 技能沙箱執行環境
- [ ] 📦 技能打包與分發格式標準化

## 📦 打包與部署指南

### 作為 CLI 工具使用

```bash
# 安裝後直接使用
pip install skillmatch
skillmatch --version
```

### 作為 Python 函式庫使用

```python
from skillmatch import SkillMatcher, SkillRegistry

# 建立匹配器
matcher = SkillMatcher()

# 搜尋技能
results = matcher.search("code review", top_k=5)
for result in results:
    print(f"{result.skill.name}: {result.score:.4f}")

# 管理註冊表
registry = SkillRegistry()
registry.list_skills()
```

### 開發模式

```bash
git clone https://github.com/gitstq/SkillMatch.git
cd SkillMatch
pip install -e .

# 執行測試
python -m unittest discover tests/ -v
```

## 🤝 貢獻指南

歡迎貢獻！請遵循以下步驟：

1. Fork 本儲存庫
2. 建立特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 建立 Pull Request

**提交規範：** 遵循 Angular 提交規範
- `feat:` 新增功能
- `fix:` 修復問題
- `docs:` 文件更新
- `refactor:` 程式碼重構
- `test:` 測試相關
- `chore:` 建構/工具變更

## 📄 開源協議

本專案基於 [MIT License](LICENSE) 開源。

---

# English

# 🎯 SkillMatch

> A lightweight CLI tool for intelligent AI Agent skill discovery, matching, and orchestration

[简体中文](#-skillmatch) | [繁體中文](#繁體中文)

## 🎉 Introduction

SkillMatch is a zero-dependency, pure-Python intelligent AI Agent skill discovery and matching engine. It helps developers quickly find the most suitable skill plugins for their AI coding assistants (Claude Code, Cursor, Copilot, etc.) through a TF-IDF+BM25 hybrid semantic matching algorithm, delivering precise skill recommendations.

**Core pain points addressed:**
- The AI Agent skill ecosystem is fragmented, lacking a unified discovery and search entry point
- Skill security is difficult to assess, with no risk pre-evaluation before installation
- Skill formats vary across different Agent frameworks, making management challenging

**Key differentiators:**
- 🚫 **Zero external dependencies** - Built entirely with the Python standard library, no third-party packages required
- 🧠 **Intelligent semantic matching** - TF-IDF + BM25 hybrid algorithm with natural language query support
- 🛡️ **7-dimensional security validation** - Comprehensive risk detection covering file writes, command execution, network requests, and more
- 🎨 **ANSI-colored TUI** - Zero-dependency terminal interactive interface
- 🔌 **Multi-framework support** - Claude Code, Cursor, Copilot, and custom frameworks

## ✨ Core Features

- **🔍 Intelligent search** - Semantic matching based on TF-IDF+BM25 hybrid algorithm with natural language query support
- **📦 22 built-in skills** - Covering code review, test generation, documentation, refactoring, security scanning, and more
- **🛡️ Security validation** - 7 risk pattern categories with automatic skill safety level assessment
- **⚡ Zero dependencies** - Pure Python standard library, ready to use with Python 3.8+
- **🎨 TUI interface** - ANSI-colored terminal interactive interface, intuitive and easy to use
- **📋 Complete CLI** - 8 subcommands covering search, install, manage, and validate workflows
- **🔄 Multi-framework adaptation** - Supports Claude Code, Cursor, Copilot, and custom Agent frameworks
- **💾 Persistent storage** - Local registry management for secure and reliable skill data

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- No third-party dependencies required

### Installation

```bash
# Install from PyPI (recommended)
pip install skillmatch

# Or install from source
git clone https://github.com/gitstq/SkillMatch.git
cd SkillMatch
pip install .
```

### Quick Usage

```bash
# Initialize configuration
skillmatch init

# Search for skills
skillmatch search "code review" --top 5

# Filter search by framework
skillmatch search "testing" --framework claude --top 10

# Install a skill
skillmatch install code-review

# List installed skills
skillmatch list

# View skill details
skillmatch info code-review

# Validate skill security
skillmatch validate ./my-skill/

# Export skill registry
skillmatch export --format json
```

## 📖 Detailed Usage Guide

### Searching Skills

```bash
# Basic search - describe your needs in natural language
skillmatch search "help me write better tests"

# Limit the number of results
skillmatch search "database optimization" --top 3

# Filter by framework
skillmatch search "api design" --framework cursor

# Filter by tag
skillmatch search "security" --tag security

# Combined filters
skillmatch search "code quality" --framework claude --tag review --top 5
```

### Managing Skills

```bash
# List all available skills (including uninstalled)
skillmatch list --all

# List installed skills
skillmatch list

# Install a skill
skillmatch install code-review

# Install from GitHub
skillmatch install https://github.com/user/skill-repo

# View skill details
skillmatch info code-review

# Uninstall a skill
skillmatch remove code-review
```

### Security Validation

```bash
# Validate a local skill directory
skillmatch validate ./my-custom-skill/

# Validation outputs risk level and recommendations
# Risk levels: safe / low / medium / high
```

### Exporting and Sharing

```bash
# Export as JSON
skillmatch export --format json > my-skills.json

# Export as YAML
skillmatch export --format yaml > my-skills.yaml
```

## 💡 Design Philosophy and Roadmap

### Design Philosophy

SkillMatch's core design philosophy is to **make AI Agent skill discovery and management as simple as a package manager**. We drew inspiration from the design patterns of mature package managers like npm and pip, combined with the unique requirements of AI Agent skills (high security demands, diverse framework adaptation), to build a skill management tool specifically designed for AI coding Agents.

### Technology Choices

| Technology | Choice | Rationale |
|------|------|------|
| Language | Python 3.8+ | Mainstream language in the AI ecosystem, high developer familiarity |
| Matching Algorithm | TF-IDF + BM25 | Classic information retrieval algorithms, zero-dependency implementation |
| Storage Format | JSON | Lightweight, highly readable, natively supported by the standard library |
| Terminal UI | ANSI Escape Codes | Zero-dependency colored terminal interface |

### Future Roadmap

- [ ] 🌐 Online skill marketplace (community-contributed skill sharing)
- [ ] 🔗 MCP protocol support (Model Context Protocol integration)
- [ ] 📊 Skill usage statistics and analytics
- [ ] 🔄 Automatic update mechanism
- [ ] 🧪 Skill sandbox execution environment
- [ ] 📦 Skill packaging and distribution format standardization

## 📦 Packaging and Deployment Guide

### Using as a CLI Tool

```bash
# Use directly after installation
pip install skillmatch
skillmatch --version
```

### Using as a Python Library

```python
from skillmatch import SkillMatcher, SkillRegistry

# Create a matcher
matcher = SkillMatcher()

# Search for skills
results = matcher.search("code review", top_k=5)
for result in results:
    print(f"{result.skill.name}: {result.score:.4f}")

# Manage the registry
registry = SkillRegistry()
registry.list_skills()
```

### Development Mode

```bash
git clone https://github.com/gitstq/SkillMatch.git
cd SkillMatch
pip install -e .

# Run tests
python -m unittest discover tests/ -v
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

**Commit conventions:** Follow the Angular commit convention
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation update
- `refactor:` Code refactoring
- `test:` Test-related changes
- `chore:` Build/tooling changes

## 📄 License

This project is open-sourced under the [MIT License](LICENSE).
