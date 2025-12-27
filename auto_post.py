import requests
import random
import os
import string
import io
from requests.auth import HTTPBasicAuth

# --- 1. 海量主题库 (涵盖全学段、全学科) ---
TOPICS_BY_CATEGORY = {
    "一年级数学": ["10以内加减法混合运算", "认识图形特征", "凑十法与破十法"],
    "六年级数学": ["圆的周长与面积推导", "百分数应用题详解", "圆柱与圆锥体积比较"],
    "初中物理": ["串并联电路电压规律", "浮力计算公式详解", "透镜成像规律解析"],
    "高中数学": ["三角函数诱导公式全解", "圆锥曲线离心率求解模板", "导数单调性研究"],
    "大学数学": ["高等数学：泰勒公式展开技巧", "线性代数：矩阵特征值", "概率论分布"],
    "大学专业课": ["Python数据结构：算法分析", "宏观经济学模型", "管理学SWOT分析"]
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

# --- 3. 配置 ---
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
WORDPRESS_URL = os.getenv('WORDPRESS_URL').rstrip('/')
WORDPRESS_USER = os.getenv('WORDPRESS_USER')
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD')

# --- 4. 核心功能函数 ---

def upload_media_reliable(category, title):
    """解决媒体库白块问题：确保获取真实的图片二进制流"""
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    try:
        # 使用更稳健的图片源，通过 API 直接获取
        img_url = f"https://images.unsplash.com/photo-1503676260728-1c00da094a0b?q=80&w=800&auto=format&fit=crop"
        response = requests.get(img_url, timeout=20)
        
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
    except Exception as e:
        print(f"❌ 图片上传失败: {e}")
        return None, None

def get_zhipu_detailed_content(topic, category):
    """解决内容过短问题：强制 AI 生成长文"""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {"Authorization": f"Bearer {ZHIPU_API_KEY}", "Content-Type": "application/json"}
    
    prompt = f"请以资深教师身份撰写关于《{topic}》的深度解析指南。要求：使用HTML格式(h2,h3,p)，必须包含1.知识讲解、2.重点难点、3.例题分析。字数要求1500字以上。"
    
    data = {
        "model": "glm-4",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8
    }
    try:
        res = requests.post(url, headers=headers, json=data, timeout=60).json()
        return res['choices'][0]['message']['content'].strip()
    except: return None

# --- 5. 发布主逻辑 ---

def post_to_wordpress_final(title, content, category):
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    cat_id = CATEGORY_MAP.get(category, 1)
    
    # 修复图片空白问题
    media_id, img_url = upload_media_reliable(category, title)
    
    # 修复标题重叠与间距问题：注入强力内联样式
    # 通过设置 line-height 和 margin 解决标题重叠
    style_fix = '<style>.entry-content h2, .entry-content h1 { line-height: 1.6 !important; margin-bottom: 20px !important; margin-top: 40px !important; clear: both; } .entry-content p { margin-bottom: 15px; line-height: 1.8; }</style>'
    
    img_html = f'<p style="text-align:center; margin-top:30px;"><img src="{img_url}" alt="{title}" style="border-radius:10px; width:100%; max-width:800px;" /></p>' if img_url else ""
    
    # 每一篇发布的文章末尾都会带上下载模块
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
    
    content = get_zhipu_detailed_content(topic, category)
    if content:
        post_to_wordpress_final(topic, content, category)

if __name__ == "__main__":
    main()
