import requests
import random
import os
import string
from requests.auth import HTTPBasicAuth

# --- 1. 海量主题库 (涵盖小初高大全学科) ---
TOPICS = {
    "小学": {
        "语文": ["一年级拼音快速记忆法", "看图写话万能句式", "必备古诗词解析"],
        "数学": ["凑十法与破十法图解", "三年级几何周长计算", "简便运算定律总结"],
        "英语": ["自然拼读核心规则", "日常问候常用语", "小学语法：名词复数"]
    },
    "初中": {
        "物理": ["初二物理：浮力计算实验", "电路图画法详解", "凸透镜成像规律总结"],
        "数学": ["全等三角形判定定理", "勾股定理应用题", "一元二次方程求根公式"],
        "化学": ["实验室制取氧气步骤", "元素周期表速记口诀", "常用化学方程式配平"]
    },
    "高中": {
        "数学": ["圆锥曲线离心率求解模板", "导数单调性研究", "三角函数诱导公式全解"],
        "物理": ["牛顿第二定律综合应用", "电磁感应楞次定律", "动量守恒定律解析"],
        "化学": ["有机官能团化学性质", "电化学原电池原理", "物质的量浓度计算"]
    },
    "大学": {
        "高等数学": ["微积分：泰勒公式展开", "拉格朗日中值定理证明", "多元函数偏导数计算"],
        "专业课": ["Python数据结构：平衡二叉树", "宏观经济IS-LM模型分析", "法学：民法典核心解读"],
        "考研英语": ["考研长难句拆解技巧", "英语一写作高分模板", "核心词汇词根词缀法"]
    }
}

# --- 2. 基础配置 ---
# 确保环境变量或字符串中没有中文字符
ZHIPU_API_KEY = str(os.getenv('ZHIPU_API_KEY', "你的APIKey")).strip()
WORDPRESS_URL = "https://www.gogewu.com/wp-json/wp/v2"
WORDPRESS_USER = "你的用户名"
WORDPRESS_PASSWORD = "你的应用密码"

# 对应 ID
CATEGORY_MAP = {"小学": 6, "初中": 774, "高中": 782, "大学": 790}

# --- 3. 增强功能函数 ---

def upload_media(keyword, title):
    """抓取 Unsplash 图片并上传至媒体库"""
    try:
        # 强制使用英文关键词避免编码错误
        search_kw = "education,study,school" 
        img_url = f"https://source.unsplash.com/featured/800x450?{search_kw}"
        response = requests.get(img_url, timeout=20)
        auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
        
        # 准备上传
        files = {'file': (f"{generate_random_slug()}.jpg", response.content, 'image/jpeg')}
        res = requests.post(f"{WORDPRESS_URL}/media", files=files, auth=auth, timeout=30)
        if res.status_code == 201:
            data = res.json()
            return data['id'], data['source_url']
    except Exception as e:
        print(f"图片上传失败: {e}")
    return None, None

def generate_random_slug(length=10):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

def get_ai_content(topic, level_name):
    """AI生成内容 - 修复编码报错关键点"""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    
    # 修复核心：确保 Authorization 头不包含任何非 ASCII 字符
    api_key_clean = ZHIPU_API_KEY.encode('ascii', 'ignore').decode('ascii')
    headers = {
        "Authorization": f"Bearer {api_key_clean}",
        "Content-Type": "application/json"
    }
    
    prompt = f"请以资深教师身份写一篇《{topic}》的专业文章。要求：HTML格式，包含h2, h3, p标签，1500字以上。内容要有深度，适合{level_name}阶段学生。"
    
    data = {
        "model": "glm-4",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8
    }
    
    try:
        res = requests.post(url, headers=headers, json=data, timeout=60)
        res.raise_for_status()
        return res.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"AI 生成报错: {e}")
        return None

# --- 4. 发布主逻辑 ---

def auto_post():
    # 随机选择学科
    level_name = random.choice(list(TOPICS.keys()))
    subject_name = random.choice(list(TOPICS[level_name].keys()))
    topic = random.choice(TOPICS[level_name][subject_name])
    
    print(f"🚀 正在准备: {level_name} - {topic}")

    content = get_ai_content(topic, level_name)
    if not content: return

    # 上传图片
    media_id, media_url = upload_media(subject_name, topic)

    # 修复间距：注入 CSS
    # 直接在内容开头强制注入 CSS 压低标题与正文间距
    style_fix = '<style>.entry-content { margin-top: -30px !important; } h2, h3 { margin-top: 15px !important; }</style>'
    
    # 强制在文中第一段后插入图片，确保文中一定有图
    if media_url:
        img_html = f'<p style="text-align:center;"><img src="{media_url}" alt="{topic}" style="border-radius:12px; max-width:100%;" /></p>'
        content = style_fix + img_html + content
    else:
        content = style_fix + content

    post_data = {
        'title': f"【{subject_name}】{topic}",
        'content': content,
        'status': 'publish',
        'categories': [CATEGORY_MAP.get(level_name, 1)],
        'featured_media': media_id if media_id else 0,
        'slug': generate_random_slug(),
        'meta': {
            'download_link': 'https://www.gogewu.com/download-center/',
            'download_code': '8888'
        }
    }

    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    response = requests.post(f"{WORDPRESS_URL}/posts", json=post_data, auth=auth, timeout=30)
    
    if response.status_code == 201:
        print(f"✅ 发布成功！文章ID: {response.json()['id']}")
    else:
        print(f"❌ 发布失败: {response.text}")

if __name__ == "__main__":
    auto_post()
