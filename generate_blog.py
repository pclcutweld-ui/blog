import os
import time
from google import genai

# 1. 初始化你测试成功的 Vertex AI 模式客户端
client = genai.Client(
    vertexai=True,
    api_key="AQ.Ab8RN6LQ5X39phfGPx5a16d4wDtfUqrPudlsdCgQ7VcTIEHOGQ"
)

def generate_article_with_gemini(topic):
    print(f"🤖 正在调用 Gemini 2.5 撰写主题: {topic}...")
    
    prompt = f"Write a professional SEO-optimized B2B technical blog post about: '{topic}'. Use HTML tags for structure (h3, p, table, blockquote). Do not wrap in ```html block."
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

def save_and_push_to_github(slug, title, content):
    # 2. 模拟根据你的项目结构生成 HTML 文件
    # 假设你的静态博客文章存在 dist/ 或者是项目根目录下
    filename = f"blog-{slug}.html" 
    
    # 组装你的完整主页/文章模板（这里根据你原有的前端样式微调）
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>{title}</title></head>
    <body>
        <h1>{title}</h1>
        <div>{content}</div>
    </body>
    </html>
    """
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"💾 本地文件 {filename} 创建成功！")

    # 3. ⚡ 核心自动化：用 Python 自动提交到 GitHub
    print("🚀 正在将新文章推送到 GitHub 仓库...")
    os.system("git add .")
    os.system(f'git commit -m "Auto-generated blog: {title}"')
    os.system("git push origin main")
    print("🎉 GitHub 已经接收到更新！Cloudflare Pages 将在 1 分钟内自动完成部署。")

if __name__ == "__main__":
    # 💡 以后在本地执行这行脚本，输入任何你想写的工业主题
    topic_input = "Advanced CNC Fiber Laser Tube Cutting Technologies"
    slug_input = "laser-tube-cutting"
    
    # 运行流
    article_content = generate_article_with_gemini(topic_input)
    save_and_push_to_github(slug_input, f"Latest Insights on {topic_input}", article_content)
