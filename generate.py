#!/usr/bin/env python3
"""
GitHub Trending Daily Report Generator
Generates HTML reports and deploys to GitHub Pages
Enhanced version with AI-powered Chinese translations
"""

import requests
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

OUTPUT_DIR = Path("docs")
DATA_DIR = Path("data")
CACHE_FILE = DATA_DIR / "translation_cache.json"

# Kimi API Configuration
KIMI_API_KEY = os.environ.get("KIMI_API_KEY", "")
KIMI_API_URL = "https://api.moonshot.cn/v1/chat/completions"

def load_translation_cache():
    """Load cached translations to avoid repeated API calls"""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_translation_cache(cache):
    """Save translation cache"""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def translate_description(repo_name, description, topics, language):
    """
    Translate project description to Chinese using Kimi API
    Returns a rich Chinese summary
    """
    if not KIMI_API_KEY:
        return None
    
    if not description:
        desc = "未提供项目描述"
    else:
        desc = description
    
    # Build cache key
    cache_key = f"{repo_name}:{hash(desc)}"
    cache = load_translation_cache()
    
    if cache_key in cache:
        print(f"  Using cached translation for {repo_name}")
        return cache[cache_key]
    
    # Prepare prompt
    topics_str = ", ".join(topics[:5]) if topics else "无"
    lang_str = language or "未标注"
    
    prompt = f"""请将以下 GitHub 项目的英文描述翻译成自然流畅的中文，并补充项目亮点。

项目名称：{repo_name}
编程语言：{lang_str}
标签：{topics_str}
原始描述：{desc}

请按以下格式输出：
1. 一句话中文简介（简洁明了）
2. 核心功能/亮点（2-3点，用•符号）
3. 适用场景（1句话）

输出示例格式：
一句话简介：这是一个...
核心亮点：
• 支持xxx功能
• 提供xxx能力
适用场景：适合需要...的开发者"""

    try:
        resp = requests.post(
            KIMI_API_URL,
            headers={
                "Authorization": f"Bearer {KIMI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "moonshot-v1-8k",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            },
            timeout=30
        )
        resp.raise_for_status()
        result = resp.json()
        translation = result["choices"][0]["message"]["content"].strip()
        
        # Cache the result
        cache[cache_key] = translation
        save_translation_cache(cache)
        
        print(f"  Translated {repo_name}")
        return translation
        
    except Exception as e:
        print(f"  Translation failed for {repo_name}: {e}")
        return None

def parse_translation(translation_text):
    """Parse the translation into structured HTML"""
    if not translation_text:
        return ""
    
    lines = translation_text.split('\n')
    html_parts = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 一句话简介
        if line.startswith('一句话简介：') or line.startswith('一句话介绍：'):
            content = line.split('：', 1)[1] if '：' in line else line
            html_parts.append(f'<div class="repo-summary">{content}</div>')
        
        # 核心亮点标题
        elif line.startswith('核心亮点：') or line.startswith('核心功能：'):
            html_parts.append('<div class="repo-highlights-title">✨ 核心亮点</div>')
        
        # 亮点列表项
        elif line.startswith('•') or line.startswith('-') or line.startswith('*'):
            content = line[1:].strip()
            html_parts.append(f'<div class="repo-highlight-item">{content}</div>')
        
        # 适用场景
        elif line.startswith('适用场景：') or line.startswith('适用人群：'):
            content = line.split('：', 1)[1] if '：' in line else line
            html_parts.append(f'<div class="repo-scene">🎯 {line}</div>')
    
    # If no structured format, treat as plain text
    if not html_parts:
        html_parts.append(f'<div class="repo-summary">{translation_text}</div>')
    
    return '\n'.join(html_parts)

TECH_TERMS = {
    "ai": "人工智能",
    "artificial intelligence": "人工智能",
    "machine learning": "机器学习",
    "deep learning": "深度学习",
    "llm": "大语言模型",
    "large language model": "大语言模型",
    "chatbot": "聊天机器人",
    "automation": "自动化",
    "framework": "框架",
    "library": "库",
    "tool": "工具",
    "cli": "命令行工具",
    "api": "API 接口",
    "server": "服务器",
    "client": "客户端",
    "database": "数据库",
    "visualization": "可视化",
    "dashboard": "仪表盘",
    "parser": "解析器",
    "scraper": "爬虫",
    "crawler": "爬虫",
    "bot": "机器人",
    "plugin": "插件",
    "extension": "扩展",
    "sdk": "开发工具包",
    "template": "模板",
    "boilerplate": "脚手架",
    "starter": "启动模板",
    "kit": "工具包",
    "generator": "生成器",
    "builder": "构建工具",
    "compiler": "编译器",
    "interpreter": "解释器",
    "runtime": "运行时",
    "vm": "虚拟机",
    "container": "容器",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "microservice": "微服务",
    "serverless": "无服务器",
    "blockchain": "区块链",
    "crypto": "加密货币",
    "web3": "Web3",
    "nft": "NFT",
    "smart contract": "智能合约",
    "game": "游戏",
    "gaming": "游戏",
    "web": "网页",
    "mobile": "移动端",
    "desktop": "桌面端",
    "app": "应用",
    "application": "应用",
    "pwa": "渐进式网页应用",
    "spa": "单页应用",
    "ssr": "服务端渲染",
    "csr": "客户端渲染",
    "static site": "静态网站",
    "cms": "内容管理系统",
    "crm": "客户关系管理",
    "erp": "企业资源规划",
    "e-commerce": "电商",
    "blog": "博客",
    "forum": "论坛",
    "wiki": "维基",
    "documentation": "文档",
    "docs": "文档",
    "tutorial": "教程",
    "guide": "指南",
    "example": "示例",
    "demo": "演示",
    "sample": "示例",
    "test": "测试",
    "testing": "测试",
    "benchmark": "性能测试",
    "profiler": "性能分析器",
    "debugger": "调试器",
    "linter": "代码检查工具",
    "formatter": "代码格式化工具",
    "preprocessor": "预处理器",
    "bundler": "打包工具",
    "minifier": "压缩工具",
    "transpiler": "转译器",
    "polyfill": "兼容性填充",
    "shim": "适配层",
    "wrapper": "封装库",
    "binding": "绑定",
    "bridge": "桥接",
    "adapter": "适配器",
    "driver": "驱动",
    "middleware": "中间件",
    "proxy": "代理",
    "gateway": "网关",
    "router": "路由器",
    "load balancer": "负载均衡",
    "cache": "缓存",
    "queue": "队列",
    "message queue": "消息队列",
    "pubsub": "发布订阅",
    "event": "事件",
    "stream": "流",
    "pipeline": "管道",
    "workflow": "工作流",
    "orchestration": "编排",
    "scheduler": "调度器",
    "cron": "定时任务",
    "job": "任务",
    "task": "任务",
    "worker": "工作进程",
    "thread": "线程",
    "process": "进程",
    "concurrent": "并发",
    "parallel": "并行",
    "async": "异步",
    "sync": "同步",
    "reactive": "响应式",
    "observable": "可观察对象",
    "state management": "状态管理",
    "store": "存储",
    "session": "会话",
    "cookie": "Cookie",
    "jwt": "JWT 令牌",
    "oauth": "OAuth 认证",
    "sso": "单点登录",
    "auth": "认证",
    "authentication": "认证",
    "authorization": "授权",
    "permission": "权限",
    "role": "角色",
    "user": "用户",
    "account": "账户",
    "profile": "个人资料",
    "dashboard": "控制台",
    "admin": "管理后台",
    "cms": "内容管理",
    "editor": "编辑器",
    "ide": "集成开发环境",
    "repl": "交互式解释器",
    "notebook": "笔记本",
    "jupyter": "Jupyter",
    "colab": "Colab",
    "playground": "沙盒环境",
    "sandbox": "沙盒",
    "shell": "命令行",
    "terminal": "终端",
    "console": "控制台",
    "gui": "图形界面",
    "ui": "用户界面",
    "ux": "用户体验",
    "design": "设计",
    "component": "组件",
    "widget": "小部件",
    "icon": "图标",
    "font": "字体",
    "theme": "主题",
    "style": "样式",
    "css": "CSS",
    "sass": "Sass",
    "less": "Less",
    "styled": "样式化",
    "animation": "动画",
    "transition": "过渡",
    "effect": "特效",
    "3d": "3D",
    "vr": "虚拟现实",
    "ar": "增强现实",
    "mr": "混合现实",
    "xr": "扩展现实",
    "iot": "物联网",
    "embedded": "嵌入式",
    "hardware": "硬件",
    "firmware": "固件",
    "kernel": "内核",
    "os": "操作系统",
    "linux": "Linux",
    "windows": "Windows",
    "macos": "macOS",
    "ios": "iOS",
    "android": "Android",
    "react": "React",
    "vue": "Vue",
    "angular": "Angular",
    "svelte": "Svelte",
    "nextjs": "Next.js",
    "nuxt": "Nuxt",
    "express": "Express",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "spring": "Spring",
    "rails": "Rails",
    "laravel": "Laravel",
    "go": "Go",
    "golang": "Go",
    "rust": "Rust",
    "python": "Python",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "java": "Java",
    "kotlin": "Kotlin",
    "swift": "Swift",
    "csharp": "C#",
    "cpp": "C++",
    "c++": "C++",
    "c": "C",
    "ruby": "Ruby",
    "php": "PHP",
    "perl": "Perl",
    "lua": "Lua",
    "r": "R",
    "scala": "Scala",
    "clojure": "Clojure",
    "haskell": "Haskell",
    "elixir": "Elixir",
    "erlang": "Erlang",
    "ocaml": "OCaml",
    "fsharp": "F#",
    "vb": "Visual Basic",
    "objective-c": "Objective-C",
    "dart": "Dart",
    "flutter": "Flutter",
    "electron": "Electron",
    "tauri": "Tauri",
    "react native": "React Native",
    "ionic": "Ionic",
    "cordova": "Cordova",
    "capacitor": "Capacitor",
    "nativescript": "NativeScript",
    "unity": "Unity",
    "unreal": "Unreal Engine",
    "godot": "Godot",
    "blender": "Blender",
    "maya": "Maya",
    "3dsmax": "3ds Max",
    "photoshop": "Photoshop",
    "illustrator": "Illustrator",
    "figma": "Figma",
    "sketch": "Sketch",
    "xd": "Adobe XD",
    "principle": "Principle",
    "framer": "Framer",
    "proto": "Proto",
    "axure": "Axure",
    "balsamiq": "Balsamiq",
    "wireframe": "线框图",
    "mockup": "原型",
    "prototype": "原型",
    "spec": "规范",
    "design system": "设计系统",
    "component library": "组件库",
    "ui kit": "UI 套件",
    "pattern": "模式",
    "guideline": "指南",
    "standard": "标准",
    "best practice": "最佳实践",
    "convention": "约定",
    "style guide": "风格指南",
    "coding standard": "编码规范",
    "lint": "代码检查",
    "format": "格式化",
    "refactor": "重构",
    "clean code": "整洁代码",
    "solid": "SOLID 原则",
    "dry": "DRY 原则",
    "kiss": "KISS 原则",
    "yagni": "YAGNI 原则",
    "patterns": "设计模式",
    "architecture": "架构",
    "microservices": "微服务",
    "monolith": "单体应用",
    "soa": "面向服务架构",
    "event-driven": "事件驱动",
    "cqrs": "CQRS 模式",
    "event sourcing": "事件溯源",
    "ddd": "领域驱动设计",
    "tdd": "测试驱动开发",
    "bdd": "行为驱动开发",
    "agile": "敏捷开发",
    "scrum": "Scrum",
    "kanban": "看板",
    "devops": "DevOps",
    "ci/cd": "CI/CD",
    "continuous integration": "持续集成",
    "continuous deployment": "持续部署",
    "continuous delivery": "持续交付",
    "infrastructure": "基础设施",
    "iac": "基础设施即代码",
    "terraform": "Terraform",
    "pulumi": "Pulumi",
    "ansible": "Ansible",
    "puppet": "Puppet",
    "chef": "Chef",
    "vagrant": "Vagrant",
    "packer": "Packer",
    "nomad": "Nomad",
    "consul": "Consul",
    "vault": "Vault",
    "monitoring": "监控",
    "logging": "日志",
    "tracing": "链路追踪",
    "observability": "可观测性",
    "metrics": "指标",
    "alerting": "告警",
    "grafana": "Grafana",
    "prometheus": "Prometheus",
    "elk": "ELK 栈",
    "elasticsearch": "Elasticsearch",
    "logstash": "Logstash",
    "kibana": "Kibana",
    "fluentd": "Fluentd",
    "jaeger": "Jaeger",
    "zipkin": "Zipkin",
    "opentelemetry": "OpenTelemetry",
    "apm": "应用性能监控",
    "profiling": "性能分析",
    "load testing": "负载测试",
    "stress testing": "压力测试",
    "chaos engineering": "混沌工程",
    "security": "安全",
    "vulnerability": "漏洞",
    "penetration testing": "渗透测试",
    "audit": "审计",
    "compliance": "合规",
    "gdpr": "GDPR",
    "hipaa": "HIPAA",
    "soc2": "SOC 2",
    "iso27001": "ISO 27001",
    "encryption": "加密",
    "hash": "哈希",
    "signature": "签名",
    "certificate": "证书",
    "ssl": "SSL",
    "tls": "TLS",
    "https": "HTTPS",
    "oauth2": "OAuth 2.0",
    "openid": "OpenID",
    "saml": "SAML",
    "ldap": "LDAP",
    "active directory": "Active Directory",
    "firewall": "防火墙",
    "vpn": "VPN",
    "proxy": "代理",
    "waf": "Web 应用防火墙",
    "ddos": "DDoS 防护",
    "bot detection": "机器人检测",
    "captcha": "验证码",
    "mfa": "多因素认证",
    "2fa": "双因素认证",
    "biometric": "生物识别",
    "fingerprint": "指纹",
    "face recognition": "人脸识别",
    "voice recognition": "语音识别",
    "natural language": "自然语言",
    "nlp": "自然语言处理",
    "computer vision": "计算机视觉",
    "cv": "计算机视觉",
    "image processing": "图像处理",
    "video processing": "视频处理",
    "audio processing": "音频处理",
    "speech recognition": "语音识别",
    "text to speech": "文本转语音",
    "ocr": "OCR 文字识别",
    "face detection": "人脸检测",
    "object detection": "目标检测",
    "segmentation": "图像分割",
    "classification": "分类",
    "regression": "回归",
    "clustering": "聚类",
    "recommendation": "推荐系统",
    "search": "搜索",
    "indexing": "索引",
    "ranking": "排序",
    "filtering": "过滤",
    "sorting": "排序",
    "pagination": "分页",
    "caching": "缓存",
    "compression": "压缩",
    "encoding": "编码",
    "decoding": "解码",
    "serialization": "序列化",
    "deserialization": "反序列化",
    "parsing": "解析",
    "tokenization": "分词",
    "stemming": "词干提取",
    "lemmatization": "词形还原",
    "ner": "命名实体识别",
    "pos tagging": "词性标注",
    "sentiment analysis": "情感分析",
    "topic modeling": "主题建模",
    "word embedding": "词嵌入",
    "vector": "向量",
    "embedding": "嵌入",
    "similarity": "相似度",
    "distance": "距离",
    "cluster": "聚类",
    "dimensionality reduction": "降维",
    "pca": "PCA",
    "tsne": "t-SNE",
    "umap": "UMAP",
    "manifold learning": "流形学习",
    "autoencoder": "自编码器",
    "gan": "生成对抗网络",
    "vae": "变分自编码器",
    "transformer": "Transformer",
    "bert": "BERT",
    "gpt": "GPT",
    "llama": "LLaMA",
    "claude": "Claude",
    "diffusion": "扩散模型",
    "stable diffusion": "Stable Diffusion",
    "midjourney": "Midjourney",
    "dall-e": "DALL-E",
    "whisper": "Whisper",
    "clip": "CLIP",
}

def get_tech_summary(description, topics, language):
    """Generate a simple Chinese summary based on description and topics"""
    if not description:
        return ""
    
    desc_lower = description.lower()
    matched_terms = []
    
    for term, chinese in TECH_TERMS.items():
        if term in desc_lower and chinese not in matched_terms:
            matched_terms.append(chinese)
    
    matched_terms = matched_terms[:3]
    
    if matched_terms:
        return "相关技术：" + "、".join(matched_terms)
    
    if language:
        lang_map = {
            "Python": "Python 项目",
            "JavaScript": "JavaScript 项目",
            "TypeScript": "TypeScript 项目",
            "Java": "Java 项目",
            "Go": "Go 语言项目",
            "Rust": "Rust 项目",
            "C++": "C++ 项目",
            "C": "C 语言项目",
            "Ruby": "Ruby 项目",
            "PHP": "PHP 项目",
            "Swift": "Swift 项目",
            "Kotlin": "Kotlin 项目",
        }
        return lang_map.get(language, f"{language} 项目")
    
    return ""

def format_datetime(iso_string):
    """Format ISO datetime to Chinese readable format"""
    if not iso_string:
        return "未知"
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.strftime("%Y年%m月%d日")
    except:
        return iso_string[:10] if iso_string else "未知"

def get_license_info(license_info):
    """Get license display name"""
    if not license_info:
        return None
    spdx = license_info.get("spdx_id", "")
    name = license_info.get("name", "")
    
    license_map = {
        "MIT": "MIT 协议",
        "GPL-3.0": "GPL v3",
        "GPL-2.0": "GPL v2",
        "Apache-2.0": "Apache 2.0",
        "BSD-3-Clause": "BSD 3-Clause",
        "BSD-2-Clause": "BSD 2-Clause",
        "MPL-2.0": "Mozilla 2.0",
        "LGPL-3.0": "LGPL v3",
        "AGPL-3.0": "AGPL v3",
        "Unlicense": "无版权限制",
        "CC0-1.0": "CC0",
    }
    
    return license_map.get(spdx, name) if spdx else name

def ensure_dirs():
    OUTPUT_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)

