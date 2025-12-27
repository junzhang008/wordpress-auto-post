import requests
import random
import os
import string
import io
from requests.auth import HTTPBasicAuth

# --- 1. 您的全量分类 ID (严格保留) ---
CATEGORY_MAP = {
    "一年级数学": 6, "二年级数学": 7, "三年级数学": 8, "四年级数学": 9, 
    "五年级数学": 10, "六年级数学": 11, "一年级语文": 12, "二年级语文": 13, 
    "三年级语文": 14, "四年级语文": 15, "五年级语文": 16, "六年级语文": 17, 
    "一年级英语": 18, "二年级英语": 19, "三年级英语": 20, "四年级英语": 21, 
    "五年级英语": 22, "六年级英语": 23, "初中数学": 774, "初中语文": 773, 
    "初中英语": 775, "初中物理": 776, "初中化学": 777,
    "高中数学": 782, "高中语文": 781, "高中英语": 783, "高中物理": 784, "高中化学": 785,
    "大学数学": 790, "大学英语": 789, "大学专业课": 792
}

# --- 2. 补全海量主题库 (涵盖小、初、高、大) ---
TOPICS_BY_CATEGORY = {
    "一年级数学": ["10以内加减法混合运算", "认识图形特征", "凑十法与破十法"],
    "六年级数学": ["圆的周长与面积推导", "百分数应用题详解", "圆柱与圆锥体积比较"],
    "初中物理": ["串并联电路电压规律", "浮力产生的原因", "透镜成像规律实验"],
    "高中数学": ["圆锥曲线离心率求解模板", "三角函数诱导公式全解", "导数单调性研究"],
    "大学专业课": ["Python数据结构：平衡二叉树", "宏观经济IS-LM模型", "管理学SWOT分析法"]
}

# --- 3. 配置 (请确保使用应用密码) ---
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
WORDPRESS_URL = os.getenv('WORDPRESS_URL').rstrip('/')
WORDPRESS_USER = os.getenv('WORDPRESS_USER')
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD')

# --- 4. 辅助函数 ---

def get_detailed_ai_content(topic, category):
    """强制 AI 生成高质量教学长文，解决内容缺失问题"""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {"Authorization": f"Bearer {ZHIPU_API_KEY}", "Content-Type": "application/json"}
    
    # 身份识别逻辑
    level = "教授" if "大学" in category else ("特级教师" if "高中" in category else "资深教师")
    
    prompt = f"""
    请以{level}身份，撰写一篇关于《{topic}》的深度教学解析文章。
    要求：
    1. 使用 HTML 格式排版（h2, h3, p）。
    2. 必须包含：一、知识讲解（详细原理）；二、重点难点；三、经典例题解析；四、课后思考。
    3. 总字数不少于 1200 字。
    4. 禁止出现“正在生成中”或占位符，直接输出正文。
    """
    
    data = {
        "model": "glm-4",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8
    }
    try:
        res = requests.post(url, headers=headers, json=data, timeout=60).json()
        return res['choices'][0]['message']['content'].strip()
    except: return None

def upload_media_reliable(category):
    """安全上传图片流，确保媒体库不出现白块"""
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    try:
        img_url = f"https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800&q=80"
        res = requests.get(img_url, timeout=20)
        img_stream = io.BytesIO(res.content)
        filename = f"edu_{''.join(random.choices(string.ascii_lowercase, k=8))}.jpg"

        files = {'file': (filename, img_stream, 'image/jpeg')}
        res = requests.post(
            f"{WORDPRESS_URL}/wp-json/wp/v2/media",
            files=files, auth=auth,
            headers={'Content-Disposition': f'attachment; filename={filename}'},
            timeout=30
        ).json()
        return res.get('id')
    except: return None

# --- 5. 发布主逻辑 (回归第一份脚本风格) ---

def post_to_wordpress(title, content, category):
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    cat_id = CATEGORY_MAP.get(category, 1)
    
    # 获取图片 ID (仅作为特色图片)
    media_id = upload_media_reliable(category)
    
    # 解决标题重叠与间距的 CSS
    style_fix = """
    <style>
        .entry-title { line-height: 1.5 !important; margin-bottom: 30px !important; }
        .entry-content h2 { margin-top: 40px !important; margin-bottom: 20px !important; }
    </style>
    """
    
    # 文末下载中心 HTML
    download_html = f"""
    <div style="border: 2px dashed #1e73be; padding: 25px; background: #f0f8ff; border-radius: 12px; text-align: center; margin-top: 50px; clear: both;">
        <h3 style="color:#1e73be; margin-top:0;">📂 资源下载中心</h3>
        <p>本篇《{title}》相关配套讲义及练习资料已打包完成。</p>
        <p><strong>下载地址：</strong> <a href="https://www.gogewu.com/download-center/" target="_blank" style="color:#ff4500; font-weight:bold;">点击跳转至下载通道</a></p>
        <p><strong>提取码：</strong> <span style="background:#ffd700; padding:2px 8px; font-weight:bold; border-radius:4px;">8888</span></p>
    </div>
    """
    
    # 拼装内容：CSS样式 + AI正文 + 下载框
    final_content = style_fix + content + download_html

    post_data = {
        'title': title,
        'content': final_content,
        'status': 'publish',
        'categories': [cat_id],
        'featured_media': media_id if media_id else 0,
        'slug': ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    }
    
    res = requests.post(f"{WORDPRESS_URL}/wp-json/wp/v2/posts", json=post_data, auth=auth, timeout=30)
    
    if res.status_code == 201:
        print(f"✅ 发布成功: {title}")
    else:
        print(f"❌ 失败: {res.text}")

def main():
    category = random.choice(list(TOPICS_BY_CATEGORY.keys()))
    topic = random.choice(TOPICS_BY_CATEGORY[category])
    print(f"🚀 开始执行任务: [{category}] - {topic}")
    
    content = get_detailed_ai_content(topic, category)
    if content:
        post_to_wordpress(topic, content, category)

if __name__ == "__main__":
    main()
