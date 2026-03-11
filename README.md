# 🔥 GitHub Daily Trending - 每日热门项目追踪

> 自动追踪 GitHub 上最热门的开源项目，每天定时推送，让你不错过任何技术趋势。

![GitHub Actions](https://img.shields.io/github/actions/workflow/status/gushuaialan1/github-daily-trending/daily.yml?color=blue&label=自动更新)
![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-在线-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📖 这是什么？

GitHub Daily Trending 是一个**全自动化的开源项目追踪工具**。它会：

- 🕘 每天北京时间 **9:00** 自动运行
- 🔍 抓取 GitHub 上最热门的 10 个新项目
- 🎨 生成精美的网页报告
- 📱 推送到飞书/钉钉/企业微信（可选）
- 📚 自动归档历史记录

**适合谁用？**
- 技术开发者：了解最新技术趋势
- 开源爱好者：发现有趣的项目
- 技术管理者：追踪行业动态
- 学习者：找到优质的学习资源

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🆓 **完全免费** | 利用 GitHub Actions + GitHub Pages，零成本运行 |
| 🎨 **精美设计** | 现代化暗色主题，支持手机和电脑访问 |
| 📊 **数据可视化** | 星标数、编程语言、Fork 数一目了然 |
| 🔔 **多端通知** | 支持飞书、钉钉、企业微信机器人推送 |
| 📜 **历史归档** | 每天的数据都会保存，可追溯历史趋势 |
| 🚀 **零维护** | 配置一次，永久自动运行 |

---

## 🚀 快速开始

### 第一步：Fork 仓库

点击页面右上角的 **「Fork」** 按钮，将本仓库复制到你的 GitHub 账号下。

> 💡 **什么是 Fork？**  
> Fork 就是把别人的项目复制一份到你自己的账号里，你可以自由修改，不影响原项目。

---

### 第二步：启用 GitHub Pages

1. 进入你 Fork 后的仓库
2. 点击 **Settings**（设置）
3. 左侧菜单选择 **Pages**
4. Source 选择 **GitHub Actions**
5. 点击 Save

> 💡 **什么是 GitHub Pages？**  
> GitHub Pages 是 GitHub 提供的免费静态网站托管服务。开启后，你的报告会自动发布为一个网页。

---

### 第三步：配置通知（可选但推荐）

如果你想每天收到飞书/钉钉推送，需要配置 webhook：

#### 飞书配置

1. **获取 Webhook URL**
   - 打开飞书，进入一个群聊
   - 点击群名 → 群设置 → 群机器人 → 添加机器人
   - 选择「自定义机器人」，起名「GitHub 热门项目」
   - 复制 webhook 地址（类似 `https://open.feishu.cn/open-apis/bot/v2/hook/xxxx`）

2. **添加到 GitHub Secrets**
   - 进入仓库 **Settings → Secrets and variables → Actions**
   - 点击 **New repository secret**
   - Name: `FEISHU_WEBHOOK`
   - Secret: 粘贴刚才复制的 webhook 地址
   - 点击 **Add secret**

#### 钉钉配置

步骤类似，Secret 名称改为 `DINGTALK_WEBHOOK`。

#### 企业微信配置

步骤类似，Secret 名称改为 `WECOM_WEBHOOK`。

---

### 第四步：测试运行

1. 进入仓库的 **Actions** 标签页
2. 点击左侧 **Daily GitHub Trending**
3. 点击右侧 **Run workflow** → **Run workflow**
4. 等待 1-2 分钟

如果显示绿色 ✅，说明运行成功！

---

### 第五步：查看报告

- **网页版**：访问 `https://你的用户名.github.io/github-daily-trending/`
- **飞书推送**：查看你配置的群聊

> 💡 **提示**：第一次部署可能需要 2-3 分钟才能访问网页。

---

## 📁 项目结构说明

```
github-daily-trending/
├── .github/workflows/
│   └── daily.yml          # 🕐 定时任务配置（每天9点运行）
│
├── docs/                   # 🌐 网页文件（GitHub Pages 托管）
│   ├── index.html         # 今日报告首页
│   ├── latest.html        # 最新报告（固定链接）
│   ├── history.html       # 历史记录页面
│   └── archive/           # 📚 每日归档文件
│
├── data/                   # 📊 JSON 原始数据
│   ├── latest.json        # 最新数据
│   └── trending-2024-03-11.json  # 历史数据
│
├── generate.py            # 🐍 核心脚本：抓取数据+生成网页
├── notify.py              # 📢 通知脚本：推送到飞书/钉钉
├── requirements.txt       # 📦 Python 依赖
└── README.md              # 📖 本说明文件
```

---

## 🔧 进阶配置

### 修改抓取数量

默认抓取 Top 10，想改成 Top 20？

编辑 `generate.py`：
```python
"per_page": 20  # 改成你想要的数量
```

### 修改定时时间

默认每天北京时间 9:00，想改成早上 8:00？

编辑 `.github/workflows/daily.yml`：
```yaml
# 每天北京时间 8:00（对应 UTC 0:00）
- cron: '0 0 * * *'
```

### 自定义网页主题

编辑 `generate.py` 中的 CSS 部分，修改颜色、字体等。

---

## 🛠️ 本地开发调试

如果你想在本地修改和测试：

```bash
# 1. 克隆仓库
git clone https://github.com/你的用户名/github-daily-trending.git
cd github-daily-trending

# 2. 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行生成脚本
python generate.py

# 5. 查看生成的网页
open docs/index.html  # Mac
# 或直接在浏览器打开 docs/index.html
```

---

## ❓ 常见问题

### Q: GitHub Pages 收费吗？
**A:** 公开仓库完全免费，没有流量限制。

### Q: 为什么我没有收到飞书推送？
**A:** 检查以下几点：
1. Webhook URL 是否正确复制？
2. Secret 名称是否为 `FEISHU_WEBHOOK`？
3. 飞书机器人是否在群里？
4. 查看 Actions 运行日志是否有错误

### Q: 可以抓取更多项目吗？
**A:** 可以，修改 `generate.py` 中的 `per_page` 参数，但建议不超过 50，避免 API 限制。

### Q: 报告什么时候更新？
**A:** 每天北京时间 9:00 自动更新。也可以随时手动触发 Actions。

### Q: 数据存在哪里？
**A:** 所有数据都在你的 GitHub 仓库中，`data/` 目录是原始 JSON，`docs/archive/` 是网页归档。

---

## 🎯 工作原理

```
┌─────────────────┐
│ GitHub Actions  │  ← 每天定时触发
│   (定时任务)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GitHub API     │  ← 抓取热门项目数据
│  (数据源)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  generate.py    │  ← 生成 HTML 网页
│  (数据处理)      │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐  ┌─────────┐
│Pages  │  │ 飞书/钉钉 │  ← 网页 + 推送
│(网页)  │  │ (通知)   │
└───────┘  └─────────┘
```

---

## 🤝 参与贡献

欢迎提交 Issue 和 PR！

- 发现问题？点击 [Issues](https://github.com/gushuaialan1/github-daily-trending/issues) 提交
- 想改进功能？Fork 后提交 Pull Request

---

## 📄 开源协议

MIT License - 详见 [LICENSE](LICENSE) 文件

这意味着你可以：
- ✅ 自由使用、修改、分发
- ✅ 用于商业项目
- ✅ 不需要开源你的衍生作品

只需要保留原始版权声明。

---

## 🙏 致谢

- [GitHub API](https://docs.github.com/en/rest) - 数据源
- [GitHub Actions](https://github.com/features/actions) - 自动化运行
- [GitHub Pages](https://pages.github.com/) - 免费托管

---

**如果这个项目对你有帮助，请给个 ⭐ Star 支持一下！**

有任何问题，欢迎随时问我。