def get_github_token():
    return os.environ.get("GITHUB_TOKEN", "")

def get_headers():
    token = get_github_token()
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "github-daily-trending-bot"
    }
    if token:
        headers["Authorization"] = f"token {token}"
    return headers

def get_trending_repos():
    """Fetch trending repositories using GitHub Search API"""
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    url = "https://api.github.com/search/repositories"
    params = {
        "q": f"created:>{week_ago}",
        "sort": "stars",
        "order": "desc",
        "per_page": 10
    }
    
    try:
        resp = requests.get(url, params=params, headers=get_headers(), timeout=30)
        resp.raise_for_status()
        repos = resp.json().get("items", [])
        if repos:
            return repos
    except Exception as e:
        print(f"Error fetching weekly trending: {e}")
    
    # Fallback
    try:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        params = {
            "q": f"stars:>100 pushed:>{yesterday}",
            "sort": "stars",
            "order": "desc",
            "per_page": 10
        }
        resp = requests.get(url, params=params, headers=get_headers(), timeout=30)
        resp.raise_for_status()
        return resp.json().get("items", [])
    except Exception as e:
        print(f"Fallback error: {e}")
        return []

def save_json(repos, date_str):
    """Save raw data as JSON"""
    data = {
        "date": date_str,
        "generated_at": datetime.now().isoformat(),
        "repos": repos
    }
    filepath = DATA_DIR / f"trending-{date_str}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    latest_path = DATA_DIR / "latest.json"
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Saved JSON to {filepath}")

