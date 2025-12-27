import requests
import random
import os
import string
import io
from requests.auth import HTTPBasicAuth

# --- 1. 您的全量分类 ID (严格保留，绝不丢失) ---
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

# --- 2. 扩充版海量主题库 (全学科覆盖) ---
TOPICS_BY_CATEGORY = {
    "一年级数学": ["10以内加减法口诀", "认识图形特征", "凑十法与破十法", "认识钟表简单时间"],
    "六年级数学": ["圆的周长与面积推导", "百分数应用题详解", "圆柱与圆锥体积比较", "比例的基本性质"],
    "初中物理": ["牛顿第二定律综合应用", "电路串并联电压规律", "浮力计算公式", "透镜成像规律实验"],
    "初中化学": ["金属活动性顺序表", "常用实验室仪器名称", "酸碱盐化学性质总结", "原子结构示意图"],
    "高中数学": ["圆锥曲线离心率求解模板", "三角函数诱导公式全解", "导数单调性研究", "等差等比数列求和"],
    "大学专业课": ["Python数据结构：平衡二叉树", "宏观经济IS-LM模型", "管理学SWOT分析", "操作系统进程调度"]
}

# --- 3. 配置 ---
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
WORDPRESS_URL = os.getenv('WORDPRESS_URL').rstrip('/')
WORDPRESS_USER = os.getenv('WORDPRESS_USER')
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD')

# --- 4. 修复后的功能模块 ---

def upload_media_properly(category):
    """修复图片空白与重复：确保二进制流完整"""
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    try:
        # 使用稳定的静态图源，避免重定向导致的白块
        img_url = f"https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=800&q=80"
        res = requests.get(img_url, timeout=20)
        img_data = io.BytesIO(res.content)
        filename = f"edu_{''.join(random.choices(string.ascii_lowercase, k=6))}.jpg"
        
        files = {'file': (filename, img_data, 'image/jpeg')}
        media_res = requests.post(
            f"{WORDPRESS_URL}/wp-json/wp/v2/media",
            files=files, auth=auth,
            headers={'Content-Disposition': f'attachment; filename={filename}'},
            timeout=30
        ).json()
        return media_res.get('id'), media_res.get('source_url')
    except: return None, None

def get_or_create_tag(tag_name):
    """物理修复：强制返回 ID，确保后台有标签"""
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    try:
        res = requests.get(f"{WORDPRESS_URL}/wp-json/wp/v2/tags?search={tag_name}", auth=auth).json()
        if res and isinstance(res, list) and len(res) > 0:
            return res[0]['id']
        new_tag = requests.post(f"{WORDPRESS_URL}/wp-json/wp/v2/tags", json={'name': tag_name}, auth=auth).json()
        return new_tag.get('id')
    except: return None

# --- 5. 发布逻辑 (参考第一份脚本并优化) ---

def post_to_wordpress_final(title, content, category):
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    cat_id = CATEGORY_MAP.get(category, 1)
    
    # 获取标签 ID (关键修复)
    tag_ids = [get_or_create_tag(n) for n in [category[:2], "优质讲义"]]
    tag_ids = [i for i in tag_ids if i]

    # 上传媒体
    media_id, img_url = upload_media_properly(category)
    
    # 样式修复：解决间距过大、图片重复问题
    # 限制正文图片高度，防止出现“两张大图”的视觉干扰
    style_fix = '<style>.wp-post-image { display:none; } .entry-content img { max-height: 400px; width: auto; margin: 0 auto 20px; display: block; } h2 { margin-top: 10px !important; }</style>'
    
    # 下载模块
    download_html = f"""
    <div style="border: 2px dashed #1e73be; padding: 20px; background: #f9f9f9; border-radius: 10px; margin-top: 30px; text-align: center;">
        <h3 style="margin-top:0;">📂 资源下载</h3>
        <p>配套资料《{title}》已就绪</p>
        <p><a href="https://www.gogewu.com/download-center/" target="_blank" style="color:#ff4500;font-weight:bold;">点此进入下载中心</a> (提取码: 8888)</p>
    </div>
    """
    
    # 最终内容拼装：首图 + 正文 + 下载框
    img_html = f'<p><img src="{img_url}" /></p>' if img_url else ""
    final_content = style_fix + img_html + content + download_html

    post_data = {
        'title': title,
        'content': final_content,
        'status': 'publish',
        'categories': [cat_id],
        'tags': tag_ids,
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
    
    # 假设此处调用 AI 生成 content
    content = f"<h2>知识详解</h2><p>针对{topic}的深度内容...</p>"
    post_to_wordpress_final(topic, content, category)

if __name__ == "__main__":
    main()
