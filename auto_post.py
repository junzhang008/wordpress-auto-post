import requests
import random
import os
import string
import io
from requests.auth import HTTPBasicAuth

# --- 1. 严格保留您的分类 ID 映射 ---
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

# --- 2. 扩充海量主题库 ---
TOPICS_BY_CATEGORY = {
    "大学数学": ["高等数学：泰勒公式展开技巧", "线性代数：矩阵特征值求解", "多重积分计算方法"],
    "高中数学": ["圆锥曲线离心率求解模板", "三角函数诱导公式全解", "导数单调性研究"],
    "初中物理": ["牛顿第二定律综合应用", "串并联电路电压规律", "浮力计算公式详解"],
    "一年级语文": ["拼音字母表快速记忆", "看图写话万能句式", "基础笔画书写规范"]
}

# --- 3. 配置信息 ---
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
WORDPRESS_URL = os.getenv('WORDPRESS_URL').rstrip('/')
WORDPRESS_USER = os.getenv('WORDPRESS_USER')
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD')

# --- 4. 修复后的核心功能函数 ---

def get_or_create_tag_id(tag_name):
    """解决后台无标签问题：强制转换为 ID"""
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    try:
        res = requests.get(f"{WORDPRESS_URL}/wp-json/wp/v2/tags?search={tag_name}", auth=auth, timeout=10).json()
        if res and isinstance(res, list) and len(res) > 0:
            for t in res:
                if t['name'] == tag_name: return t['id']
        new_tag = requests.post(f"{WORDPRESS_URL}/wp-json/wp/v2/tags", json={'name': tag_name}, auth=auth).json()
        return new_tag.get('id')
    except: return None

def upload_diverse_media(category):
    """解决媒体库白块问题：强制抓取二进制流并上传"""
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    # 根据学科匹配搜索词
    mapping = {"数学": "math", "物理": "physics", "语文": "library", "大学": "campus"}
    kw = next((v for k, v in mapping.items() if k in category), "education")
    
    try:
        # 获取图片并处理重定向，获取真实的二进制流
        img_url = f"https://source.unsplash.com/800x450/?{kw}"
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
        ).json()
        return upload_res.get('id'), upload_res.get('source_url')
    except: return None, None

def get_ai_long_content(topic, category):
    """解决内容消失问题：强制生成长文本内容"""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {"Authorization": f"Bearer {ZHIPU_API_KEY}", "Content-Type": "application/json"}
    prompt = f"请以资深教师身份撰写关于《{topic}》的教学解析文章。要求使用HTML格式(h2,h3,p)，内容必须包含知识讲解、经典例题、重点难点，总字数不少于1200字。禁止只输出一句话占位符。"
    
    data = {"model": "glm-4", "messages": [{"role": "user", "content": prompt}], "temperature": 0.8}
    try:
        res = requests.post(url, headers=headers, json=data, timeout=60).json()
        content = res['choices'][0]['message']['content'].strip()
        # 二次检查：如果AI偷懒只吐出一行，则抛弃
        if len(content) < 100: return None
        return content
    except: return None

# --- 5. 发布主逻辑 ---

def post_to_wordpress(title, content, category):
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    cat_id = CATEGORY_MAP.get(category, 1)
    
    # 标签处理 (解决无标签问题)
    tag_names = [category[:2], "精选资源", "格物智库"]
    tag_ids = [get_or_create_tag_id(name) for name in tag_names if get_or_create_tag_id(name)]

    # 媒体上传 (解决白块问题)
    media_id, img_url = upload_diverse_media(category)
    
    # 样式修复：解决标题重叠
    style_fix = '<style>.entry-content { margin-top: 30px !important; } .entry-header { margin-bottom: 20px !important; }</style>'
    img_html = f'<p style="text-align:center;"><img src="{img_url}" alt="{title}" style="border-radius:10px; width:100%;" /></p>' if img_url else ""
    
    # 下载框模块 (解决下载不显示问题)
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
    print(f"🚀 任务启动: {category} - {topic}")
    
    content = get_ai_long_content(topic, category)
    if content:
        post_to_wordpress(topic, content, category)

if __name__ == "__main__":
    main()