def generate_html(repos, date_str):
    """Generate beautiful HTML report with AI translations"""
    today_display = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y年%m月%d日")
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub 热门项目 - {today_display}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #e2e8f0;
            min-height: 100vh;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 40px 30px;
            background: rgba(255,255,255,0.05);
            border-radius: 24px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }}
        h1 {{
            font-size: 2.8em;
            margin-bottom: 12px;
            background: linear-gradient(90deg, #fbbf24, #f59e0b, #ef4444);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .date {{
            color: #94a3b8;
            font-size: 1.15em;
            letter-spacing: 0.5px;
        }}
        .subtitle {{
            color: #64748b;
            margin-top: 15px;
            font-size: 0.95em;
            line-height: 1.6;
        }}
        .repo {{
            background: rgba(255,255,255,0.03);
            border-radius: 20px;
            padding: 28px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.06);
            transition: all 0.3s ease;
        }}
        .repo:hover {{
            transform: translateY(-4px);
            box-shadow: 0 20px 60px rgba(0,0,0,0.4);
            background: rgba(255,255,255,0.05);
            border-color: rgba(255,255,255,0.12);
        }}
        .repo-header {{
            display: flex;
            align-items: center;
            margin-bottom: 16px;
        }}
        .rank {{
            width: 46px;
            height: 46px;
            border-radius: 14px;
            background: linear-gradient(135deg, #fbbf24, #f59e0b);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.3em;
            margin-right: 16px;
            color: #0f172a;
            flex-shrink: 0;
        }}
        .repo-title {{
            flex: 1;
            min-width: 0;
        }}
        .repo-name {{
            font-size: 1.35em;
            font-weight: 600;
            margin-bottom: 4px;
        }}
        .repo-name a {{
            color: #60a5fa;
            text-decoration: none;
            transition: color 0.2s;
            word-break: break-all;
        }}
        .repo-name a:hover {{
            color: #93c5fd;
            text-decoration: underline;
        }}
        .repo-owner {{
            color: #64748b;
            font-size: 0.85em;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .repo-owner img {{
            width: 18px;
            height: 18px;
            border-radius: 50%;
        }}
        .repo-desc {{
            color: #94a3b8;
            line-height: 1.6;
            margin-bottom: 14px;
            font-size: 0.9em;
            font-style: italic;
            border-left: 2px solid rgba(148, 163, 184, 0.3);
            padding-left: 12px;
        }}
        .repo-desc:empty {{ display: none; }}
        .repo-desc-label {{
            color: #64748b;
            font-size: 0.75em;
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .repo-summary {{
            color: #e2e8f0;
            font-size: 1.05em;
            line-height: 1.7;
            margin-bottom: 12px;
            font-weight: 500;
        }}
        .repo-highlights-title {{
            color: #fbbf24;
            font-size: 0.85em;
            margin: 12px 0 6px 0;
            font-weight: 600;
        }}
        .repo-highlight-item {{
            color: #cbd5e1;
            font-size: 0.9em;
            line-height: 1.6;
            margin: 4px 0 4px 16px;
            position: relative;
        }}
        .repo-highlight-item::before {{
            content: "•";
            color: #fbbf24;
            position: absolute;
            left: -12px;
        }}
        .repo-scene {{
            color: #34d399;
            font-size: 0.85em;
            margin-top: 10px;
            padding: 6px 12px;
            background: rgba(52, 211, 153, 0.1);
            border-radius: 8px;
            display: inline-block;
        }}
        .repo-meta {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            font-size: 0.85em;
            margin-top: 16px;
            margin-bottom: 12px;
        }}
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 5px;
            padding: 5px 12px;
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
        }}
        .stars {{ color: #fbbf24; }}
        .lang {{ color: #a78bfa; }}
        .forks {{ color: #94a3b8; }}
        .license {{ color: #34d399; }}
        .topics {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 12px;
        }}
        .topic {{
            padding: 4px 12px;
            background: rgba(96, 165, 250, 0.15);
            color: #60a5fa;
            border-radius: 12px;
            font-size: 0.8em;
        }}
        .repo-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid rgba(255,255,255,0.06);
            font-size: 0.8em;
            color: #64748b;
        }}
        .nav {{
            display: flex;
            justify-content: center;
            gap: 12px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}
        .nav a {{
            padding: 12px 24px;
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            color: #94a3b8;
            text-decoration: none;
            font-size: 0.95em;
            transition: all 0.2s;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .nav a:hover {{
            background: rgba(255,255,255,0.1);
            color: #e2e8f0;
        }}
        .nav a.active {{
            background: rgba(251, 191, 36, 0.15);
            color: #fbbf24;
            border-color: rgba(251, 191, 36, 0.3);
        }}
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 30px;
            color: #64748b;
            font-size: 0.9em;
        }}
        .footer a {{
            color: #60a5fa;
            text-decoration: none;
        }}
        .ai-badge {{
            display: inline-block;
            padding: 2px 8px;
            background: linear-gradient(135deg, #fbbf24, #f59e0b);
            color: #0f172a;
            font-size: 0.7em;
            font-weight: bold;
            border-radius: 4px;
            margin-left: 8px;
            vertical-align: middle;
        }}
        @media (max-width: 600px) {{
            h1 {{ font-size: 2em; }}
            .repo {{ padding: 20px; }}
            .rank {{ width: 40px; height: 40px; font-size: 1.1em; }}
            .repo-name {{ font-size: 1.15em; }}
            .repo-meta {{ gap: 10px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔥 GitHub 热门项目</h1>
            <div class="date">{today_display} · 今日新星 Top 10</div>
            <div class="subtitle">
                自动追踪 GitHub 上最近一周最受欢迎的开源项目<br>
                发现前沿技术、创新工具和优秀的代码实践
            </div>
        </header>
        
        <div class="nav">
            <a href="index.html" class="active">📊 今日榜单</a>
            <a href="history.html">📚 历史归档</a>
            <a href="https://github.com/{os.environ.get('GITHUB_REPOSITORY', 'user/repo')}" target="_blank">⚙️ 仓库设置</a>
        </div>
"""
    
    print("Generating AI translations...")
    for i, repo in enumerate(repos[:10], 1):
        name = repo.get("full_name", "Unknown")
        url = repo.get("html_url", "#")
        desc = repo.get("description") or ""
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)
        lang = repo.get("language") or "未标注"
        topics = repo.get("topics", [])
        created_at = format_datetime(repo.get("created_at"))
        pushed_at = format_datetime(repo.get("pushed_at"))
        license_info = get_license_info(repo.get("license"))
        owner = repo.get("owner", {})
        owner_name = owner.get("login", "")
        owner_avatar = owner.get("avatar_url", "")
        
        # Get AI translation
        translation = translate_description(name, desc, topics, lang)
        translation_html = parse_translation(translation) if translation else ""
        
        # Build topics HTML
        topics_html = ""
        if topics:
            topics_html = '<div class="topics">' + ''.join([f'<span class="topic">{t}</span>' for t in topics[:5]]) + '</div>'
        
        # Build license HTML
        license_html = f'<div class="meta-item license">📄 {license_info}</div>' if license_info else ""
        
        # Build original description HTML (collapsed)
        orig_desc_html = f'<div class="repo-desc">{desc}</div>' if desc else ""
        
        # AI badge
        ai_badge = '<span class="ai-badge">AI</span>' if translation else ""
        
        html += f"""
        <div class="repo">
            <div class="repo-header">
                <div class="rank">{i}</div>
                <div class="repo-title">
                    <div class="repo-name"><a href="{url}" target="_blank">{name}</a>{ai_badge}</div>
                    <div class="repo-owner">
                        {"<img src='" + owner_avatar + "' alt=''>" if owner_avatar else "👤"}
                        {owner_name} · 创建于 {created_at}
                    </div>
                </div>
            </div>
            {translation_html}
            {orig_desc_html}
            {topics_html}
            <div class="repo-meta">
                <div class="meta-item stars">⭐ {stars:,}</div>
                <div class="meta-item lang">🟣 {lang}</div>
                <div class="meta-item forks">🍴 {forks:,}</div>
                {license_html}
            </div>
            <div class="repo-footer">
                <span>📝 最后更新于 {pushed_at}</span>
                <span>🔗 <a href="{url}" target="_blank">查看仓库 →</a></span>
            </div>
        </div>
"""
    
    html += f"""
        <div class="footer">
            <p>📅 每日自动更新 · 由 GitHub Actions 生成 · 中文翻译由 AI 提供</p>
            <p style="margin-top: 10px; font-size: 0.85em;">
                生成时间：{datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")} · 
                <a href="https://github.com/gushuaialan1/github-daily-trending" target="_blank">GitHub 仓库</a>
            </p>
        </div>
    </div>
</body>
</html>"""
    
    return html

def generate_history_page():
    """Generate history index page"""
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub 热门项目 - 历史记录</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang SC", sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #e2e8f0;
            min-height: 100vh;
            padding: 40px 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        header {
            text-align: center;
            margin-bottom: 40px;
            padding: 40px 30px;
            background: rgba(255,255,255,0.05);
            border-radius: 24px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        h1 {
            font-size: 2.5em;
            margin-bottom: 12px;
            background: linear-gradient(90deg, #fbbf24, #f59e0b, #ef4444);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .nav {
            display: flex;
            justify-content: center;
            gap: 12px;
            margin-bottom: 30px;
        }
        .nav a {
            padding: 12px 24px;
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            color: #94a3b8;
            text-decoration: none;
            font-size: 0.95em;
            transition: all 0.2s;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .nav a:hover {
            background: rgba(255,255,255,0.1);
            color: #e2e8f0;
        }
        .nav a.active {
            background: rgba(251, 191, 36, 0.15);
            color: #fbbf24;
            border-color: rgba(251, 191, 36, 0.3);
        }
        .date-list {
            background: rgba(255,255,255,0.03);
            border-radius: 20px;
            padding: 30px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.06);
        }
        .date-item {
            padding: 18px 24px;
            border-bottom: 1px solid rgba(255,255,255,0.06);
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.2s;
        }
        .date-item:last-child {
            border-bottom: none;
        }
        .date-item:hover {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            margin: 0 -8px;
            padding-left: 32px;
            padding-right: 32px;
        }
        .date-item a {
            color: #60a5fa;
            text-decoration: none;
            font-size: 1.1em;
            font-weight: 500;
        }
        .date-item a:hover {
            text-decoration: underline;
        }
        .arrow {
            color: #64748b;
        }
        .footer {
            text-align: center;
            margin-top: 50px;
            color: #64748b;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📚 历史归档</h1>
            <p style="color: #94a3b8; margin-top: 10px;">查看往期 GitHub 热门项目报告</p>
        </header>
        
        <div class="nav">
            <a href="index.html">📊 今日榜单</a>
            <a href="history.html" class="active">📚 历史归档</a>
        </div>
        
        <div class="date-list" id="dateList">
            <div class="date-item">
                <a href="latest.html">📅 最新报告（今日）</a>
                <span class="arrow">→</span>
            </div>
        </div>
        
        <div class="footer">
            <p>💡 提示：历史数据每日自动归档保存</p>
        </div>
    </div>
    
    <script>
        fetch('data/latest.json')
            .then(r => r.json())
            .then(data => {
                const list = document.getElementById('dateList');
                const date = data.date;
                if (date) {
                    const item = document.createElement('div');
                    item.className = 'date-item';
                    item.innerHTML = `<a href="archive/${date}.html">📅 ${date} 的报告</a><span class="arrow">→</span>`;
                    list.appendChild(item);
                }
            })
            .catch(() => {});
    </script>
</body>
</html>"""
    return html

def main():
    ensure_dirs()
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    print(f"Generating report for {date_str}...")
    
    print("Fetching trending repos...")
    repos = get_trending_repos()
    
    if not repos:
        print("No repos found!")
        return
    
    print(f"Found {len(repos)} repos")
    
    # Save JSON data
    save_json(repos, date_str)
    
    # Generate HTML reports with AI translations
    html = generate_html(repos, date_str)
    
    # Save as index.html
    index_path = OUTPUT_DIR / "index.html"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved index.html")
    
    # Save as latest.html
    latest_path = OUTPUT_DIR / "latest.html"
    with open(latest_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved latest.html")
    
    # Save dated archive
    archive_dir = OUTPUT_DIR / "archive"
    archive_dir.mkdir(exist_ok=True)
    archive_path = archive_dir / f"{date_str}.html"
    with open(archive_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved archive/{date_str}.html")
    
    # Generate history page
    history_path = OUTPUT_DIR / "history.html"
    with open(history_path, "w", encoding="utf-8") as f:
        f.write(generate_history_page())
    print(f"Saved history.html")
    
    # Copy data to docs
    docs_data_dir = OUTPUT_DIR / "data"
    docs_data_dir.mkdir(exist_ok=True)
    import shutil
    shutil.copy(DATA_DIR / "latest.json", docs_data_dir / "latest.json")
    
    print("Done!")

if __name__ == "__main__":
    main()
