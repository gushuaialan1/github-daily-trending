#!/usr/bin/env python3
"""
GitHub Trending Daily Report Generator
Generates HTML reports and deploys to GitHub Pages
"""

import requests
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

OUTPUT_DIR = Path("docs")
DATA_DIR = Path("data")

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
    """
    Fetch trending repositories using GitHub Search API
    Gets repos with most stars created in the last week
    """
    # Try last 7 days for new repos
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    # Query for repos created in last week, sorted by stars
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
    
    # Fallback: search for repos with high stars pushed recently
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
    
    # Also save as latest.json
    latest_path = DATA_DIR / "latest.json"
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Saved JSON to {filepath}")

def generate_html(repos, date_str):
    """Generate beautiful HTML report"""
    today_display = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y年%m月%d日")
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub Trending - {today_display}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
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
            margin-bottom: 14px;
        }}
        .rank {{
            width: 42px;
            height: 42px;
            border-radius: 12px;
            background: linear-gradient(135deg, #fbbf24, #f59e0b);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.2em;
            margin-right: 16px;
            color: #0f172a;
        }}
        .repo-name {{
            font-size: 1.35em;
            font-weight: 600;
        }}
        .repo-name a {{
            color: #60a5fa;
            text-decoration: none;
            transition: color 0.2s;
        }}
        .repo-name a:hover {{
            color: #93c5fd;
            text-decoration: underline;
        }}
        .repo-desc {{
            color: #cbd5e1;
            line-height: 1.7;
            margin-bottom: 16px;
            font-size: 0.95em;
        }}
        .repo-meta {{
            display: flex;
            gap: 24px;
            flex-wrap: wrap;
            font-size: 0.9em;
        }}
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .stars {{ color: #fbbf24; }}
        .lang {{ color: #a78bfa; }}
        .forks {{ color: #94a3b8; }}
        .nav {{
            display: flex;
            justify-content: center;
            gap: 12px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}
        .nav a {{
            padding: 10px 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            color: #94a3b8;
            text-decoration: none;
            font-size: 0.9em;
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
        @media (max-width: 600px) {{
            h1 {{ font-size: 2em; }}
            .repo {{ padding: 20px; }}
            .rank {{ width: 36px; height: 36px; font-size: 1em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔥 GitHub Trending</h1>
            <div class="date">{today_display} · 今日热门 Top 10</div>
        </header>
        
        <div class="nav">
            <a href="index.html" class="active">今日</a>
            <a href="history.html">历史</a>
            <a href="https://github.com/{os.environ.get('GITHUB_REPOSITORY', 'user/repo')}" target="_blank">GitHub →</a>
        </div>
"""
    
    for i, repo in enumerate(repos[:10], 1):
        name = repo.get("full_name", "Unknown")
        url = repo.get("html_url", "#")
        desc = repo.get("description") or "暂无描述"
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)
        lang = repo.get("language") or "未知"
        
        html += f"""
        <div class="repo">
            <div class="repo-header">
                <div class="rank">{i}</div>
                <div class="repo-name"><a href="{url}" target="_blank">{name}</a></div>
            </div>
            <div class="repo-desc">{desc}</div>
            <div class="repo-meta">
                <div class="meta-item stars">⭐ {stars:,}</div>
                <div class="meta-item lang">🟣 {lang}</div>
                <div class="meta-item forks">🍴 {forks:,}</div>
            </div>
        </div>
"""
    
    html += f"""
        <div class="footer">
            <p>每日自动更新 · 由 GitHub Actions 生成</p>
            <p style="margin-top: 10px; font-size: 0.85em;">Generated at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
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
    <title>GitHub Trending - 历史记录</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
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
            padding: 10px 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            color: #94a3b8;
            text-decoration: none;
            font-size: 0.9em;
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
            padding: 16px 20px;
            border-bottom: 1px solid rgba(255,255,255,0.06);
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background 0.2s;
        }
        .date-item:last-child {
            border-bottom: none;
        }
        .date-item:hover {
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
        }
        .date-item a {
            color: #60a5fa;
            text-decoration: none;
            font-size: 1.1em;
        }
        .date-item a:hover {
            text-decoration: underline;
        }
        .arrow {
            color: #64748b;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📚 历史记录</h1>
            <p style="color: #94a3b8;">查看往期 GitHub Trending 报告</p>
        </header>
        
        <div class="nav">
            <a href="index.html">今日</a>
            <a href="history.html" class="active">历史</a>
        </div>
        
        <div class="date-list" id="dateList">
            <div class="date-item">
                <a href="latest.html">最新报告</a>
                <span class="arrow">→</span>
            </div>
        </div>
    </div>
    
    <script>
        // Dynamically populate from available files
        fetch('data/latest.json')
            .then(r => r.json())
            .then(data => {
                const list = document.getElementById('dateList');
                const date = data.date;
                if (date) {
                    const item = document.createElement('div');
                    item.className = 'date-item';
                    item.innerHTML = `<a href="archive/${date}.html">${date}</a><span class="arrow">→</span>`;
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
    
    # Generate HTML reports
    html = generate_html(repos, date_str)
    
    # Save as index.html (today's report)
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
    
    # Copy data to docs for web access
    docs_data_dir = OUTPUT_DIR / "data"
    docs_data_dir.mkdir(exist_ok=True)
    
    # Symlink or copy latest.json
    import shutil
    shutil.copy(DATA_DIR / "latest.json", docs_data_dir / "latest.json")
    
    print("Done!")

if __name__ == "__main__":
    main()
