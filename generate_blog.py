# -*- coding: utf-8 -*-
import os
import json
import time
import re
import requests
from datetime import datetime

def run():
    # 1. 确保基础数据池文件和目录结构完备
    if not os.path.exists("keywords.txt"):
        with open("keywords.txt", "w", encoding="utf-8") as f:
            f.write("12kW H-Beam 3D laser cutting machine price\n")
            
    if not os.path.exists("backlinks.txt"):
        with open("backlinks.txt", "w", encoding="utf-8") as f:
            f.write("https://pclgroupcncmachine.com/structural-steel-laser-cutting/\nhttps://pclgroupcncmachine.com/\n")
            
    if not os.path.exists("images.txt"):
        with open("images.txt", "w", encoding="utf-8") as f:
            f.write("https://pclgroupcncmachine.com/wp-content/uploads/2024/12/tcp-h-beam-cutting-machine-scaled.jpg\n")

    # 轮转提取当前关键词
    with open("keywords.txt", "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]
    if not keywords:
        print("Error: keywords.txt 为空！")
        return
    keyword = keywords[0]
    remaining_keywords = keywords[1:]

    # 轮转提取当前锚文本外链
    with open("backlinks.txt", "r", encoding="utf-8") as f:
        links = [line.strip() for line in f if line.strip()]
    if not links:
        links = ["https://pclgroupcncmachine.com/"]
    link = links[0]
    remaining_links = links[1:]

    # 提取机床大图
    with open("images.txt", "r", encoding="utf-8") as f:
        imgs = [line.strip() for line in f if line.strip()]
    img = imgs[0] if imgs else ""

    # 安全读取并严格清洗 API Key
    raw_api_key = os.environ.get("GEMINI_API_KEY")
    if not raw_api_key:
        print("Error: 环境变量 GEMINI_API_KEY 缺失，请检查 GitHub Secrets 配置！")
        return
    api_key = raw_api_key.strip().strip("'").strip('"').replace("\\", "")
    
    masked_key = api_key[:6] + "..." + api_key[-6:] if len(api_key) > 12 else "INVALID"
    print(f"🔑 API Key 成功加载: {masked_key} (长度: {len(api_key)})")

    # 2. 构造极其严苛、去 AI 腔调的 B2B 工业级 HTML 页面 Prompt
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
        f"3. Exact Internal Hyperlink Implementation (Link Library): You MUST seamlessly embed the exact string \"{link}\" as an organic anchor text hyperlink in the middle of a paragraph. Do not create an isolated link.",
        f"4. Image Placement: Embed this exact image HTML element inside the body text organically: <img src=\"{img}\" alt=\"{keyword}\" style=\"width:100%;max-width:800px;border-radius:8px;margin:20px 0;\">",
        "5. Real-world FAQ Section: Provide 3 hard-core, realistic technical Q&As that global steel buyers ask during commercial procurement.",
        "6. Call to Action: Add contact methods at the bottom: WhatsApp: 8618660174681, email: pclmachinery@outlook.com.",
        "",
        "[OUTPUT FORMAT]:",
        "Return the entire response as a single, valid, self-contained HTML file.",
        "Output ONLY the raw HTML code. Do NOT enclose the response in markdown blocks like ```html ... ```."
    ]
    full_prompt = "\n".join(prompt_lines)
    payload = {"contents": [{"parts": [{"text": full_prompt}]}]}

    # 3. 指定兼容新老密钥的最稳固网关及备用链路
    models_to_try = [
        {"name": "gemini-2.5-flash", "api_version": "v1"},
        {"name": "gemini-1.5-flash", "api_version": "v1"},
        {"name": "gemini-3-flash-preview", "api_version": "v1beta"}
    ]
    
    article_text = None
    
    for model_info in models_to_try:
        model_name = model_info["name"]
        api_version = model_info["api_version"]
        
        if article_text:
            break
            
        print(f"\n🔄 正在请求模型: {model_name} (接口版本: {api_version})...")
        
        # 混合测试两种传参模式以应付谷歌网关的间歇性策略变动
        # 尝试方案 A: Headers 头部鉴权
        url_a = f"https://generativelanguage.googleapis.com/{api_version}/models/{model_name}:generateContent"
        headers_a = {"Content-Type": "application/json", "x-goog-api-key": api_key}
        
        try:
            print(f"  [方案A] 发送请求，关键词: {keyword}...")
            response = requests.post(url_a, json=payload, headers=headers_a, timeout=60)
            if response.status_code == 200:
                res_data = response.json()
                raw_html = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                raw_html = re.sub(r'^```html\s*', '', raw_html, flags=re.IGNORECASE)
                raw_html = re.sub(r'^```[a-zA-Z]*\s*', '', raw_html)
                raw_html = re.sub(r'\s*```$', '', raw_html).strip()
                if len(raw_html) > 500:
                    article_text = raw_html
                    print(f"  🎉 方案A成功打通！")
                    break
            else:
                print(f"  [方案A] 状态码: {response.status_code}")
        except Exception as e:
            print(f"  [方案A] 失败: {e}")
            
        # 尝试方案 B: URL 参数鉴权备份
        url_b = f"[https://generativelanguage.googleapis.com/](https://generativelanguage.googleapis.com/){api_version}/models/{model_name}:generateContent?key={api_key}"
        try:
            print(f"  [方案B] 启动备份路径尝试...")
            response = requests.post(url_b, json=payload, headers={"Content-Type": "application/json"}, timeout=45)
            if response.status_code == 200:
                res_data = response.json()
                raw_html = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                raw_html = re.sub(r'^```html\s*', '', raw_html, flags=re.IGNORECASE)
                raw_html = re.sub(r'^```[a-zA-Z]*\s*', '', raw_html)
                raw_html = re.sub(r'\s*```$', '', raw_html).strip()
                if len(raw_html) > 500:
                    article_text = raw_html
                    print(f"  🎉 方案B备份路径打通！")
                    break
            else:
                print(f"  [方案B] 状态码: {response.status_code}")
        except Exception as e:
            print(f"  [方案B] 失败: {e}")

    # 4. 全自动编译并同步刷新整个博客门户首页
    if article_text:
        with open("keywords.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(remaining_keywords + [keyword]) + "\n")
        with open("backlinks.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(remaining_links + [link]) + "\n")

        os.makedirs("posts", exist_ok=True)
        clean_title = keyword.replace(" ", "-")
        clean_title = re.sub(r'[\\/*?:"<>|]', '', clean_title)
        file_path = f"posts/{clean_title}.html"
        
        with open(file_path, "w", encoding="utf-8") as out_f:
            out_f.write(article_text)
        print(f"🎉 物理文章已成功存入: {file_path}")

        print("\n🔨 正在无损重构博客首页 (index.html)...")
        posts_list = []
        for file in os.listdir("posts"):
            if file.endswith(".html"):
                path_to_file = os.path.join("posts", file)
                title_search = "CNC Laser Machinery Blog"
                with open(path_to_file, "r", encoding="utf-8") as pf:
                    content = pf.read()
                    match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                    if match:
                        title_search = match.group(1)
                
                mtime = os.path.getmtime(path_to_file)
                date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
                url_slug = file.replace(".html", "")
                
                posts_list.append({
                    "title": title_search,
                    "date": date_str,
                    "url": f"/posts/{url_slug}",
                    "timestamp": mtime
                })
        
        posts_list.sort(key=lambda x: x["timestamp"], reverse=True)

        blog_cards_html = ""
        card_template = """
            <div class="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300 border border-gray-100 flex flex-col justify-between">
                <div class="p-6">
                    <span class="text-xs font-semibold text-blue-600 uppercase tracking-wider">__POST_DATE__</span>
                    <h2 class="mt-2 text-xl font-bold text-gray-900 line-clamp-2 hover:text-blue-600 transition-colors">
                        <a href="__POST_URL__">__POST_TITLE__</a>
                    </h2>
                    <p class="mt-3 text-sm text-gray-500 line-clamp-3">
                        Discover elite B2B technical specs, ROI analysis, mechanical tolerances, and factory output metrics regarding this structural steel processing technology.
                    </p>
                </div>
                <div class="p-6 pt-0">
                    <a href="__POST_URL__" class="inline-flex items-center text-sm font-semibold text-blue-600 hover:text-blue-700">
                        Read Full Whitepaper
                        <svg class="ml-1 w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>
                    </a>
                </div>
            </div>
        """
        for post in posts_list:
            single_card = card_template
            single_card = single_card.replace("__POST_DATE__", str(post['date']))
            single_card = single_card.replace("__POST_URL__", str(post['url']))
            single_card = single_card.replace("__POST_TITLE__", str(post['title']))
            blog_cards_html += single_card

        index_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PCL CNC Laser Machinery & Technology Blog</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 text-gray-800 min-h-screen flex flex-col">
    <nav class="bg-white border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16 items-center">
                <div class="flex-shrink-0">
                    <a href="/" class="text-xl font-extrabold text-blue-600 tracking-wider">PCL MACHINERY</a>
                </div>
                <div class="flex space-x-4">
                    <a href="/" class="text-gray-900 px-3 py-2 rounded-md text-sm font-medium border-b-2 border-blue-600">Blog Portal</a>
                    <a href="https://pclgroupcncmachine.com/" target="_blank" class="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium">Official Website</a>
                </div>
            </div>
        </div>
    </nav>
    <header class="bg-gradient-to-r from-blue-700 to-indigo-800 py-16 text-center text-white">
        <div class="max-w-4xl mx-auto px-4">
            <h1 class="text-4xl sm:text-5xl font-black tracking-tight mb-4">Structural Steel Laser Technology</h1>
            <p class="text-lg sm:text-xl text-blue-100 font-light max-w-2xl mx-auto">
                Hardcore engineering whitepapers, procurement Q&As, and ROI analysis written directly by machinery experts.
            </p>
        </div>
    </header>
    <main class="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            __CARDS_PLACEHOLDER__
        </div>
    </main>
    <footer class="bg-white border-t border-gray-200 py-8 text-center text-sm text-gray-500 mt-auto">
        <div class="max-w-7xl mx-auto px-4">
            <p>© __YEAR__ PCL CNC Group. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>"""
        
        index_template = index_template.replace("__CARDS_PLACEHOLDER__", blog_cards_html)
        index_template = index_template.replace("__YEAR__", str(datetime.now().year))

        with open("index.html", "w", encoding="utf-8") as index_f:
            index_f.write(index_template)
        print("🎉 博客门户首页编译成功！")

        with open("_redirects", "w", encoding="utf-8") as red_f:
            red_f.write("/posts/:title /posts/:title.html 200\n")
        print("📁 伪静态路由更新完毕。")
    else:
        print("\n❌ 严重错误: 所有方案及兼容路径均无法使用当前 API 密钥通过谷歌网关验证。")
        exit(1)

if __name__ == "__main__":
    run()
