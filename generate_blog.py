import os
import json
import urllib.request
import time
import re

def run():
    # 1. 确保基础文件池存在
    if not os.path.exists("keywords.txt"):
        with open("keywords.txt", "w", encoding="utf-8") as f:
            f.write("12kW H-Beam 3D laser cutting machine price\n")
            
    if not os.path.exists("backlinks.txt"):
        with open("backlinks.txt", "w", encoding="utf-8") as f:
            f.write("https://pclgroupcncmachine.com/structural-steel-laser-cutting/\nhttps://pclgroupcncmachine.com/\n")
            
    if not os.path.exists("images.txt"):
        with open("images.txt", "w", encoding="utf-8") as f:
            f.write("https://pclgroupcncmachine.com/wp-content/uploads/2024/12/tcp-h-beam-cutting-machine-scaled.jpg\n")

    # 精准安全提取并分离关键词
    with open("keywords.txt", "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]
    if not keywords:
        print("Error: No keywords in keywords.txt")
        return
    keyword = keywords[0]
    remaining_keywords = keywords[1:]  # 剥离出剩下的词

    # 精准安全提取并分离外链
    with open("backlinks.txt", "r", encoding="utf-8") as f:
        links = [line.strip() for line in f if line.strip()]
    if not links:
        links = ["https://pclgroupcncmachine.com/"]
    link = links[0]
    remaining_links = links[1:]  # 剥离出剩下的外链

    # 随机提取图片
    with open("images.txt", "r", encoding="utf-8") as f:
        imgs = [line.strip() for line in f if line.strip()]
    img = imgs[0] if imgs else ""

    # 获取系统密钥
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY variable is missing!")
        return

    # 2. 构造干净的纯文本 Prompt
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
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    # 3. 智能多轨抗压熔断循环
    max_retries = 5
    base_delay = 20  
    article_text = None
    
    for attempt in range(max_retries):
        try:
            print(f"Sending request to Gemini API (Attempt {attempt + 1}/{max_retries})...")
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
            
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                raw_html = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                
                # 清理首尾 Markdown 标记块
                if raw_html.startswith("```html"):
                    raw_html = raw_html[7:]
                elif raw_html.startswith("```"):
                    raw_html = raw_html[3:]
                if raw_html.endswith("```"):
                    raw_html = raw_html[:-3]
                raw_html = raw_html.strip()
                
                # 全方位地毯式安全熔断拦截
                if len(raw_html) > 800 and "html" in raw_html.lower() and raw_html.lower() != "null" and raw_html.strip() != "null":
                    article_text = raw_html
                    break
                else:
                    print("⚠️ Detect invalid empty/null/short response from API. Force retry...")
                    time.sleep(10)

        except urllib.error.HTTPError as e:
            if e.code == 429:
                sleep_time = base_delay * (2 ** attempt)
                print(f"Hit Rate Limit (429). Waiting {sleep_time}s...")
                time.sleep(sleep_time)
            else:
                print(f"HTTP Error {e.code}, retrying...")
                time.sleep(10)
        except Exception as e:
            print(f"Exception: {e}, retrying...")
            time.sleep(10)
            
    # 4. 终极验证放行
    if article_text:
        # 【修复完美轮转逻辑】成功拿到了文章，才把当前的词和外链推到队伍最后面
        with open("keywords.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(remaining_keywords + [keyword]) + "\n")
        with open("backlinks.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(remaining_links + [link]) + "\n")

        # 保存为静态文件
        os.makedirs("posts", exist_ok=True)
        # SEO 增强：清洗关键词中可能存在的特殊符号，防止产生非法 Linux 文件名
        clean_title = keyword.replace(" ", "-")
        clean_title = re.sub(r'[\\/*?:"<>|]', '', clean_title)
        file_path = f"posts/{clean_title}.html"
        
        with open(file_path, "w", encoding="utf-8") as out_f:
            out_f.write(article_text)
        print(f"🎉 Success! Real SEO article written into: {file_path}")
    else:
        print("❌ Fatal Error: API kept returning 'null' or empty texts after all retries. Blocked file push to protect site.")
        exit(1)

if __name__ == "__main__":
    run()
