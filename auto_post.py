import requests
import random
import os
import string
from requests.auth import HTTPBasicAuth

# --- 1. 海量主题库 (涵盖小初高大) ---
TOPICS = {
    "小学": {
        "一年级语文": ["拼音字母表背诵技巧", "看图写话基本句式", "常用汉字笔顺规范"],
        "三年级数学": ["两位数乘法口算卡", "认识周长与面积", "分数的初步认识"],
        "六年级英语": ["一般过去时用法总结", "小学必背100个单词", "英文自我介绍模板"]
    },
    "初中": {
        "初中物理": ["浮力计算公式大全", "电路图画法详解", "凸透镜成像规律"],
        "初中数学": ["全等三角形证明题", "一元二次方程根的判别式", "勾股定理应用题"],
        "初中化学": ["元素周期表记忆口诀", "实验室制取氧气步骤", "物质的鉴别与推断"]
    },
    "高中": {
        "高中数学": ["圆锥曲线离心率公式", "导数在极值中的应用", "三角函数诱导公式全集"],
        "高中英语": ["高考英语作文万能模板", "定语从句易错点分析", "虚拟语气核心用法"],
        "高中生物": ["减数分裂过程图解", "遗传因子杂交实验", "光合作用过程详解"]
    },
    "大学": {
        "高等数学": ["泰勒公式深度解析", "拉格朗日中值定理证明", "多重积分计算技巧"],
        "考研英语": ["考研英语翻译长难句", "50个核心超纲词汇", "阅读理解解题逻辑"],
        "专业课": ["Python数据结构：链表", "宏观经济IS-LM模型", "管理学SWOT分析法"]
    }
}

# --- 2. 基础配置 ---
ZHIPU_API_KEY = "你的智谱APIKey"
WP_URL = "https://www.gogewu.com/wp-json/wp/v2"
WP_USER = "你的用户名"
WP_APP_PASSWORD = "你的应用密码(不是登录密码)"

# 对应你网站后台的分类ID
CAT_MAP = {"小学": 6, "初中": 774, "高中": 782, "大学": 790}

# --- 3. 增强功能函数 ---

def upload_media_from_unsplash(keyword, title):
    """直接从Unsplash抓取并上传到WP媒体库，返回ID和URL"""
    try:
        # 使用更精准的教育类关键词
        img_url = f"https://source.unsplash.com/featured/800x450?education,{keyword}"
        response = requests.get(img_url, timeout=15)
        auth = HTTPBasicAuth(WP_USER, WP_APP_PASSWORD)
        
        files = {
            'file': (f"{title}.jpg", response.content, 'image/jpeg')
        }
        res = requests.post(f"{WP_URL}/media", files=files, auth=auth)
        if res.status_code == 201:
            return res.json()['id'], res.json()['source_url']
    except:
        return None, None

def get_ai_content(topic):
    """AI生成内容"""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {"Authorization": f"Bearer {ZHIPU_API_KEY}"}
    prompt = f"你是一位资深教师，请写一篇关于《{topic}》的深度教学文章。要求：使用HTML格式，包含h2, h3, p标签，字数1500字以上，逻辑严密。"
    data = {
        "model": "glm-4",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    res = requests.post(url, headers=headers, json=data).json()
    return res['choices'][0]['message']['content']

# --- 4. 发布逻辑 ---

def auto_post():
    # 随机选一个学段和主题
    grade = random.choice(list(TOPICS.keys()))
    subject = random.choice(list(TOPICS[grade].keys()))
    topic = random.choice(TOPICS[grade][subject])
    
    print(f"🚀 正在准备: {grade} - {topic}")
    
    # 1. 获取内容
    content = get_ai_content(topic)
    
    # 2. 获取并上传图片 (缩略图)
    media_id, media_url = upload_media_from_unsplash(subject, topic)
    
    # 3. 修复间距 + 注入文中图片
    # 在内容最前面注入 CSS 样式，解决标题间距问题
    style_fix = '<style>.entry-header { margin-bottom: 5px !important; } .entry-content h2 { margin-top: 10px !important; }</style>'
    
    # 强行在正文第一段后面插入一张图片，确保“文中一定有图”
    if media_url:
        img_html = f'<p style="text-align:center;"><img src="{media_url}" alt="{topic}" style="border-radius:10px;"/></p>'
        content = style_fix + img_html + content
    
    # 4. 发布文章
    post_data = {
        'title': f"【{subject}】{topic}深度解析与学习资料",
        'content': content,
        'status': 'publish',
        'categories': [CAT_MAP.get(grade, 1)],
        'featured_media': media_id if media_id else 0,
        # 必须匹配 functions.php 中的字段名
        'meta': {
            'download_link': 'https://www.gogewu.com/download-center/',
            'download_code': '8888'
        }
    }
    
    auth = HTTPBasicAuth(WP_USER, WP_APP_PASSWORD)
    res = requests.post(f"{WP_URL}/posts", json=post_data, auth=auth)
    
    if res.status_code == 201:
        print(f"✅ 成功发布文章！ID: {res.json()['id']}")
    else:
        print(f"❌ 发布失败: {res.text}")

if __name__ == "__main__":
    auto_post()
