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

# --- 1. 大幅扩充的主题库 (涵盖全学段) ---
TOPICS_BY_CATEGORY = {
    "一年级数学": ["10以内加减法口诀", "认识左右上下", "数一数与比一比", "认识钟表简单时间"],
    "六年级数学": ["圆的周长与面积推导", "百分数应用题详解", "圆柱与圆锥体积比较", "扇形统计图分析"],
    "初中数学": ["有理数的混合运算", "一元一次方程应用题", "勾股定理逆定理证明", "二次函数图像平移规律", "全等三角形判定"],
    "初中物理": ["串并联电路电压规律", "浮力产生的原因", "平面镜成像实验", "动能与势能转化"],
    "初中化学": ["金属活动性顺序表", "常用实验室仪器名称", "质量守恒定律验证", "饱和溶液与不饱和溶液"],
    "高中数学": ["集合的运算符号", "三角函数诱导公式", "等差数列求和公式", "圆锥曲线离心率", "导数单调性研究"],
    "高中物理": ["牛顿第二定律综合应用", "带电粒子在磁场中运动", "动量守恒动能不守恒分析", "光电效应方程"],
    "高中化学": ["有机官能团化学性质", "原电池正负极判断", "勒夏特列原理应用", "物质的量浓度换算"],
    "大学数学": ["泰勒公式展开技巧", "矩阵特征值与特征向量", "多元函数偏导数", "贝叶斯公式应用"],
    "大学英语": ["CET4高频核心词汇", "考研英语长难句拆解", "学术论文摘要写作规范", "雅思口语提分思路"],
    "大学专业课": ["Python数据结构与算法", "宏观经济学IS-LM模型", "心理学马斯洛需求层次", "管理学SWOT分析法"]
}

# --- 2. 基础配置 ---
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
WORDPRESS_URL = os.getenv('WORDPRESS_URL').rstrip('/')
WORDPRESS_USER = os.getenv('WORDPRESS_USER')
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD')

CATEGORY_MAP = {
    "一年级数学": 6, "六年级数学": 11,
    "初中数学": 774, "初中语文": 773, "初中英语": 775, "初中物理": 776, "初中化学": 777,
    "高中数学": 782, "高中语文": 781, "高中英语": 783, "高中物理": 784, "高中化学": 785,
    "大学数学": 790, "大学英语": 789, "大学专业课": 792
}

# --- 3. 增强功能函数 ---

def generate_random_slug(length=10):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

def get_or_create_tag_id(tag_name):
    """确保获取标签ID (修复后台无标签的关键)"""
    try:
        auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
        # 搜索标签
        res = requests.get(f"{WORDPRESS_URL}/wp-json/wp/v2/tags?search={tag_name}", auth=auth, timeout=10).json()
        if res and isinstance(res, list):
            for t in res:
                if t['name'] == tag_name: return t['id']
        # 创建标签
        new_tag = requests.post(f"{WORDPRESS_URL}/wp-json/wp/v2/tags", json={'name': tag_name, 'slug': tag_name}, auth=auth, timeout=10).json()
        return new_tag.get('id')
    except: return None

def upload_media(image_url, title):
    """上传并获取媒体ID"""
    try:
        img_data = requests.get(image_url, timeout=20).content
        auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
        res = requests.post(
            f"{WORDPRESS_URL}/wp-json/wp/v2/media",
            headers={'Content-Disposition': f'attachment; filename={generate_random_slug()}.jpg', 'Content-Type': 'image/jpeg'},
            data=img_data, auth=auth, timeout=30
        ).json()
        return res.get('id'), res.get('source_url')
    except: return None, None

def get_ai_content(topic, category):
    """AI内容生成，强制包含图片占位符"""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {"Authorization": f"Bearer {ZHIPU_API_KEY}"}
    
    prompt = f"""你是一名资深教育专家，请为'{category}'学段的学生撰写关于'{topic}'的教学文章。
    要求：
    1. 使用HTML格式(h2, h3, p)，不少于1500字。
    2. 内容需包含知识点拨、例题精讲和课后思考。
    3. 必须在文中适当位置插入两个 [IMAGE_PLACEHOLDER] 标签。"""
    
    data = {"model": "glm-4", "messages": [{"role": "user", "content": prompt}], "temperature": 0.8}
    res = requests.post(url, headers=headers, json=data, timeout=60).json()
    return res['choices'][0]['message']['content']

# --- 4. 发布逻辑 ---

def post_to_wordpress(title, content, category):
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    cat_id = CATEGORY_MAP.get(category, 1)
    
    # 1. 准备标签 (从标题和分类中提取)
    raw_tags = [category[:2], category[2:], title[:4], "学习资料", "格物智库"]
    tag_ids = [get_or_create_tag_id(t) for t in raw_tags if get_or_create_tag_id(t)]

    # 2. 处理图片
    # 使用保底图库源，确保一定能抓到图
    img_url = f"https://source.unsplash.com/featured/800x450/?education,{category[-2:]}"
    media_id, media_src = upload_media(img_url, title)
    
    # 3. 强制在文中替换图片占位符 (解决文中无图)
    if media_src:
        img_html = f'<div style="text-align:center;"><img src="{media_src}" alt="{title}" style="border-radius:10px; max-width:100%;"/><p style="font-size:12px;color:#999;">{title} 相关图解</p></div>'
        content = content.replace("[IMAGE_PLACEHOLDER]", img_html, 1) # 替换第一个占位符
        content = content.replace("[IMAGE_PLACEHOLDER]", "", 1) # 删掉多余的
        # 在正文最前面也加一张图
        content = img_html + content

    post_data = {
        'title': title,
        'content': content,
        'status': 'publish',
        'categories': [cat_id],
        'tags': tag_ids, # 发布标签ID列表
        'featured_media': media_id if media_id else 0,
        'meta': {
            'download_link': 'https://www.gogewu.com/download-center/', 
            'download_code': '8888'
        }
    }
    
    res = requests.post(f"{WORDPRESS_URL}/wp-json/wp/v2/posts", json=post_data, auth=auth, timeout=30)
    if res.status_code == 201:
        print(f"✅ 发布成功: {title} (ID: {res.json()['id']})")
    else:
        print(f"❌ 发布失败: {res.text}")

def main():
    # 随机选择主题进行发布
    category = random.choice(list(TOPICS_BY_CATEGORY.keys()))
    topic = random.choice(TOPICS_BY_CATEGORY[category])
    print(f"🚀 开始处理: {category} - {topic}")
    
    content = get_ai_content(topic, category)
    if content:
        post_to_wordpress(topic, content, category)

if __name__ == "__main__":
    main()
