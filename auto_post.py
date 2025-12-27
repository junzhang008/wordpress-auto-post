import requests
import random
import os
import string
import io
from requests.auth import HTTPBasicAuth

# --- 1. 海量主题库 (全学段全学科) ---
TOPICS_BY_CATEGORY = {
    "一年级数学": ["10以内加减法混合运算", "认识图形特征", "简单的数位概念"],
    "五年级语文": ["古诗词深度赏析", "景物描写高分技巧", "民间故事缩写大纲"],
    "六年级数学": ["圆的面积公式推导", "百分数应用题详解", "比例的性质"],
    "初中物理": ["牛顿第二定律综合应用", "电路串并联识别", "透镜成像规律"],
    "高中数学": ["圆锥曲线离心率求解模板", "三角函数诱导公式", "导数单调性"],
    "大学专业课": ["Python数据结构：平衡二叉树", "宏观经济IS-LM模型", "管理学SWOT分析"]
}

# --- 2. 完整分类 ID 映射 (根据您提供的数据) ---
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

# --- 3. 配置 ---
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
WORDPRESS_URL = os.getenv('WORDPRESS_URL').rstrip('/')
WORDPRESS_USER = os.getenv('WORDPRESS_USER')
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD')

# --- 4. 核心功能函数 ---

def upload_media_final(category):
    """解决图片空白问题：模拟浏览器头，完整抓取二进制流"""
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        # 随机取一个关键词提高图片相关性
        kw = random.choice(["education", "classroom", "study", "books"])
        img_url = f"https://source.unsplash.com/800x450/?{kw},{category[-2:]}"
        
        response = requests.get(img_url, headers=headers, timeout=20, allow_redirects=True)
        if response.status_code != 200: return None, None

        image_stream = io.BytesIO(response.content)
        filename = f"edu_{''.join(random.choices(string.ascii_lowercase, k=8))}.jpg"

        files = {'file': (filename, image_stream, 'image/jpeg')}
        
        res = requests.post(
            f"{WORDPRESS_URL}/wp-json/wp/v2/media",
            files=files, auth=auth,
            headers={'Content-Disposition': f'attachment; filename={filename}'},
            timeout=30
        ).json()
        
        return res.get('id'), res.get('source_url')
    exceptException as e:
        print(f"❌ 图片上传异常: {e}")
        return None, None

def get_or_create_tag_id(tag_name):
    """确保后台正常显示标签（将文字转为 ID）"""
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    try:
        res = requests.get(f"{WORDPRESS_URL}/wp-json/wp/v2/tags?search={tag_name}", auth=auth).json()
        if res and isinstance(res, list) and len(res) > 0:
            return res[0]['id']
        new_tag = requests.post(f"{WORDPRESS_URL}/wp-json/wp/v2/tags", json={'name': tag_name}, auth=auth).json()
        return new_tag.get('id')
    except: return None

# --- 5. 发布主逻辑 ---

def post_to_wordpress(title, content, category):
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    cat_id = CATEGORY_MAP.get(category, 1)
    
    # 获取标签 ID (解决后台无标签问题)
    tag_ids = [get_or_create_tag_id(n) for n in [category[:2], "优质资料"]]
    tag_ids = [i for i in tag_ids if i is not None]

    # 获取图片 (解决媒体库空白问题)
    media_id, img_url = upload_media_final(category)
    
    # 样式修复与图片注入 (解决文中无图与间距问题)
    style_fix = '<style>.entry-content { margin-top: -35px !important; }</style>'
    img_html = f'<p style="text-align:center;"><img src="{img_url}" alt="{title}" style="border-radius:10px; width:100%;" /></p>' if img_url else ""
    
    # 强力注入下载中心 (解决下载不显示问题)
    download_html = f"""
    <div style="border: 2px dashed #1e73be; padding: 20px; background: #f0f8ff; border-radius: 12px; text-align: center; margin-top: 50px;">
        <h3 style="color:#1e73be; margin-top:0;">📂 资源下载中心</h3>
        <p>本篇《{title}》相关配套学习资料已准备就绪。</p>
        <p><strong>下载地址：</strong> <a href="https://www.gogewu.com/download-center/" target="_blank" style="color:#ff4500;">点击进入下载通道</a></p>
        <p><strong>提取码：</strong> <span style="background:#ffd700; padding:2px 8px; font-weight:bold; border-radius:4px;">8888</span></p>
    </div>
    """
    
    final_content = style_fix + img_html + content + download_html

    post_data = {
        'title': title,
        'content': final_content,
        'status': 'publish',
        'categories': [cat_id],
        'tags': tag_ids,
        'featured_media': media_id if media_id else 0,
        'slug': ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)),
        'meta': {
            'download_link': 'https://www.gogewu.com/download-center/', 
            'download_code': '8888'
        }
    }
    
    res = requests.post(f"{WORDPRESS_URL}/wp-json/wp/v2/posts", json=post_data, auth=auth, timeout=30)
    
    if res.status_code == 201:
        print(f"✅ 发布成功: {title}")
    else:
        print(f"❌ 发布失败: {res.text}")

def main():
    category = random.choice(list(TOPICS_BY_CATEGORY.keys()))
    topic = random.choice(TOPICS_BY_CATEGORY[category])
    
    # 此处应有获取 AI 内容的代码
    content = f"<h2>{topic} 知识详解</h2><p>深度解析内容生成中...</p>"
    
    post_to_wordpress(topic, content, category)

if __name__ == "__main__":
    main()
