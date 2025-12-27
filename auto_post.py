import requests
import random
import os
import string
from requests.auth import HTTPBasicAuth

# --- 1. 海量主题库 (涵盖全学段、全学科) ---
TOPICS_BY_CATEGORY = {
    "一年级数学": ["10以内加减法口诀", "认识图形特征", "凑十法与破十法"],
    "六年级语文": ["古诗词赏析技巧", "六年级下册作文大纲", "文言文基础知识总结"],
    "初中物理": ["串并联电路电压规律", "浮力计算公式详解", "透镜成像实验"],
    "初中化学": ["金属活动性顺序表", "常用实验室仪器名称", "化学方程式配平"],
    "高中数学": ["圆锥曲线离心率求解模板", "三角函数诱导公式全解", "导数单调性研究"],
    "高中物理": ["牛顿第二定律综合应用", "电磁感应楞次定律", "动量守恒"],
    "大学数学": ["高等数学：泰勒公式展开技巧", "线性代数：矩阵特征值", "概率论分布"],
    "大学专业课": ["Python数据结构：算法分析", "宏观经济学模型", "管理学SWOT分析"],
    # 您可以按照此格式继续在此扩充数千个知识点...
}

# --- 2. 您的完整分类 ID 映射 ---
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
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD') # 请务必使用“应用密码”

# --- 4. 增强功能核心函数 ---

def get_or_create_tag_id(tag_name):
    """解决后台无标签问题：获取或创建标签 ID"""
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    try:
        res = requests.get(f"{WORDPRESS_URL}/wp-json/wp/v2/tags?search={tag_name}", auth=auth, timeout=10).json()
        if res and isinstance(res, list) and len(res) > 0:
            return res[0]['id']
        new_tag = requests.post(f"{WORDPRESS_URL}/wp-json/wp/v2/tags", json={'name': tag_name}, auth=auth, timeout=10).json()
        return new_tag.get('id')
    except: return None

def upload_media_and_get_info(category, title):
    """解决文中无图问题：先上传到媒体库，返回 ID 和 URL"""
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    try:
        # 使用更精准的教育类图片源
        img_url = f"https://source.unsplash.com/featured/800x450?education,{category[-2:]}"
        img_content = requests.get(img_url, timeout=20).content
        
        filename = f"edu_{''.join(random.choices(string.ascii_lowercase + string.digits, k=6))}.jpg"
        files = {'file': (filename, img_content, 'image/jpeg')}
        
        res = requests.post(f"{WORDPRESS_URL}/wp-json/wp/v2/media", files=files, auth=auth, timeout=30).json()
        return res.get('id'), res.get('source_url')
    except: return None, None

def get_ai_content(topic, category):
    """生成正文内容"""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {"Authorization": f"Bearer {ZHIPU_API_KEY}"}
    prompt = f"请以资深专家的身份撰写关于《{topic}》的教学解析文章。要求：使用HTML格式(h2,h3,p)，1500字以上。内容必须包含知识讲解、重点难点。不要写下载链接。"
    data = {"model": "glm-4", "messages": [{"role": "user", "content": prompt}], "temperature": 0.8}
    res = requests.post(url, headers=headers, json=data, timeout=60).json()
    return res['choices'][0]['message']['content'].strip()

# --- 5. 发布主逻辑 ---

def post_to_wordpress(title, content, category):
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    cat_id = CATEGORY_MAP.get(category, 1)
    
    # A. 标签处理（转为 ID）
    tag_names = [category[:2], "名师讲义", "格物智库"]
    tag_ids = [get_or_create_tag_id(name) for name in tag_names]
    tag_ids = [i for i in tag_ids if i is not None]

    # B. 图片处理（获取 ID 与 URL）
    media_id, img_url = upload_media_and_get_info(category, title)
    
    # C. 样式优化、图片注入与下载中心注入
    style_fix = '<style>.entry-content { margin-top: -30px !important; } .dl-box { border: 2px dashed #1e73be; padding: 20px; background: #f0f7ff; border-radius: 12px; text-align: center; margin-top: 30px; }</style>'
    
    img_html = f'<p style="text-align:center;"><img src="{img_url}" alt="{title}" style="border-radius:10px; width:100%;" /></p>' if img_url else ""
    
    download_html = f"""
    <div class="dl-box">
        <h3 style="color:#1e73be; margin-top:0;">📂 资源下载中心</h3>
        <p>本篇《{title}》相关配套讲义及练习题已打包完毕。</p>
        <p><strong>下载地址：</strong> <a href="https://www.gogewu.com/download-center/" target="_blank" style="color:#ff4500;">点击进入下载中心</a></p>
        <p><strong>提取码：</strong> <span style="background:#ffd700; padding:2px 8px; font-weight:bold; border-radius:4px;">8888</span></p>
    </div>
    """
    
    final_content = style_fix + img_html + content + download_html

    # D. 执行发布
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
    print(f"🚀 任务启动: [{category}] - {topic}")
    
    content = get_ai_content(topic, category)
    if content:
        post_to_wordpress(topic, content, category)

if __name__ == "__main__":
    main()
