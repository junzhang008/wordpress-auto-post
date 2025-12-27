import requests
import random
import os
import string
from datetime import datetime
from requests.auth import HTTPBasicAuth
import jieba
import jieba.analyse
import time
import re

# --- 1. 完整全学段主题库 ---
TOPICS_BY_CATEGORY = {
    "一年级数学": ["10以内加减法", "认识图形"], "六年级数学": ["圆的面积", "比例应用"],
    "初中数学": ["有理数运算", "一元一次方程", "几何证明题", "函数图像"],
    "初中物理": ["电路图绘制", "浮力计算", "透镜成像"],
    "高中数学": ["三角函数变换", "圆锥曲线模板", "导数的意义"],
    "高中物理": ["牛顿运动定律", "电磁感应", "动量守恒"],
    "大学数学": ["高等数学极限", "线性代数矩阵", "概率论正态分布"],
    "大学英语": ["四六级写作模板", "考研英语长难句", "学术论文表达"],
    "大学专业课": ["算法分析", "宏观调控原理", "认知行为疗法"]
}

# --- 2. 基础配置 ---
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
WORDPRESS_URL = os.getenv('WORDPRESS_URL').rstrip('/')
WORDPRESS_USER = os.getenv('WORDPRESS_USER')
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD') # 请使用应用密码
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY')

CATEGORY_MAP = {
    "一年级数学": 6, "六年级数学": 11,
    "初中数学": 774, "初中语文": 773, "初中英语": 775, "初中物理": 776, "初中化学": 777,
    "高中数学": 782, "高中语文": 781, "高中英语": 783, "高中物理": 784, "高中化学": 785,
    "大学数学": 790, "大学英语": 789, "大学专业课": 792
}

# --- 3. 核心功能函数 ---

def generate_random_slug(length=10):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

def get_or_create_tag(tag_name):
    try:
        auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
        res = requests.get(f"{WORDPRESS_URL}/wp-json/wp/v2/tags?search={tag_name}", auth=auth).json()
        if res: return res[0]['id']
        new_tag = requests.post(f"{WORDPRESS_URL}/wp-json/wp/v2/tags", json={'name': tag_name}, auth=auth).json()
        return new_tag.get('id')
    except: return None

def upload_image(image_url, title):
    """下载并上传图片到媒体库"""
    try:
        img_data = requests.get(image_url, timeout=15).content
        auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
        res = requests.post(
            f"{WORDPRESS_URL}/wp-json/wp/v2/media",
            headers={'Content-Disposition': f'attachment; filename={generate_random_slug()}.jpg', 'Content-Type': 'image/jpeg'},
            data=img_data, auth=auth, timeout=30
        ).json()
        return res.get('id'), res.get('source_url')
    except: return None, None

def get_zhipu_content(topic, category):
    """AI 内容生成 - 自动识别身份"""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {"Authorization": f"Bearer {ZHIPU_API_KEY}"}
    
    # 身份适配逻辑
    level = "教授" if "大学" in category else ("特级教师" if "高中" in category else "资深老师")
    target = "大学生" if "大学" in category else "中小学生"

    prompt = f"请以{level}身份，为{target}写一篇关于'{topic}'的深度教学文章。要求：使用HTML格式(h2,h3,p)，字数不少于1500字。内容需包含核心知识点、例题解析和学习建议。"
    
    data = {
        "model": "glm-4",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    res = requests.post(url, headers=headers, json=data).json()
    return res['choices'][0]['message']['content']

# --- 4. 发布主逻辑 ---

def post_to_wordpress(title, content, category):
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    cat_id = CATEGORY_MAP.get(category, 1)
    
    # 获取特色图片 (保底策略)
    img_url = f"https://source.unsplash.com/featured/?education,{category[-2:]}"
    media_id, media_url = upload_image(img_url, title)
    
    # 构造文章内容：在开头强制插入一张图片，解决文中没图的问题
    if media_url:
        content = f'<p><img src="{media_url}" alt="{title}" style="border-radius:10px;" /></p>' + content

    post_data = {
        'title': title,
        'content': content,
        'status': 'publish',
        'categories': [cat_id],
        'slug': generate_random_slug(),
        'featured_media': media_id if media_id else 0,
        # 这里的 meta 必须配合 functions.php 的注册才能生效
        'meta': {
            'download_link': 'https://www.gogewu.com/dfdprt/', 
            'download_code': '8888'
        }
    }
    
    res = requests.post(f"{WORDPRESS_URL}/wp-json/wp/v2/posts", json=post_data, auth=auth)
    if res.status_code == 201:
        print(f"✅ 发布成功: {title} (ID: {res.json()['id']})")
    else:
        print(f"❌ 发布失败: {res.text}")

def main():
    category = random.choice(list(TOPICS_BY_CATEGORY.keys()))
    topic = random.choice(TOPICS_BY_CATEGORY[category])
    print(f"开始处理: {category} - {topic}")
    
    content = get_zhipu_content(topic, category)
    if content:
        post_to_wordpress(topic, content, category)

if __name__ == "__main__":
    main()
