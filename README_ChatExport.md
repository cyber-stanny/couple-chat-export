# 💑 Couple Chat Export

情侣/夫妻微信单聊记录提取工具 - 用于 AI 情感分析

## 简介

这个工具帮助你从微信本地数据库提取**单聊（私聊）**记录，导出为 AI 友好的格式，用于：
- 📊 情感趋势分析
- 💬 聊天模式洞察  
- 📈 关系发展时间线
- 🎯 高光时刻回顾

## ⚠️ 重要声明

- **仅供个人使用**：处理你自己的聊天记录
- **隐私保护**：提取完成后立即删除敏感文件
- **合规提示**：使用 chatlog 提取数据可能违反微信用户协议，请自行评估风险

## 前置要求

1. **安装 chatlog**
   ```bash
   go install github.com/sjzar/chatlog@latest
   ```
   或从 [releases](https://github.com/imldy/chatlog/releases) 下载预编译版本

2. **安装 Python 依赖**
   ```bash
   pip install requests
   ```

3. **微信电脑版**（macOS 或 Windows）

## 快速开始

### 第一步：准备 chatlog

在终端执行：

```bash
# 获取微信数据密钥
chatlog key

# 解密数据库
chatlog decrypt

# 启动 HTTP 服务
chatlog server
```

保持终端运行，服务会监听在 `http://127.0.0.1:5030`

### 第二步：运行提取脚本

```bash
python couple_chat_export.py --partner "老婆的备注名" --output ./my_chat
```

示例：
```bash
# 如果备注是"老婆"
python couple_chat_export.py --partner "老婆" --output ./7years

# 如果备注是"宝贝"
python couple_chat_export.py --partner "宝贝" --output ./couple_data
```

### 第三步：按提示操作

1. 脚本会列出所有联系人，自动匹配伴侣名字
2. 如果没有自动匹配，会显示候选列表让你选择
3. 等待数据导出完成（6.3GB 可能需要几分钟）

## 输出文件说明

```
my_chat/
├── chat_raw.json              # 完整原始数据（JSON格式）
├── chat_timeline.csv          # 时间线表格（Excel可打开）
├── stats.json                 # 统计报告
└── ai_analysis/               # AI 分析专用切片
    ├── dialogue_2023-01.txt   # 每月对话
    ├── dialogue_2023-02.txt
    ├── yearly_2023_summary.txt   # 年度汇总
    └── yearly_2024_summary.txt
```

## AI 分析指南

### 单月度分析

**文件**: `ai_analysis/dialogue_2023-05.txt`

**Prompt**:
```
请分析以下我和伴侣的聊天记录，输出：
1. 本月情感基调（积极/中性/消极，百分比）
2. 高频话题（Top 5）
3. 谁主动发起对话更多
4. 最暖心的3个瞬间
5. 如果有矛盾，简要说明原因

聊天记录：
[粘贴文件内容]
```

### 年度趋势分析

**文件**: `ai_analysis/yearly_2023_summary.txt`

**Prompt**:
```
请分析我们2023年的聊天趋势：
1. 这一年的关系发展曲线
2. 聊天频率变化及可能原因
3. 共同关注的话题演变
4. 给我们的年度关键词
5. 这一年的情感里程碑
```

### 数据可视化

用 `chat_timeline.csv` 在 Excel/Numbers 中制作：

- **折线图**: 每月消息量趋势
- **柱状图**: 每天24小时聊天分布
- **热力图**: 一周七天 × 24小时聊天密度
- **词云**: 高频关键词（需要额外工具）

## 安全清理

分析完成后，删除敏感数据：

```bash
# 删除 chatlog 解密的数据库
rm -rf ~/.chatlog/decrypted/
rm -rf ~/.chatlog/data/

# 可选：卸载 chatlog
rm ~/go/bin/chatlog  # 如果通过 go install 安装
```

保留导出的文本文件即可，这些是安全的。

## 隐私建议

| 方案 | 隐私性 | 便捷性 | 推荐度 |
|------|--------|--------|--------|
| **本地模型** (Ollama + DeepSeek) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 最推荐 |
| **Claude/GPT API** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 注意脱敏 |
| **网页版 Claude/GPT** | ⭐⭐ | ⭐⭐⭐⭐⭐ | 不要上传完整数据 |

**建议**：
- 先用本地模型做测试
- 上传到云端 AI 时，先用小样本测试 Prompt
- 绝对不要上传包含身份证号、银行卡号等敏感信息的内容

## 常见问题

### Q: macOS 提示无法获取密钥？

A: 需要临时关闭 SIP（系统完整性保护）：
1. 重启进入恢复模式（Intel: Cmd+R, Apple Silicon: 长按电源键）
2. 终端执行 `csrutil disable`
3. 重启后重试
4. 获取密钥后可重新启用 `csrutil enable`

### Q: 找不到联系人？

A: 脚本会显示消息数最多的私聊候选列表，从列表中选择即可。也可以输入完整的微信昵称搜索。

### Q: 导出数据量太大，AI 处理不了？

A: 使用 `ai_analysis/` 下的月度切片文件，每个月单独分析。或者使用年度汇总文件，已经是抽样后的数据。

### Q: 语音消息能导出吗？

A: chatlog 支持语音导出，但本脚本主要处理文字消息。语音需要额外用 Whisper 等工具转文字后再分析。

## 技术细节

- **语言**: Python 3.8+
- **依赖**: requests
- **数据来源**: chatlog HTTP API (http://127.0.0.1:5030)
- **输出格式**: JSON, CSV, TXT

## 致谢

- [chatlog](https://github.com/sjzar/chatlog) - 提供微信数据提取能力

## License

MIT - 仅供个人学习研究使用
