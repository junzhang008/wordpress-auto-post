import requests
import random
import os
import string
from requests.auth import HTTPBasicAuth

# --- 1. 海量全学段全学科主题库 ---
TOPICS_BY_CATEGORY = {
    "一年级数学": ["10以内加减法口诀", "认识左右上下", "数一数与比一比"],
    "六年级数学": ["圆的周长与面积推导", "百分数应用题详解", "圆柱与圆锥体积"],
    "初中物理": ["串并联电路电压规律", "浮力产生原因", "透镜成像实验"],
    "高中数学": ["三角函数诱导公式", "圆锥曲线离心率", "导数单调性研究"],
    "大学数学": ["泰勒公式展开技巧", "矩阵特征值", "多元函数偏导数"],
    "大学专业课": ["Python数据结构", "宏观经济IS-LM模型", "管理学SWOT分析"]
}

# --- 2. 基础配置 ---
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
WORDPRESS_URL = os.getenv('WORDPRESS_URL').rstrip('/')
WORDPRESS_USER = os.getenv('WORDPRESS_USER')
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD')

CATEGORY_MAP = {
    "一年级数学": 6, "六年级数学": 11, "初中物理": 776,
    "高中数学": 782, "大学数学": 790, "大学专业课": 792
}

# --- 3. 增强功能函数 ---

def get_or_create_tag_id(tag_name):
    """确保获取标签ID（数字），解决后台无标签问题"""
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    try:
        # 搜索现有标签
        res = requests.get(f"{WORDPRESS_URL}/wp-json/wp/v2/tags?search={tag_name}", auth=auth).json()
        if res and isinstance(res, list) and len(res) > 0:
            return res[0]['id']
        # 没找到则创建
        new_tag = requests.post(f"{WORDPRESS_URL}/wp-json/wp/v2/tags", json={'name': tag_name}, auth=auth).json()
        return new_tag.get('id')
    except: return None

def upload_image_and_get_url(category, title):
    """上传图片到媒体库并返回 URL 和 ID"""
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    try:
        img_url = f"https://source.unsplash.com/featured/800x450?education,{category[-2:]}"
        img_content = requests.get(img_url, timeout=15).content
        
        filename = f"post_{''.join(random.choices(string.ascii_lowercase, k=5))}.jpg"
        files = {
            'file': (filename, img_content, 'image/jpeg')
        }
        res = requests.post(f"{WORDPRESS_URL}/wp-json/wp/v2/media", files=files, auth=auth, timeout=30).json()
        return res.get('id'), res.get('source_url')
    except: return None, None

def get_ai_content(topic, category):
    """获取AI文章正文"""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {"Authorization": f"Bearer {ZHIPU_API_KEY}"}
    prompt = f"请以专家身份撰写《{topic}》的深度解析。HTML格式(h2,h3,p)，1500字以上。不要写下载链接。"
    data = {"model": "glm-4", "messages": [{"role": "user", "content": prompt}], "temperature": 0.8}
    res = requests.post(url, headers=headers, json=data, timeout=60).json()
    return res['choices'][0]['message']['content'].strip()

# --- 4. 发布主逻辑 ---

def post_to_wordpress(title, content, category):
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    cat_id = CATEGORY_MAP.get(category, 1)
    
    # A. 处理标签：将文字转为 ID 列表
    tag_names = [category[:2], "精选资源", "格物智库"]
    tag_ids = [get_or_create_tag_id(name) for name in tag_names]
    tag_ids = [i for i in tag_ids if i is not None]

    # B. 处理图片：上传并获取 URL
    media_id, img_url = upload_image_and_get_url(category, title)
    
    # C. 注入 CSS、图片和下载中心
    style_fix = '<style>.entry-content { margin-top: -30px !important; } .download-box { border: 2px dashed #0073aa; padding: 20px; background: #f0f8ff; border-radius: 10px; text-align: center; margin-top: 40px; }</style>'
    
    img_html = ""
    if img_url:
        img_html = f'<p style="text-align:center;"><img src="{img_url}" alt="{title}" style="border-radius:10px; width:100%;" /></p>'
    
    download_html = f"""
    <div class="download-box">
        <h3 style="margin-top:0;">📚 资源下载中心</h3>
        <p>本篇《{title}》相关配套学习资料已打包完成</p>
        <p><strong>下载地址：</strong> <a href="https://www.gogewu.com/download-center/" target="_blank">点击进入下载通道</a></p>
        <p><strong>提取码：</strong> <span style="color:red; font-size:18px;">8888</span></p>
    </div>
    """
    
    # 重新拼接正文
    final_content = style_fix + img_html + content + download_html

    # D. 发布请求
    post_data = {
        'title': title,
        'content': final_content,
        'status': 'publish',
        'categories': [cat_id],
        'tags': tag_ids, # 传递 ID 列表
        'featured_media': media_id if media_id else 0,
        'slug': ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    }
    
    res = requests.post(f"{WORDPRESS_URL}/wp-json/wp/v2/posts", json=post_data, auth=auth, timeout=30)
    
    if res.status_code == 201:
        print(f"✅ 发布成功: {title} (已添加图片、标签和下载中心)")
    else:
        print(f"❌ 失败: {res.text}")

def main():
    category = random.choice(list(TOPICS_BY_CATEGORY.keys()))
    topic = random.choice(TOPICS_BY_CATEGORY[category])
    print(f"🚀 开始处理: {category} - {topic}")
    
    content = get_ai_content(topic, category)
    if content:
        post_to_wordpress(topic, content, category)

if __name__ == "__main__":
    main()
