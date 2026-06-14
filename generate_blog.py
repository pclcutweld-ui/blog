import os
import random
import json
import requests  # 引入请求库，绕过 SDK 凭证限制

# 🔐 安全读取 GitHub Secrets 传进来的 Key
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    # 兜底测试 Key
    API_KEY = "AQ.Ab8RN6LQ5X39phfGPx5a16d4wDtfUqrPudlsdCgQ7VcTIEHOGQ"

def get_keywords_and_topic():
    """从本地 keywords.txt 读取关键词"""
    try:
        with open("keywords.txt", "r", encoding="utf-8") as f:
            keywords = [line.strip() for line in f if line.strip()]
        selected = random.sample(keywords, min(2, len(keywords)))
        return " and ".join(selected)
    except Exception:
        return "High-Power CNC Fiber Laser Cutting Technology for Heavy Steel Fabrication"

def generate_article_body(topic):
    """通过底层的 HTTP 请求直接和你的 Vertex API 通信，完美解决 401 报错"""
    print(f"🤖 正在通过云端安全网关调用 Gemini 2.5-Flash，主题：{topic}...")
    
    prompt = f"""You are a senior industrial technical writer for PCL Group (CNC Fiber Laser Cutting & Welding Automation Manufacturer).
    Write a comprehensive, professional, SEO-optimized B2B blog post in English about: "{topic}".
    
    Requirements:
    1. Length: Around 800-1000 words.
    2. Format: Return ONLY raw HTML elements suitable for insertion inside a body tag. Do NOT include <html>, <head>, or <body> wrappers.
    3. Typography: Must include proper <h3> subheadings, structural <p> paragraphs, <b>bold core concepts</b>.
    4. Must include a standard HTML <table> comparing technical specifications or performance metrics.
    5. Must include one <blockquote> highlighting a summary note for industrial procurement managers.
    6. Strictly AVOID wrapping the response in markdown code blocks like ```html. Return raw text with HTML tags directly.
    """
    
    # ⚡ 使用 Vertex AI 专属的公开 API 终点，直接携带 Key 访问，GitHub Actions 环境完美通行
    url = f"[https://us-central1-aiplatform.googleapis.com/v1/projects/329474420473/locations/us-central1/publishers/google/models/gemini-2.5-flash:generateContent?key=](https://us-central1-aiplatform.googleapis.com/v1/projects/329474420473/locations/us-central1/publishers/google/models/gemini-2.5-flash:generateContent?key=){API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        # 解析返回的 HTML 正文
        ai_text = data['candidates'][0]['content']['parts'][0]['text']
        
        # 兜底清洗可能存在的 Markdown 标签
        cleaned_text = ai_text.replace("```html", "").replace("```", "").strip()
        return cleaned_text
    except Exception as e:
        print(f"❌ 接口请求失败，详细响应日志: {response.text if 'response' in locals() else str(e)}")
        raise e

def build_static_page():
    topic = get_keywords_and_topic()
    title = f"Latest Breakthroughs in {topic}"
    html_content = generate_article_body(topic)
    
    # 🎨 工业数字化美化模板
    full_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | PCL Group Technical Insights</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.7; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #334155; }}
        header {{ background: #0f172a; padding: 20px; color: #fff; margin-bottom: 30px; font-weight: bold; border-radius: 4px; }}
        header a {{ color: #0070f3; text-decoration: none; margin-right: 10px; }}
        h1 {{ font-size: 28px; color: #0f172a; font-weight: 800; margin-bottom: 25px; line-height: 1.3; }}
        h3 {{ font-size: 20px; color: #0f172a; margin-top: 35px; margin-bottom: 15px; font-weight: 700; }}
        p {{ margin-bottom: 20px; text-align: justify; }}
        table {{ width: 100%; border-collapse: collapse; margin: 25px 0; }}
        th {{ background-color: #f8f9fa; border-bottom: 2px solid #e9ecef; padding: 12px; text-align: left; }}
        td {{ padding: 12px; border-bottom: 1px solid #eee; }}
        blockquote {{ background: #f8f9fa; border-left: 5px solid #0070f3; margin: 25px 0; padding: 15px 20px; border-radius: 4px; font-style: italic; }}
        .back-link {{ display: inline-block; margin-top: 40px; color: #0070f3; text-decoration: none; font-weight: 600; }}
    </style>
</head>
<body>
    <header><a href="/">PCL GROUP</a> // Global Industrial Resource Base</header>
    <h1>{title}</h1>
    <div class="article-body">
        {html_content}
    </div>
    <a class="back-link" href="/">← Back to Knowledge Base</a>
</body>
</html>"""

    output_filename = "index.html"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(full_template)
    
    print(f"🎉 自动化出稿完毕！已成功生成静态网页文件: {output_filename}")

if __name__ == "__main__":
    build_static_page()
