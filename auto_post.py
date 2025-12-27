import requests
import random
import os
import string
import io
from requests.auth import HTTPBasicAuth

# --- 1. 分类 ID 映射 (严格保留您的数据) ---
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

# --- 2. 主题库 ---
TOPICS_BY_CATEGORY = {
    "大学数学": ["高等数学：泰勒公式展开技巧", "线性代数：矩阵特征值求解", "多重积分计算方法"],
    "初中物理": ["牛顿第二定律综合应用", "串并联电路电压规律", "浮力计算公式详解"],
    "一年级语文": ["拼音字母表快速记忆", "看图写话万能句式", "基础笔画书写规范"]
}

# --- 3. 配置信息 ---
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
WORDPRESS_URL = os.getenv('WORDPRESS_URL').rstrip('/')
WORDPRESS_USER = os.getenv('WORDPRESS_USER')
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD')

# --- 4. 核心功能函数 ---

def get_or_create_tag_id(tag_name):
    """【解决后台无标签】将文字标签转为 WP 识别的 ID 数字"""
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    try:
        # 搜索现有标签
        search_res = requests.get(f"{WORDPRESS_URL}/wp-json/wp/v2/tags?search={tag_name}", auth=auth, timeout=10)
        res = search_res.json()
        if res and isinstance(res, list) and len(res) > 0:
            for t in res:
                if t['name'] == tag_name: return t['id']
        # 创建新标签
        new_tag_res = requests.post(f"{WORDPRESS_URL}/wp-json/wp/v2/tags", json={'name': tag_name}, auth=auth)
        new_tag = new_tag_res.json()
        return new_tag.get('id')
    except: return None

def upload_diverse_media(category, topic):
    """【解决图片单一且无法加载】根据科目匹配图库关键词，并处理二进制流"""
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    
    # 建立学科与图片的关键词映射
    mapping = {
        "数学": ["geometry", "math", "calculation", "formula"],
        "物理": ["physics", "laboratory", "electricity", "experiment"],
        "化学": ["chemistry", "test tube", "molecule", "reaction"],
        "语文": ["library", "ancient book", "writing", "calligraphy"],
        "英语": ["english", "alphabet", "global", "vocabulary"]
    }
    
    # 根据分类动态选择搜索词
    kws = ["education", "classroom", "student"]
    for key, val in mapping.items():
        if key in category:
            kws.extend(val)
            break
    keyword = random.choice(kws)

    try:
        # 确保处理重定向，获取真实的图片流以防止白块
        img_url = f"https://source.unsplash.com/800x450/?{keyword}"
        img_res = requests.get(img_url, timeout=20, allow_redirects=True)
        if img_res.status_code != 200: return None, None
        
        image_data = io.BytesIO(img_res.content)
        filename = f"edu_{''.join(random.choices(string.ascii_lowercase, k=8))}.jpg"
        
        files = {'file': (filename, image_data, 'image/jpeg')}
        upload_res = requests.post(
            f"{WORDPRESS_URL}/wp-json/wp/v2/media",
            files=files, auth=auth,
            headers={'Content-Disposition': f'attachment; filename={filename}'},
            timeout=30
        )
        res = upload_res.json()
        return res.get('id'), res.get('source_url')
    except: return None, None

def post_to_wordpress(title, content, category):
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    cat_id = CATEGORY_MAP.get(category, 1)
    
    # 1. 自动转换标签文字为 ID 数字
    raw_tag_names = [category[:2], category[-2:], "学习资料"]
    tag_ids = [get_or_create_tag_id(name) for name in raw_tag_names if get_or_create_tag_id(name)]

    # 2. 获取并上传多样化图片
    media_id, img_url = upload_diverse_media(category, title)
    
    # 3. 样式修正：缩短标题与图片间距并修复可能的重叠
    style_fix = '<style>.entry-content { margin-top: -35px !important; } .entry-header { margin-bottom: 5px !important; }</style>'
    
    # 4. 注入正文首图及下载框
    img_html = f'<p style="text-align:center;"><img src="{img_url}" alt="{title}" style="border-radius:10px; width:100%;" /></p>' if img_url else ""
    
    download_html = f"""
    <div style="border: 2px dashed #1e73be; padding: 25px; background: #f0f8ff; border-radius: 12px; text-align: center; margin-top: 50px; clear: both;">
        <h3 style="color:#1e73be; margin-top:0;">📂 资源下载中心</h3>
        <p>本篇《{title}》相关配套讲义及练习资料已打包完成。</p>
        <p><strong>下载地址：</strong> <a href="https://www.gogewu.com/download-center/" target="_blank" style="color:#ff4500; font-weight:bold;">点击跳转至下载通道</a></p>
        <p><strong>提取码：</strong> <span style="background:#ffd700; padding:2px 8px; font-weight:bold; border-radius:4px;">8888</span></p>
    </div>
    """
    
    final_content = style_fix + img_html + content + download_html

    post_data = {
        'title': title,
        'content': final_content,
        'status': 'publish',
        'categories': [cat_id],
        'tags': tag_ids, # 发送 ID 列表而非文字
        'featured_media': media_id if media_id else 0,
        'slug': ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    }
    
    res = requests.post(f"{WORDPRESS_URL}/wp-json/wp/v2/posts", json=post_data, auth=auth, timeout=30)
    if res.status_code == 201:
        print(f"✅ 发布成功: {title}")
    else:
        print(f"❌ 失败: {res.text}")

# --- 5. 运行 ---
def main():
    category = random.choice(list(TOPICS_BY_CATEGORY.keys()))
    topic = random.choice(TOPICS_BY_CATEGORY[category])
    
    # 这里接入您的 AI 内容生成逻辑
    content = f"<h2>{topic} 深度解析</h2><p>高质量学习内容生成中...</p>"
    
    post_to_wordpress(topic, content, category)

if __name__ == "__main__":
    main()
