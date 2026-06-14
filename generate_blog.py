import os
import random
from google import genai

# 🔐 安全核心：从 GitHub Secrets 传递的环境变量中读取 API Key
# 这样代码里就不会包含任何敏感明文，绝对安全！
API_KEY = os.environ.get("GEMINI_API_KEY")

# 如果在本地测试时没有配置环境变量，可作为本地测试的兜底（GitHub 运行时会自动走上面那行）
if not API_KEY:
    API_KEY = "AQ.Ab8RN6LQ5X39phfGPx5a16d4wDtfUqrPudlsdCgQ7VcTIEHOGQ"

client = genai.Client(
    vertexai=True,   # 核心：保持你测试成功的重要参数
    api_key=API_KEY
)

def get_keywords_and_topic():
    """从本地 keywords.txt 读取关键词并组合一个工业硬核主题"""
    try:
        with open("keywords.txt", "r", encoding="utf-8") as f:
            keywords = [line.strip() for line in f if line.strip()]
        selected = random.sample(keywords, min(2, len(keywords)))
        return " and ".join(selected)
    except Exception:
        return "High-Power CNC Fiber Laser Cutting Technology for Heavy Steel Fabrication"

def generate_article_body(topic):
    """调用最新的 Gemini 2.5 系列模型撰写长文"""
    print(f"🤖 正在调用 Gemini 2.5-Flash 撰写深度技术文章，主题：{topic}...")
    
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
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    cleaned_text = response.text.replace("```html", "").replace("```", "").strip()
    return cleaned_text

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
