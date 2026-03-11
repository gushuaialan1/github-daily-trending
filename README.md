# 🔥 GitHub Daily Trending

每日自动抓取 GitHub 热门项目，生成精美的网页报告。

## 🌟 特性

- **每日自动更新** - 通过 GitHub Actions 每天北京时间 9:00 自动运行
- **精美网页** - 现代化的暗色主题设计，支持移动端
- **历史归档** - 所有历史报告自动保存，可随时查看
- **零成本部署** - 使用 GitHub Pages 免费托管
- **自动通知** - 支持飞书/钉钉/企业微信等多种通知方式

## 🚀 快速开始

### 1. Fork 本仓库

点击右上角的 "Fork" 按钮，将仓库复制到你的账号下。

### 2. 启用 GitHub Pages

进入仓库的 **Settings → Pages**：
- Source: 选择 "GitHub Actions"

### 3. 配置通知（可选）

如需推送到飞书/钉钉/企业微信：

进入 **Settings → Secrets and variables → Actions**，添加以下 secrets：

| Secret 名称 | 说明 |
|------------|------|
| `FEISHU_WEBHOOK` | 飞书机器人 webhook URL |
| `DINGTALK_WEBHOOK` | 钉钉机器人 webhook URL |
| `WECOM_WEBHOOK` | 企业微信机器人 webhook URL |

### 4. 手动触发测试

进入 **Actions** 标签页，选择 "Daily GitHub Trending"，点击 "Run workflow" 手动触发。

### 5. 访问网页

部署完成后，访问链接：
```
https://你的用户名.github.io/github-daily-trending/
```

## 📁 项目结构

```
.
├── .github/workflows/
│   └── daily.yml          # GitHub Actions 工作流
├── docs/                   # GitHub Pages 部署目录
│   ├── index.html         # 今日报告
│   ├── latest.html        # 最新报告
│   ├── history.html       # 历史记录
│   └── archive/           # 历史归档
├── data/                   # JSON 数据
│   ├── latest.json        # 最新数据
│   └── trending-YYYY-MM-DD.json  # 历史数据
├── generate.py            # 主脚本
├── notify.py              # 通知脚本
├── requirements.txt       # Python 依赖
└── README.md              # 本文件
```

## 🔔 通知配置

### 飞书机器人

1. 在飞书群中添加自定义机器人
2. 复制 webhook URL
3. 添加到仓库 secrets: `FEISHU_WEBHOOK`

### 钉钉机器人

1. 在钉钉群中添加自定义机器人
2. 复制 webhook URL
3. 添加到仓库 secrets: `DINGTALK_WEBHOOK`

### 企业微信机器人

1. 在企业微信群中添加群机器人
2. 复制 webhook URL
3. 添加到仓库 secrets: `WECOM_WEBHOOK`

## 🛠️ 本地开发

```bash
# 克隆仓库
git clone https://github.com/你的用户名/github-daily-trending.git
cd github-daily-trending

# 安装依赖
pip install -r requirements.txt

# 运行生成脚本
python generate.py

# 查看结果
open docs/index.html
```

## 📝 自定义

### 修改抓取数量

编辑 `generate.py`：
```python
"per_page": 20  # 改为想要的数量
```

### 修改主题颜色

编辑 `generate.py` 中的 CSS 样式部分。

### 修改定时时间

编辑 `.github/workflows/daily.yml`：
```yaml
# 每天北京时间 8:00 (UTC 0:00)
- cron: '0 0 * * *'
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

由 [GitHub Actions](https://github.com/features/actions) 和 [GitHub Pages](https://pages.github.com/) 强力驱动 ❤️
