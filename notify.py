#!/usr/bin/env python3
"""
Notification sender for GitHub Daily Trending
Supports Feishu, DingTalk, and WeCom webhooks
"""

import os
import json
import requests
from datetime import datetime

def send_feishu(webhook_url, title, content, page_url):
    """Send notification to Feishu"""
    msg = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": title,
                    "content": [
                        [{"tag": "text", "text": content}],
                        [{"tag": "a", "text": "🔗 点击查看完整报告", "href": page_url}]
                    ]
                }
            }
        }
    }
    
    try:
        resp = requests.post(webhook_url, json=msg, timeout=10)
        resp.raise_for_status()
        print("✅ Feishu notification sent")
        return True
    except Exception as e:
        print(f"❌ Feishu failed: {e}")
        return False

def send_dingtalk(webhook_url, title, content, page_url):
    """Send notification to DingTalk"""
    msg = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": f"### {title}\n\n{content}\n\n[🔗 点击查看完整报告]({page_url})"
        }
    }
    
    try:
        resp = requests.post(webhook_url, json=msg, timeout=10)
        resp.raise_for_status()
        print("✅ DingTalk notification sent")
        return True
    except Exception as e:
        print(f"❌ DingTalk failed: {e}")
        return False

def send_wecom(webhook_url, title, content, page_url):
    """Send notification to WeCom"""
    msg = {
        "msgtype": "news",
        "news": {
            "articles": [
                {
                    "title": title,
                    "description": content,
                    "url": page_url,
                    "picurl": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
                }
            ]
        }
    }
    
    try:
        resp = requests.post(webhook_url, json=msg, timeout=10)
        resp.raise_for_status()
        print("✅ WeCom notification sent")
        return True
    except Exception as e:
        print(f"❌ WeCom failed: {e}")
        return False

def main():
    # Load data
    data_file = "data/latest.json"
    if not os.path.exists(data_file):
        print(f"Data file not found: {data_file}")
        return
    
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    repos = data.get("repos", [])[:5]  # Top 5 for notification
    date_str = data.get("date", datetime.now().strftime("%Y-%m-%d"))
    
    # Build page URL
    repo = os.environ.get("GITHUB_REPOSITORY", "user/repo")
    page_url = f"https://{repo.split('/')[0]}.github.io/github-daily-trending/"
    
    # Build notification content
    title = f"🔥 GitHub Trending {date_str}"
    content_lines = ["今日热门 Top 5:\n"]
    
    for i, repo_item in enumerate(repos, 1):
        name = repo_item.get("full_name", "Unknown")
        desc = repo_item.get("description") or "暂无描述"
        stars = repo_item.get("stargazers_count", 0)
        content_lines.append(f"{i}. {name} ⭐{stars}")
        if len(desc) > 50:
            desc = desc[:50] + "..."
        content_lines.append(f"   {desc}\n")
    
    content = "\n".join(content_lines)
    
    print(f"Title: {title}")
    print(f"Content preview:\n{content[:200]}...")
    
    # Send notifications
    sent = False
    
    if os.environ.get("FEISHU_WEBHOOK"):
        send_feishu(os.environ["FEISHU_WEBHOOK"], title, content, page_url)
        sent = True
    
    if os.environ.get("DINGTALK_WEBHOOK"):
        send_dingtalk(os.environ["DINGTALK_WEBHOOK"], title, content, page_url)
        sent = True
    
    if os.environ.get("WECOM_WEBHOOK"):
        send_wecom(os.environ["WECOM_WEBHOOK"], title, content, page_url)
        sent = True
    
    if not sent:
        print("⚠️ No webhook configured, skipping notifications")
        print(f"Report URL: {page_url}")

if __name__ == "__main__":
    main()
