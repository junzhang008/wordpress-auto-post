import requests
import random
import os
import string
from requests.auth import HTTPBasicAuth

# --- 1. 海量主题库 (全学段覆盖) ---
TOPICS_BY_CATEGORY = {
    "一年级数学": ["10以内加减法口诀", "认识图形特征", "凑十法与破十法"],
    "六年级数学": ["圆的周长与面积推导", "百分数应用题详解", "圆柱与圆锥体积"],
    "初中物理": ["串并联电路电压规律", "浮力计算公式", "透镜成像实验"],
    "高中数学": ["三角函数诱导公式", "圆锥曲线离心率", "导数单调性研究"],
    "大学数学": ["高等数学：泰勒公式展开", "线性代数矩阵特征值", "概率论正态分布"],
    "大学专业课": ["Python数据结构算法", "宏观经济IS-LM模型", "管理学SWOT分析"]
}

# --- 2. 您的完整分类 ID 映射 (已补全) ---
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

# --- 3. 基础配置 ---
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
WORDPRESS_URL = os.getenv('WORDPRESS_URL').rstrip('/')
WORDPRESS_USER = os.getenv('WORDPRESS_USER')
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD')

# --- 4. 修复后的图片上传函数 ---

def upload_media_fixed(category, title):
    """解决图片空白问题：模拟浏览器请求并处理重定向"""
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        # 1. 获取真实图片流
        img_url = f"https://source.unsplash.com/800x450/?education,{category[-2:]}"
        img_res = requests.get(img_url, headers=headers, timeout=20, allow_redirects=True)
        
        if img_res.status_code != 200:
            return None, None

        # 2. 上传至 WordPress
        filename = f"edu_{''.join(random.choices(string.ascii_lowercase, k=6))}.jpg"
        files = {
            'file': (filename, img_res.content, 'image/jpeg')
        }
        res = requests.post(
            f"{WORDPRESS_URL}/wp-json/wp/v2/media",
            headers={'Content-Disposition': f'attachment; filename={filename}'},
            files=files, auth=auth, timeout=30
        ).json()
        
        return res.get('id'), res.get('source_url')
    except Exception as e:
        print(f"图片处理失败: {e}")
        return None, None

def get_or_create_tag_id(tag_name):
    """获取标签ID，确保后台显示标签"""
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
    
    # 标签处理
    tag_names = [category[:2], "优质资源", "格物智库"]
    tag_ids = [get_or_create_tag_id(name) for name in tag_names if get_or_create_tag_id(name)]

    # 图片处理
    media_id, img_url = upload_media_fixed(category, title)
    
    # 样式修复与文末下载模块注入
    style_fix = '<style>.entry-content { margin-top: -30px !important; } .dl-section { border: 2px dashed #1e73be; padding: 20px; background: #f9fbfd; border-radius: 12px; text-align: center; margin-top: 40px; }</style>'
    
    img_html = f'<p style="text-align:center;"><img src="{img_url}" alt="{title}" style="border-radius:10px; width:100%;" /></p>' if img_url else ""
    
    # 强行加入下载中心模块
    download_html = f"""
    <div class="dl-section">
        <h3 style="color:#1e73be; margin-top:0;">📂 资源下载中心</h3>
        <p>本篇《{title}》相关配套讲义及练习资料已更新。</p>
        <p><strong>下载地址：</strong> <a href="https://www.gogewu.com/download-center/" target="_blank" style="color:#ff4500;">点击进入下载中心</a></p>
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
        'slug': ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    }
    
    res = requests.post(f"{WORDPRESS_URL}/wp-json/wp/v2/posts", json=post_data, auth=auth, timeout=30)
    
    if res.status_code == 201:
        print(f"✅ 发布成功: {title}")
    else:
        print(f"❌ 发布失败: {res.text}")

def main():
    category = random.choice(list(TOPICS_BY_CATEGORY.keys()))
    topic = random.choice(TOPICS_BY_CATEGORY[category])
    
    # 模拟 AI 生成 (此处应替换为您真实的 AI 调用逻辑)
    content = f"<h2>{topic} 深度解析</h2><p>高质量教学内容生成中...</p>"
    
    post_to_wordpress(topic, content, category)

if __name__ == "__main__":
    main()
