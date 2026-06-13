import os
import json
import time
import re
import requests

def run():
    # 1. 确保数据池文件和基础目录结构完备
    if not os.path.exists("keywords.txt"):
        with open("keywords.txt", "w", encoding="utf-8") as f:
            f.write("12kW H-Beam 3D laser cutting machine price\n")
            
    if not os.path.exists("backlinks.txt"):
        with open("backlinks.txt", "w", encoding="utf-8") as f:
            f.write("https://pclgroupcncmachine.com/structural-steel-laser-cutting/\nhttps://pclgroupcncmachine.com/\n")
            
    if not os.path.exists("images.txt"):
        with open("images.txt", "w", encoding="utf-8") as f:
            f.write("https://pclgroupcncmachine.com/wp-content/uploads/2024/12/tcp-h-beam-cutting-machine-scaled.jpg\n")

    # 精准轮转提取当前行对应的关键词
    with open("keywords.txt", "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]
    if not keywords:
        print("Error: No keywords in keywords.txt")
        return
    keyword = keywords[0]
    remaining_keywords = keywords[1:]

    # 精准轮转提取当前行对应的超链接
    with open("backlinks.txt", "r", encoding="utf-8") as f:
        links = [line.strip() for line in f if line.strip()]
    if not links:
        links = ["https://pclgroupcncmachine.com/"]
    link = links[0]
    remaining_links = links[1:]

    # 提取大图
    with open("images.txt", "r", encoding="utf-8") as f:
        imgs = [line.strip() for line in f if line.strip()]
    img = imgs[0] if imgs else ""

    # 安全提取并严格清洗 API 密钥（防止用户误粘贴引号、空格、换行或反斜杠）
    raw_api_key = os.environ.get("GEMINI_API_KEY")
    if not raw_api_key:
        print("Error: GEMINI_API_KEY environment variable is missing!")
        return
        
    api_key = raw_api_key.strip().strip("'").strip('"').replace("\\", "")
    
    # 打印安全脱敏后的密钥信息，方便在日志中比对排查
    masked_key = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "INVALID_OR_EMPTY"
    print(f"Loaded API Key: {masked_key} (Cleaned Length: {len(api_key)})")

    # 2. 构造干净的高级 SEO 营销提示词（严格清洗，去除所有 AI 味）
    prompt_lines = [
        f"You are an elite B2B machinery sales director and hands-on welding engineer. Write a highly professional, technically precise industrial whitepaper for the keyword \"{keyword}\".",
        "",
        "[CRITICAL - REMOVE ALL AI FLAVOR]:",
        "- Do NOT use typical AI transition words like \"In conclusion\", \"Crucial role\", \"Furthermore\", \"In summary\", \"Moreover\", \"Dive deep\", \"Testament\".",
        "- Use a confident, direct, and slightly blunt tone, common among factory and industrial manufacturing experts.",
        "- Speak strictly in terms of business ROI, steel fabricator pain points, mechanical tolerances, and factory output metrics.",
        "",
        "[REQUIRED STRUCTURE]:",
        "1. Technical Evaluation (Use realistic numbers, structural tolerances, H-beam dimensions like 300x300mm or HEA/HEB standards).",
        "2. Machine Specification & Advantages (Break down real industrial components: cutting heads, heavy-duty chucks, rack and pinion systems).",
        f"3. Exact Internal Hyperlink Implementation (Link Library): You MUST seamlessly embed the exact string \"{link}\" as an organic anchor text hyperlink in the middle of a paragraph. Do not create an isolated link. The anchor text MUST be a natural phrasing related to structural steel processing or automation.",
        f"4. Image Placement: Embed this exact image HTML element inside the body text organically to show the real machine layout: <img src=\"{img}\" alt=\"{keyword}\" style=\"width:100%;max-width:800px;border-radius:8px;margin:20px 0;box-shadow:0 4px 6px rgba(0,0,0,0.1);\">",
        "5. Real-world FAQ Section: Provide 3 hard-core, realistic technical Q&As that global steel buyers ask during commercial procurement.",
        "6. Call to Action: Add contact methods at the bottom: WhatsApp: 8618660174681, email: pclmachinery@outlook.com.",
        "",
        "[OUTPUT FORMAT]:",
        "Return the entire response as a single, valid, self-contained HTML file (including <html>, <head> with a catchy <title>, <style> for a premium clean layout, and <body>).",
        "At the very bottom of the HTML document, just before the closing </body> tag, you MUST inject a perfectly structured <script type=\"application/ld+json\"> containing a dual JSON-LD Schema that wraps BOTH Article and FAQPage into a single graph.",
        "Output ONLY the raw HTML code. Do NOT enclose the response in markdown blocks like ```html ... ```."
    ]
    full_prompt = "\n".join(prompt_lines)
    payload = {"contents": [{"parts": [{"text": full_prompt}]}]}

    # 3. 智能多模型与多端点交叉路由链 (移除受限的未发布预览版，优先采用稳定和广泛授权的模型)
    models_to_try = [
        {"name": "gemini-2.0-flash", "api_version": "v1"},
        {"name": "gemini-2.0-flash", "api_version": "v1beta"},
        {"name": "gemini-1.5-flash", "api_version": "v1"},
        {"name": "gemini-1.5-flash", "api_version": "v1beta"},
        {"name": "gemini-1.5-pro", "api_version": "v1"},
        {"name": "gemini-1.5-pro", "api_version": "v1beta"}
    ]
    
    article_text = None
    successful_model = None
    successful_version = None
    
    # 遍历尝试可用模型与端点组合
    for model_info in models_to_try:
        model_name = model_info["name"]
        api_version = model_info["api_version"]
        
        if article_text:
            break
            
        print(f"\n🔄 Trying Model: {model_name} ({api_version} endpoint)...")
        url = f"https://generativelanguage.googleapis.com/{api_version}/models/{model_name}:generateContent?key={api_key}"
        
        # 每个端点组合最多重试 3 次，防止遭遇高频拥堵限制
        max_retries = 3
        base_delay = 10
        
        for attempt in range(max_retries):
            try:
                print(f"  Sending request (Attempt {attempt + 1}/{max_retries}) for keyword: {keyword}...")
                response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
                
                # 处理 429 频率限制异常
                if response.status_code == 429:
                    sleep_time = base_delay * (2 ** attempt)
                    print(f"  ⚠️ Hit Rate Limit (429) on {model_name}. Waiting {sleep_time}s...")
                    time.sleep(sleep_time)
                    continue
                
                # 处理 400, 403, 404 等模型无权限或不可用异常，直接切换到下一个端点/模型
                if response.status_code in [400, 403, 404]:
                    print(f"  ❌ Model {model_name} ({api_version}) returned status {response.status_code} (Unauthorized, unsupported or deprecated). Switching to next option...")
                    break
                    
                response.raise_for_status()
                res_data = response.json()
                raw_html = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                
                # 安全剥离 Markdown HTML 标记
                raw_html = re.sub(r'^```html\s*', '', raw_html, flags=re.IGNORECASE)
                raw_html = re.sub(r'^```[a-zA-Z]*\s*', '', raw_html)
                raw_html = re.sub(r'\s*```$', '', raw_html)
                raw_html = raw_html.strip()
                
                # 质量拦截把关
                if len(raw_html) > 500 and "html" in raw_html.lower() and raw_html.lower() != "null":
                    article_text = raw_html
                    successful_model = model_name
                    successful_version = api_version
                    print(f"  🎉 Successfully generated via {model_name} ({api_version})!")
                    break
                else:
                    print("  ⚠️ Suspicious short/empty text returned. Retrying inside current configuration...")
                    time.sleep(5)
                    
            except Exception as e:
                print(f"  ⚠️ Error during {model_name} ({api_version}) call: {e}")
                time.sleep(5)

    # 4. 成功放行并同步生成重定向路由
    if article_text:
        # 更新队列序列
        with open("keywords.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(remaining_keywords + [keyword]) + "\n")
        with open("backlinks.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(remaining_links + [link]) + "\n")

        # 生成合规文件名
        os.makedirs("posts", exist_ok=True)
        clean_title = keyword.replace(" ", "-")
        clean_title = re.sub(r'[\\/*?:"<>|]', '', clean_title)
        file_path = f"posts/{clean_title}.html"
        
        with open(file_path, "w", encoding="utf-8") as out_f:
            out_f.write(article_text)
        print(f"\n🎉 Success! Real SEO article written into: {file_path} (Generated by {successful_model} via {successful_version})")

        # 同步生成并修复 _redirects 边缘伪静态配置文件
        with open("_redirects", "w", encoding="utf-8") as red_f:
            red_f.write("/posts/:title /posts/:title.html 200\n")
        print("📁 _redirects rule synced successfully.")
    else:
        print("\n❌ Fatal Error: All models and endpoint combinations in the fallback chain failed to generate valid content.")
        exit(1)

if __name__ == "__main__":
    run()
