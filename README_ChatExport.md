# 💑 Couple Chat Export

情侣/夫妻微信单聊记录提取工具 - 基于 chatlog_alpha，用于 AI 情感分析

## 简介

这个工具帮助你从微信本地数据库提取**单聊（私聊）**记录，导出为 AI 友好的格式，用于：
- 📊 情感趋势分析
- 💬 聊天模式洞察  
- 📈 关系发展时间线
- 🎯 高光时刻回顾

## ⚠️ 重要声明

- **仅供个人使用**：处理你自己的聊天记录
- **隐私保护**：提取完成后立即删除敏感文件
- **合规提示**：使用第三方工具提取微信数据可能违反用户协议，请自行评估风险

---

## 🔧 前置要求

### 1. 下载 chatlog_alpha

原 [chatlog](https://github.com/sjzar/chatlog) 已被官方移除，现使用社区维护版本 **chatlog_alpha**：

**下载地址**：https://github.com/teest114514/chatlog_alpha/releases

根据你的系统下载：
- Windows: `chatlog_windows_amd64.exe`
- macOS: `chatlog_darwin_amd64` (Intel) 或 `chatlog_darwin_arm64` (Apple Silicon)

### 2. 准备解密 DLL

**重要**：chatlog_alpha 需要配合 DLL 文件使用

1. 从 release 页面下载 `wx_key1.dll` 和 `wx_key2.dll`
2. 在 chatlog 可执行文件同级目录创建文件夹：`lib/windows_x64/`
3. 将 DLL 文件放入该文件夹

目录结构示例：
```
chatlog/
├── chatlog.exe              # 主程序
├── lib/
│   └── windows_x64/
│       ├── wx_key1.dll      # 主要解密 DLL
│       └── wx_key2.dll      # 备用 DLL
```

### 3. 安装 Python 依赖

```bash
pip install requests
```

### 4. 微信电脑版

**测试支持的版本**：4.1.5.30（建议使用此版本或接近的版本）

---

## 🚀 快速开始

### 第一步：启动 chatlog_alpha

```bash
# 进入 chatlog 所在目录

# Windows
chatlog.exe key      # 获取数据密钥（需重启微信）
chatlog.exe server   # 启动 HTTP 服务

# macOS/Linux
./chatlog key
./chatlog server
```

**关键提示**：
- 获取密钥时需要**重启微信**，不是直接点击解密
- 保持终端运行，服务会监听在 `http://127.0.0.1:5030`
- 如果 wx_key1.dll 不行，尝试使用 wx_key2.dll

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
3. 等待数据导出完成

---

## 📁 输出文件说明

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

---

## 🤖 AI 分析指南

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

---

## 🔒 安全清理

分析完成后，删除敏感数据：

```bash
# 删除 chatlog 相关的临时文件
# Windows
rmdir /s /q %USERPROFILE%\.chatlog

# macOS/Linux
rm -rf ~/.chatlog/

# 可选：删除 chatlog 可执行文件和 DLL
```

保留导出的文本文件即可，这些是安全的。

---

## 🛡️ 隐私建议

| 方案 | 隐私性 | 便捷性 | 推荐度 |
|------|--------|--------|--------|
| **本地模型** (Ollama + DeepSeek) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 最推荐 |
| **Claude/GPT API** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 注意脱敏 |
| **网页版 Claude/GPT** | ⭐⭐ | ⭐⭐⭐⭐⭐ | 不要上传完整数据 |

**建议**：
- 先用本地模型做测试
- 上传到云端 AI 时，先用小样本测试 Prompt
- 绝对不要上传包含身份证号、银行卡号等敏感信息的内容
- 考虑将真实姓名替换为"我"/"TA"等代称后再上传

---

## ❓ 常见问题

### Q: macOS 提示无法获取密钥？

A: 需要临时关闭 SIP（系统完整性保护）：
1. 重启进入恢复模式（Intel: Cmd+R, Apple Silicon: 长按电源键）
2. 终端执行 `csrutil disable`
3. 重启后重试
4. 获取密钥后可重新启用 `csrutil enable`

### Q: DLL 文件放在哪里？

A: 必须与 chatlog 可执行文件同目录下的 `lib/windows_x64/` 文件夹中：
```
chatlog.exe
lib/
└── windows_x64/
    ├── wx_key1.dll
    └── wx_key2.dll
```

### Q: 提示"获取密钥失败"？

A: 
1. 确认使用的是**重启获取密钥**方式，不是直接解密
2. 尝试更换 wx_key2.dll
3. 确认微信版本在支持范围内（4.1.5.30）

### Q: 找不到联系人？

A: 脚本会显示消息数最多的私聊候选列表，从列表中选择即可。也可以输入完整的微信昵称搜索。

### Q: 导出数据量太大，AI 处理不了？

A: 使用 `ai_analysis/` 下的月度切片文件，每个月单独分析。或者使用年度汇总文件，已经是抽样后的数据。

### Q: 语音消息能导出吗？

A: chatlog_alpha 支持语音导出，但本脚本主要处理文字消息。语音需要额外用 Whisper 等工具转文字后再分析。

### Q: 为什么不用原版 chatlog？

A: 原版 chatlog (sjzar/chatlog) 已于 2025年10月收到微信官方函件后移除全部代码。chatlog_alpha 是社区维护的二次开发版本，基于 xiaofeng2042 的分支继续更新。

---

## 📝 技术细节

- **语言**: Python 3.8+
- **依赖**: requests
- **数据来源**: chatlog_alpha HTTP API (http://127.0.0.1:5030)
- **输出格式**: JSON, CSV, TXT
- **测试环境**: 微信 4.1.5.30

---

## 🙏 致谢

- [chatlog_alpha](https://github.com/teest114514/chatlog_alpha) - 社区维护的微信数据提取工具
- [chatlog](https://github.com/sjzar/chatlog) - 原项目作者 Sarv
- [wx_key](https://github.com/ycccccccy/wx_key) - 提供解密源码

---

## 📜 License

MIT - 仅供个人学习研究使用

---

## ⚠️ 免责声明

本工具仅供个人学习和数据备份使用。使用本工具可能违反微信用户协议，请自行评估法律风险。开发者不对使用本工具造成的任何损失或法律责任负责。
