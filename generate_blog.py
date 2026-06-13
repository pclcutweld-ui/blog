import os
import json
import urllib.request

def run():
    # 1. 检查并读取数据池
    if not os.path.exists("keywords.txt"):
        with open("keywords.txt", "w", encoding="utf-8") as f:
            f.write("12kW H-Beam 3D laser cutting machine price\n")
            
    if not os.path.exists("backlinks.txt"):
        with open("backlinks.txt", "w", encoding="utf-8") as f:
            f.write("https://pclgroupcncmachine.com/structural-steel-laser-cutting/\nhttps://pclgroupcncmachine.com/\n")
            
    if not os.path.exists("images.txt"):
        with open("images.txt", "w", encoding="utf-8") as f:
            f.write("https://pclgroupcncmachine.com/wp-content/uploads/2024/12/tcp-h-beam-cutting-machine-scaled.jpg\n")

    # 轮转关键词
    with open("keywords.txt", "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]
    if not keywords:
        print("No keywords found.")
        return
    keyword = keywords[0]
    with open("keywords.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(keywords[1:] + [keyword]) + "\n")

    # 轮转链接
    with open("backlinks.txt", "r", encoding="utf-8") as f:
        links = [line.strip() for line in f if line.strip()]
    link = links[0] if links else "https://pclgroupcncmachine.com/"
    if links:
        with open("backlinks.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(links[1:] + [link]) + "\n")

    # 随机图片
    with open("images.txt", "r", encoding="utf-8") as f:
        imgs = [line.strip() for line in f if line.strip()]
    img = imgs[0] if imgs else ""

    # 2. 获取 API KEY
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY secret is missing!")
        return

    # 3. 组装 Prompt
    prompt = f"""You are an elite B2B machinery sales director and hands-on welding engineer. Write a highly professional, technically precise industrial whitepaper for the keyword "{keyword}".

[CRITICAL - REMOVE ALL AI FLAVOR]:
- Do NOT use typical AI transition words like "In conclusion", "Crucial role", "Furthermore", "In summary", "Moreover", "Dive deep", "Testament".
- Use a confident, direct, and slightly blunt tone, common among industrial manufacturing experts.
- Speak strictly in terms of business ROI, steel fabricator pain points, mechanical tolerances, and factory output metrics.

[REQUIRED STRUCTURE]:
1. Technical Evaluation (Use realistic numbers, structural tolerances, H-beam dimensions like 300x300mm or HEA/HEB standards).
2. Machine Specification & Advantages (Break down real industrial components: cutting heads, heavy-duty chucks, rack and pinion systems).
3. Exact Internal Hyperlink Implementation (Link Library): You MUST seamlessly embed the exact string below as an organic anchor text hyperlink in the middle of a paragraph. Do not create an isolated link. 
   Anchor text MUST be a natural phrasing related to structural steel processing or automation.
   Link target: "{link}"
4. Image Placement: Embed this exact image HTML element inside the body text organically to show the real machine layout:
   <img src="{img}" alt="{keyword}" style="width:100%;max-width:800px;border-radius:8px;margin:20px 0;box-shadow:0 4px 6px rgba(0,0,0,0.1);">
5. Real-world FAQ Section: Provide 3 hard-core, realistic technical Q&As that global steel buyers ask during commercial procurement.
6. Call to Action: Add contact methods at the bottom: WhatsApp: 8618660174681, email: pclmachinery@outlook.com.

[OUTPUT FORMAT]:
Return the entire response as a single, valid, self-contained HTML file (including <html>, <head> with a catchy <title>, <style> for a premium clean layout, and <body>). 
At the very bottom of the HTML document, just before the closing </body> tag, you MUST inject a perfectly structured <script type="application/ld+json"> containing a dual JSON-LD Schema that wraps BOTH Article and FAQPage into a single graph.
Output ONLY the raw HTML code. Do NOT enclose the response in markdown blocks like ```html ... 
```."""

    # 4. 发起 HTTP 请求
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    req = urllib.request.Request(
        url, 
        data=json.dumps(payload).encode("utf-8"), 
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            article_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
            
            # 清理 Markdown 包裹
            if article_text.startswith("```html"):
                article_text = article_text[7:]
            elif article_text.startswith("
```"):
                article_text = article_text[3:]
            if article_text.endswith("```"):
                article_text = article_text[:-3]
            article_text = article_text.strip()

            # 5. 保存并导出
            os.makedirs("posts", exist_ok=True)
            clean_title = keyword.replace(" ", "-")
            file_path = f"posts/{clean_title}.html"
            
            with open(file_path, "w", encoding="utf-8") as out_f:
                out_f.write(article_text)
            print(f"Successfully generated: {file_path}")

            # 写入边缘重定向规则
            with open("_redirects", "w", encoding="utf-8") as red_f:
                red_f.write("/posts/:title /posts/:title.html 200\n")

    except Exception as e:
        print(f"Failed to execute API call: {e}")
        exit(1)

if __name__ == "__main__":
    run()
