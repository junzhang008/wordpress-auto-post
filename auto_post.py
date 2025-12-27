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

# --- 1. 海量主题库：覆盖全学段各学科 ---
TOPICS_BY_CATEGORY = {
    # 小学
    "一年级数学": ["10以内加减法练习", "认识图形"], "六年级数学": ["圆的面积计算", "比例应用"],
    "三年级语文": ["段落写作基础", "成语故事"], "六年级英语": ["一般将来时用法", "语法综合"],
    # 初中
    "初中数学": ["有理数运算技巧", "一元一次方程", "几何证明题入门", "函数图像性质"],
    "初中物理": ["电路图绘制基础", "浮力计算公式", "透镜成像规律", "机械能守恒"],
    "初中化学": ["酸碱盐性质", "化学方程式配平", "实验室制取氧气"],
    # 高中
    "高中数学": ["集合与函数概念", "三角函数变换", "圆锥曲线模板", "导数单调性"],
    "高中物理": ["牛顿定律应用", "电磁感应综合", "动量守恒定律", "天体运动"],
    "高中化学": ["有机官能团总结", "电解池原理", "物质的量浓度"],
    # 大学
    "大学数学": ["高等数学：极限与连续", "线性代数：矩阵", "概率论：正态分布"],
    "大学英语": ["四六级写作模板", "考研长难句拆解", "学术论文表达"],
    "大学专业课": ["Python算法分析", "宏观经济模型", "管理学SWOT分析"]
}

# --- 2. 配置 (请使用你原始脚本中验证通过的配置) ---
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
WORDPRESS_URL = os.getenv('WORDPRESS_URL').rstrip('/')
WORDPRESS_USER = os.getenv('WORDPRESS_USER')
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD')
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY')

CATEGORY_MAP = {
    "一年级数学": 6, "六年级数学": 11,
    "初中数学": 774, "初中物理": 776,
    "高中数学": 782, "高中物理": 784,
    "大学数学": 790, "大学专业课": 792
}

# --- 3. 核心功能函数 (回归原始逻辑) ---

def generate_random_slug(length=8):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

def upload_image_to_wordpress(image_url, title):
    """【修复图片显示】下载并上传媒体库，返回ID和URL"""
    try:
        response = requests.get(image_url, timeout=15)
        auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
        filename = f"{generate_random_slug()}.jpg"
        res = requests.post(
            f"{WORDPRESS_URL}/wp-json/wp/v2/media",
            headers={'Content-Disposition': f'attachment; filename={filename}', 'Content-Type': 'image/jpeg'},
            data=response.content, auth=auth, timeout=30
        ).json()
        return res.get('id'), res.get('source_url')
    except: return None, None

def get_zhipu_ai_content(topic, category):
    """【AI生成】根据学段自动匹配身份"""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {"Authorization": f"Bearer {ZHIPU_API_KEY}", "Content-Type": "application/json"}
    
    # 动态设定身份，解决“间距和专业度”问题
    level = "教授" if "大学" in category else ("特级教师" if "高中" in category else "资深教师")
    
    prompt = f"请以{level}身份，为学生写一篇关于《{topic}》的深度解析。HTML格式，包含h2/h3/p，1500字以上。内容要紧凑，不要有多余的空行。"
    
    data = {
        "model": "glm-4",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8
    }
    res = requests.post(url, headers=headers, json=data, timeout=60).json()
    return res['choices'][0]['message']['content'].strip()

# --- 4. 发布主逻辑 (严格执行原始发布流程) ---

def post_to_wordpress_with_tags(title, content, category, slug):
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    category_id = CATEGORY_MAP.get(category, 1)
    
    # 1. 自动获取图片并插入文中 (解决文中无图)
    img_kw = f"education,{category[-2:]}"
    img_url_raw = f"https://source.unsplash.com/featured/800x450?{img_kw}"
    media_id, media_src = upload_image_to_wordpress(img_url_raw, title)
    
    # 强制在开头插入图片并修复间距样式
    style_fix = '<style>.entry-content { margin-top: -25px !important; }</style>'
    if media_src:
        img_html = f'<p style="text-align:center;"><img src="{media_src}" alt="{title}" style="border-radius:8px;"/></p>'
        content = style_fix + img_html + content
    else:
        content = style_fix + content

    # 2. 构造数据 (严格匹配 WP API 格式)
    post_data = {
        'title': title,
        'content': content,
        'status': 'publish',
        'categories': [category_id],
        'slug': slug,
        'featured_media': media_id if media_id else 0,
        # 【关键：下载框自动化】前提是你在 functions.php 注册了这两个 meta
        'meta': {
            'download_link': 'https://www.gogewu.com/download-center/',
            'download_code': '8888'
        }
    }
    
    res = requests.post(f"{WORDPRESS_URL}/wp-json/wp/v2/posts", json=post_data, auth=auth, timeout=30)
    
    if res.status_code == 201:
        print(f"✅ 发布成功: {title}")
        return True
    else:
        print(f"❌ 发布失败: {res.text}")
        return False

def main():
    category = random.choice(list(TOPICS_BY_CATEGORY.keys()))
    topic = random.choice(TOPICS_BY_CATEGORY[category])
    print(f"🚀 处理中: {category} - {topic}")
    
    content = get_zhipu_ai_content(topic, category)
    if content:
        slug = generate_random_slug()
        post_to_wordpress_with_tags(topic, content, category, slug)

if __name__ == "__main__":
    main()
