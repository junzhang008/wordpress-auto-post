import requests
import random
import os
import string
from datetime import datetime
from requests.auth import HTTPBasicAuth
import jieba
import jieba.analyse
import time

# --- 1. 海量全学段全学科主题库 ---
TOPICS_BY_CATEGORY = {
    # 小学
    "一年级数学": ["10以内加减法混合运算", "认识图形的特征", "认识钟表与整时"],
    "五年级语文": ["景物描写技巧训练", "缩写句子的方法", "文言文《少年中国说》解析"],
    # 初中
    "初中物理": ["牛顿第二定律综合应用", "电路串并联识别方法", "透镜成像实验步骤"],
    "初中化学": ["金属活动性顺序实验", "酸碱中和反应原理", "实验室制取二氧化碳"],
    # 高中
    "高中数学": ["圆锥曲线离心率求解模板", "三角函数诱导公式全解析", "导数在切线方程中的应用"],
    "高中地理": ["地球公转的地理意义", "大气环流与气候带分布", "地质构造与地貌形成"],
    # 大学
    "大学数学": ["高等数学：泰勒中值定理应用", "线性代数：矩阵特征值求解", "概率论：贝叶斯公式深度推导"],
    "大学专业课": ["Python数据结构：平衡二叉树", "宏观经济学：IS-LM模型分析", "心理学：遗忘曲线规律应用"]
}

# --- 2. 基础配置 ---
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
WORDPRESS_URL = os.getenv('WORDPRESS_URL').rstrip('/')
WORDPRESS_USER = os.getenv('WORDPRESS_USER')
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD')

CATEGORY_MAP = {
    "一年级数学": 6, "初中物理": 776, "高中数学": 782, "大学数学": 790, "大学专业课": 792
    # 请根据您的后台 ID 继续补充
}

# --- 3. 核心功能函数 ---

def generate_random_slug(length=10):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

def get_or_create_tag_id(tag_name):
    try:
        auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
        res = requests.get(f"{WORDPRESS_URL}/wp-json/wp/v2/tags?search={tag_name}", auth=auth).json()
        if res and isinstance(res, list):
            for t in res:
                if t['name'] == tag_name: return t['id']
        new_tag = requests.post(f"{WORDPRESS_URL}/wp-json/wp/v2/tags", json={'name': tag_name, 'slug': tag_name}, auth=auth).json()
        return new_tag.get('id')
    except: return None

def upload_image_and_get_url(category, topic):
    """搜索并上传图片，直接返回可用于 HTML 的 URL"""
    try:
        query = f"education,{category[-2:]},{topic[:2]}"
        img_url = f"https://source.unsplash.com/featured/800x450/?{query}"
        img_data = requests.get(img_url, timeout=20).content
        auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
        res = requests.post(
            f"{WORDPRESS_URL}/wp-json/wp/v2/media",
            headers={'Content-Disposition': f'attachment; filename={generate_random_slug()}.jpg', 'Content-Type': 'image/jpeg'},
            data=img_data, auth=auth, timeout=30
        ).json()
        return res.get('id'), res.get('source_url')
    except: return None, None

def get_ai_content(topic, category):
    """AI内容生成，纯文本输出"""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {"Authorization": f"Bearer {ZHIPU_API_KEY}"}
    prompt = f"请以资深专家的身份撰写《{topic}》的教学指南。要求：使用HTML格式(h2,h3,p)，1200字以上，包含知识点拨、例题精讲。不要在文中写图片占位符。"
    data = {"model": "glm-4", "messages": [{"role": "user", "content": prompt}], "temperature": 0.8}
    res = requests.post(url, headers=headers, json=data, timeout=60).json()
    return res['choices'][0]['message']['content']

# --- 4. 发布主逻辑 ---

def post_to_wordpress(title, content, category):
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    cat_id = CATEGORY_MAP.get(category, 1)
    
    # 修复距离：注入 CSS 样式
    style_fix = '<style>.entry-content { margin-top: -20px !important; }</style>'
    
    # 获取并上传 2 张图片，分别放在文章开头和中间
    media_id1, url1 = upload_image_and_get_url(category, title)
    media_id2, url2 = upload_image_and_get_url(category, "study")
    
    final_content = style_fix
    if url1:
        final_content += f'<p style="text-align:center;"><img src="{url1}" alt="{title}" style="border-radius:8px;"/></p>'
    
    # 将内容切分，在中间插入第二张图
    parts = content.split('</h3>', 1)
    if len(parts) > 1 and url2:
        final_content += parts[0] + f'</h3><p style="text-align:center;"><img src="{url2}" alt="知识点解" style="border-radius:8px;"/></p>' + parts[1]
    else:
        final_content += content

    # 处理标签
    tag_ids = [get_or_create_tag_id(n) for n in [category[:2], "格物智库", "精华资源"]]

    post_data = {
        'title': title, 'content': final_content, 'status': 'publish',
        'categories': [cat_id], 'tags': tag_ids, 'slug': generate_random_slug(),
        'featured_media': media_id1 if media_id1 else 0,
        'meta': {
            'download_link': 'https://www.gogewu.com/download-center/', 
            'download_code': '8888'
        }
    }
    
    res = requests.post(f"{WORDPRESS_URL}/wp-json/wp/v2/posts", json=post_data, auth=auth)
    if res.status_code == 201:
        print(f"✅ 发布成功: {title}")
    else:
        print(f"❌ 错误: {res.text}")

def main():
    category = random.choice(list(TOPICS_BY_CATEGORY.keys()))
    topic = random.choice(TOPICS_BY_CATEGORY[category])
    content = get_ai_content(topic, category)
    if content:
        post_to_wordpress(topic, content, category)

if __name__ == "__main__":
    main()
