import requests
import random
import os
import string
import io
from requests.auth import HTTPBasicAuth

# --- 1. 海量主题库 (全学段全学科) ---
TOPICS_BY_CATEGORY = {
    "一年级数学": ["10以内加减法练习", "认识图形特征", "简单的数位概念"],
    "六年级语文": ["小升初作文万能开头", "古诗词名句深度解析", "六年级下册必考字词"],
    "初中物理": ["牛顿第二定律综合应用", "电路串并联识别方法", "透镜成像实验步骤"],
    "高中数学": ["圆锥曲线离心率求解模板", "三角函数诱导公式全解", "导数单调性研究"],
    "大学专业课": ["Python数据结构：平衡二叉树", "宏观经济IS-LM模型分析", "管理学SWOT分析法"]
}

# --- 2. 您完整的分类 ID 映射 (修正无误版) ---
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
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD') # 必须使用“应用密码”

# --- 4. 核心功能函数 ---

def upload_media_final(category, title):
    """解决图片空白问题：确保二进制流完整并强制指定MIME类型"""
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    try:
        # 获取高质量教育类图片
        img_url = f"https://source.unsplash.com/800x450/?education,{category[-2:]}"
        response = requests.get(img_url, timeout=20, allow_redirects=True)
        
        if response.status_code != 200: return None, None

        # 将二进制内容包装，并生成唯一文件名
        image_stream = io.BytesIO(response.content)
        filename = f"edu_{''.join(random.choices(string.ascii_lowercase, k=8))}.jpg"

        # 关键修复：显式指定文件名、内容流、和MIME类型
        files = {
            'file': (filename, image_stream, 'image/jpeg')
        }
        
        # 上传到 WordPress 媒体库
        res = requests.post(
            f"{WORDPRESS_URL}/wp-json/wp/v2/media",
            files=files,
            auth=auth,
            headers={'Content-Disposition': f'attachment; filename={filename}'},
            timeout=30
        ).json()
        
        return res.get('id'), res.get('source_url')
    except Exception as e:
        print(f"❌ 图片上传异常: {e}")
        return None, None

def get_or_create_tag_id(tag_name):
    """确保标签正常显示（ID 模式）"""
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
    
    # A. 标签处理
    tag_ids = [get_or_create_tag_id(n) for n in [category[:2], "优质资源"]]
    tag_ids = [i for i in tag_ids if i is not None]

    # B. 图片处理 (解决空白问题)
    media_id, img_url = upload_media_final(category, title)
    
    # C. 样式修复：压低间距
    style_fix = '<style>.entry-content { margin-top: -35px !important; }</style>'
    
    # D. 强制文中图片显示
    img_html = f'<p style="text-align:center;"><img src="{img_url}" alt="{title}" style="border-radius:10px; width:100%;" /></p>' if img_url else ""
    
    # E. 强力注入下载中心
    download_html = f"""
    <div style="border: 2px dashed #1e73be; padding: 25px; background: #f0f8ff; border-radius: 12px; text-align: center; margin-top: 50px;">
        <h3 style="color:#1e73be; margin-top:0;">📂 资源下载中心</h3>
        <p>本篇《{title}》相关配套讲义及练习资料已打包完成。</p>
        <p><strong>下载地址：</strong> <a href="https://www.gogewu.com/download-center/" target="_blank" style="color:#ff4500;">点击跳转至下载通道</a></p>
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
        print(f"✅ 发布成功: {title} (图片、标签、下载框已全部强制注入)")
    else:
        print(f"❌ 发布失败: {res.text}")

def main():
    category = random.choice(list(TOPICS_BY_CATEGORY.keys()))
    topic = random.choice(TOPICS_BY_CATEGORY[category])
    
    # 此处假设您已经调用了 AI 获取 content，这里做模拟演示
    content = f"<h2>{topic} 核心知识点</h2><p>高质量学习内容深度解析中...</p>"
    
    post_to_wordpress(topic, content, category)

if __name__ == "__main__":
    main()
