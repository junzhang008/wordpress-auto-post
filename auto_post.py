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

# --- 1. 海量主题库扩展 (小学、初中、高中、大学全覆盖) ---
TOPICS_BY_CATEGORY = {
    "一年级数学": ["10以内加减法混合运算", "认识图形的特征", "凑十法与破十法"],
    "六年级数学": ["圆的面积公式推导", "百分数应用题详解", "圆柱与圆锥体积比较"],
    "初中数学": ["一元二次方程求根公式", "全等三角形判定定理", "勾股定理应用"],
    "初中物理": ["串并联电路电压规律", "浮力计算公式详解", "透镜成像规律"],
    "高中数学": ["三角函数诱导公式全解", "圆锥曲线离心率求解", "导数单调性研究"],
    "高中物理": ["牛顿第二定律综合应用", "电磁感应楞次定律", "动量守恒分析"],
    "大学数学": ["高等数学：泰勒公式展开", "线性代数：矩阵特征值", "概率论：正态分布"],
    "大学专业课": ["Python数据结构算法", "宏观经济IS-LM模型", "管理学SWOT分析法"]
}

# --- 2. 基础配置 (⚠️ 用户名必须是纯英文，防止报错) ---
ZHIPU_API_KEY = str(os.getenv('ZHIPU_API_KEY', "你的APIKey")).strip()
WORDPRESS_URL = "https://www.gogewu.com/wp-json/wp/v2"
WORDPRESS_USER = "your_english_username"  # 必须是纯英文
WORDPRESS_PASSWORD = "your_application_password" # 必须是应用密码

# 分类 ID 映射
CATEGORY_MAP = {
    "一年级数学": 6, "六年级数学": 11,
    "初中数学": 774, "初中物理": 776,
    "高中数学": 782, "高中物理": 784,
    "大学数学": 790, "大学专业课": 792
}

# --- 3. 核心功能函数 ---

def get_or_create_tag_id(tag_name):
    """修复后台无标签问题：获取或创建标签ID"""
    try:
        auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
        res = requests.get(f"{WORDPRESS_URL}/tags?search={tag_name}", auth=auth, timeout=10).json()
        if res and isinstance(res, list):
            for t in res:
                if t['name'] == tag_name: return t['id']
        new_tag = requests.post(f"{WORDPRESS_URL}/tags", json={'name': tag_name}, auth=auth, timeout=10).json()
        return new_tag.get('id')
    except: return None

def upload_image_logic(category, topic):
    """解决图片不显示问题：下载并上传媒体，返回ID和URL"""
    try:
        # 使用随机图库作为稳定源
        img_url = f"https://source.unsplash.com/featured/800x450?education,{category[-2:]}"
        img_res = requests.get(img_url, timeout=20)
        auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
        # 上传到WordPress
        files = {'file': ('image.jpg', img_res.content, 'image/jpeg')}
        res = requests.post(f"{WORDPRESS_URL}/media", files=files, auth=auth, timeout=30).json()
        return res.get('id'), res.get('source_url')
    except: return None, None

def get_ai_content_safe(topic, category):
    """解决报错问题：安全获取AI内容，确保无特殊编码"""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    api_key_clean = ZHIPU_API_KEY.encode('ascii', 'ignore').decode('ascii')
    headers = {"Authorization": f"Bearer {api_key_clean}", "Content-Type": "application/json"}
    
    prompt = f"请以资深教师身份，为{category}学段写一篇关于《{topic}》的深度解析文章。使用HTML格式(h2,h3,p)，1500字以上。"
    data = {"model": "glm-4", "messages": [{"role": "user", "content": prompt}], "temperature": 0.8}
    
    try:
        res = requests.post(url, headers=headers, json=data, timeout=60).json()
        return res['choices'][0]['message']['content']
    except: return None

# --- 4. 发布逻辑 (修正下载框和间距) ---

def post_to_wordpress(title, content, category):
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    cat_id = CATEGORY_MAP.get(category, 1)
    
    # 1. 准备标签 ID (解决标签不显示问题)
    raw_tags = [category[:2], "资源下载", "格物智库"]
    tag_ids = [get_or_create_tag_id(t) for t in raw_tags if get_or_create_tag_id(t)]

    # 2. 处理图片逻辑 (解决文中和缩略图不显示)
    media_id, img_url = upload_image_logic(category, title)
    if img_url:
        # 强制在内容最前面插入图片 HTML
        img_html = f'<p style="text-align:center;"><img src="{img_url}" alt="{title}" style="border-radius:10px; width:100%;"/></p>'
        content = img_html + content

    # 3. 构造发布数据 (包含下载框 Meta)
    post_data = {
        'title': title,
        'content': content,
        'status': 'publish',
        'categories': [cat_id],
        'tags': tag_ids,
        'featured_media': media_id if media_id else 0,
        'slug': ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10)),
        'meta': {
            'download_link': 'https://www.gogewu.com/download-center/', 
            'download_code': '8888'
        }
    }
    
    # 4. 执行发布
    res = requests.post(f"{WORDPRESS_URL}/posts", json=post_data, auth=auth, timeout=30)
    if res.status_code == 201:
        print(f"✅ 发布成功: {title}")
    else:
        print(f"❌ 发布失败: {res.text}")

def main():
    category = random.choice(list(TOPICS_BY_CATEGORY.keys()))
    topic = random.choice(TOPICS_BY_CATEGORY[category])
    print(f"🚀 正在准备: {category} - {topic}")
    
    content = get_ai_content_safe(topic, category)
    if content:
        post_to_wordpress(topic, content, category)

if __name__ == "__main__":
    main()
