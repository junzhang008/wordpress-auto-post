import requests
import random
import os
import string
from datetime import datetime
from requests.auth import HTTPBasicAuth
import jieba
import jieba.analyse
import base64
import time
import re

# --- 1. 完整全学段主题库 ---
TOPICS_BY_CATEGORY = {
    # 小学部分
    "一年级数学": ["10以内加减法", "认识图形", "数字的大小比较", "简单的凑十法"],
    "二年级数学": ["乘法口诀记忆", "长度单位换算", "100以内进位加法"],
    "三年级数学": ["分数的初步认识", "两位数乘法技巧", "长方形周长计算"],
    "四年级数学": ["大数的认识", "运算定律简便计算", "三角形内角和"],
    "五年级数学": ["方程初步认识", "多边形的面积计算", "因数与倍数"],
    "六年级数学": ["圆的面积公式推导", "百分数应用题", "比例的性质"],
    "一年级语文": ["拼音字母表", "汉字基础笔画", "看图写话入门"],
    "二年级语文": ["古诗词背诵", "词语接龙游戏", "标点符号用法"],
    "三年级语文": ["段落写作基础", "成语故事积累", "阅读理解入门"],
    "四年级语文": ["作文构思技巧", "修辞手法详解", "文言文小故事"],
    "五年级语文": ["议论文初步", "现代文深度阅读", "文学常识积累"],
    "六年级语文": ["综合写作训练", "古文名篇鉴赏", "毕业感言写作"],
    "一年级英语": ["26个字母发音", "基础问候语", "颜色与数字单词"],
    "二年级英语": ["简单句型练习", "英语儿歌串烧", "动物名称单词"],
    "三年级英语": ["常用动词短语", "一般现在时基础", "自我介绍模版"],
    "四年级英语": ["英语听力入门", "方位介词用法", "描述天气的单词"],
    "五年级英语": ["过去时态讲解", "英语小短文阅读", "比较级与最高级"],
    "六年级英语": ["综合语法复习", "升学面谈英语", "一般将来时用法"],

    # 初中部分 (Junior High)
    "初中数学": ["有理数运算技巧", "一元一次方程应用题", "几何证明题入门", "函数图像性质", "勾股定理应用"],
    "初中语文": ["文言文常词积累", "现代文阅读理解套路", "中考作文素材积累", "名著导读：朝花夕拾"],
    "初中英语": ["一般现在时与过去时区别", "中考核心词汇记忆", "英语听力提分技巧", "完形填空解题套路"],
    "初中物理": ["电路图绘制基础", "浮力计算公式详解", "透镜成像规律", "机械能守恒定律"],
    "初中化学": ["酸碱盐化学性质", "化学方程式配平方法", "实验室制取氧气", "元素周期表快速记忆"],

    # 高中部分 (Senior High)
    "高中数学": ["集合与函数概念", "三角函数恒等变换", "圆锥曲线解题模板", "导数的几何意义", "概率与统计"],
    "高中语文": ["文言文虚词详解", "高考议论文写作逻辑", "古典诗歌鉴赏术语", "先秦散文研究"],
    "高中英语": ["长难句拆解技巧", "高考英语写作高阶词汇", "定语从句全攻略", "虚拟语气用法总结"],
    "高中物理": ["受力分析与牛顿定律", "电磁感应综合题", "动量守恒定律", "天体运动轨道计算"],
    "高中化学": ["有机化学官能团总结", "电化学原电池原理", "物质的量浓度计算", "化学平衡常数应用"],

    # 大学部分 (University)
    "大学数学": ["高等数学：极限与连续", "线性代数：矩阵运算", "概率论：正态分布", "离散数学：图论"],
    "大学英语": ["四六级写作高分模板", "考研英语长难句", "雅思/托福口语备考", "学术论文英语表达"],
    "大学专业课": ["计算机基础：算法分析", "经济学：宏观调控原理", "心理学：认知行为疗法", "管理学：职场沟通技巧"]
}

# --- 2. 配置信息 ---
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
WORDPRESS_URL = os.getenv('WORDPRESS_URL')
WORDPRESS_USER = os.getenv('WORDPRESS_USER')
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD')
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY')

# 分类映射 (已整合您提供的 ID)
CATEGORY_MAP = {
    "一年级数学": 6, "二年级数学": 7, "三年级数学": 8, "四年级数学": 9, 
    "五年级数学": 10, "六年级数学": 11, "一年级语文": 12, "二年级语文": 13, 
    "三年级语文": 14, "四年级语文": 15, "五年级语文": 16, "六年级语文": 17, 
    "一年级英语": 18, "二年级英语": 19, "三年级英语": 20, "四年级英语": 21, 
    "五年级英语": 22, "六年级英语": 23,
    "初中数学": 774, "初中语文": 773, "初中英语": 775, "初中物理": 776, "初中化学": 777,
    "高中数学": 782, "高中语文": 781, "高中英语": 783, "高中物理": 784, "高中化学": 785,
    "大学数学": 790, "大学英语": 789, "大学专业课": 792
}

# 增强的图片关键词映射
TOPIC_IMAGE_KEYWORDS = {
    "数学": ["mathematics", "calculation", "geometry", "formula", "logic"],
    "语文": ["literature", "reading", "writing", "book", "culture"],
    "英语": ["english", "learning", "international", "alphabet", "vocabulary"],
    "小学": ["children", "basic", "playful", "cartoon", "education"],
    "初中": ["student", "classroom", "study", "science", "library"],
    "高中": ["high school", "exam", "thinking", "focus", "academic"],
    "大学": ["university", "professional", "research", "campus", "advanced"]
}

ARTICLE_ANGLES = {
    "数学": ["实用解题技巧", "常见错误分析", "思维训练方法", "知识点深度解析"],
    "语文": ["阅读方法指导", "写作技巧分享", "古诗词鉴赏", "阅读理解策略"],
    "英语": ["单词记忆技巧", "语法学习策略", "听力训练方法", "写作技巧指导"],
    "物理": ["实验过程解析", "公式推导逻辑", "经典错题研究", "核心概念讲解"],
    "化学": ["反应原理分析", "实验安全指南", "周期律深度研究", "物质结构解析"],
    "专业课": ["核心理论解析", "行业应用前景", "学术前沿动态", "实战案例分析"]
}

IMAGE_TYPES = ["概念图解", "实例演示", "步骤说明", "对比分析", "应用场景", "趣味插图", "知识总结", "思维导图"]
TAG_CACHE = {}

# --- 3. 辅助功能函数 ---

def generate_random_slug(length=8):
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_smart_tags(category, content, title):
    tags = set()
    grade_tag = "大学" if "大学" in category else category[:2]
    subject_tag = category[2:] if "大学" not in category else category[2:]
    
    tags.add(grade_tag)
    tags.add(subject_tag)
    
    # 提取内容关键词
    try:
        keywords = jieba.analyse.extract_tags(content, topK=6)
        tags.update(keywords)
    except:
        pass
    
    final_tags = [t for t in tags if 2 <= len(t) <= 8][:10]
    return final_tags

def get_or_create_tag(tag_name):
    global TAG_CACHE
    if tag_name in TAG_CACHE: return TAG_CACHE[tag_name]
    try:
        api_url = f"{WORDPRESS_URL.rstrip('/')}/wp-json/wp/v2/tags"
        auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
        search_res = requests.get(f"{api_url}?search={tag_name}", auth=auth, timeout=10).json()
        for t in search_res:
            if t['name'] == tag_name:
                TAG_CACHE[tag_name] = t['id']
                return t['id']
        res = requests.post(api_url, json={'name': tag_name, 'slug': tag_name}, auth=auth, timeout=10).json()
        TAG_CACHE[tag_name] = res['id']
        return res['id']
    except:
        return None

def get_image_keywords(category, topic, image_type):
    keywords = []
    if "大学" in category: level = "大学"
    elif "高中" in category: level = "高中"
    elif "初中" in category: level = "初中"
    else: level = "小学"
    
    subject = "数学" if "数学" in category else ("语文" if "语文" in category else "英语")
    keywords.extend(TOPIC_IMAGE_KEYWORDS.get(level, []))
    keywords.extend(TOPIC_IMAGE_KEYWORDS.get(subject, []))
    return list(set(keywords))[:5]

def get_unsplash_image(keywords):
    if not UNSPLASH_ACCESS_KEY: return None
    try:
        url = "https://api.unsplash.com/photos/random"
        res = requests.get(url, params={"query": " ".join(keywords), "orientation": "landscape"}, 
                           headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}, timeout=10)
        return res.json()['urls']['regular'] if res.status_code == 200 else None
    except: return None

def upload_image_to_wordpress(image_url, title):
    try:
        img_res = requests.get(image_url, timeout=15)
        auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
        res = requests.post(f"{WORDPRESS_URL.rstrip('/')}/wp-json/wp/v2/media",
                            headers={'Content-Disposition': f'attachment; filename={generate_random_slug()}.jpg', 'Content-Type': 'image/jpeg'},
                            data=img_res.content, auth=auth, timeout=30)
        return res.json()['id'] if res.status_code == 201 else None
    except: return None

# --- 4. 核心 AI 内容生成逻辑 (增加全学段身份识别) ---

def get_zhipu_ai_content(topic, category, angle):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {"Authorization": f"Bearer {ZHIPU_API_KEY}", "Content-Type": "application/json"}
    
    # 动态调整身份和字数要求
    if "大学" in category:
        identity, audience, word_limit = "大学教授", "大学生", "1800-2200"
    elif "高中" in category:
        identity, audience, word_limit = "高中特级教师", "高中生", "1500-1800"
    elif "初中" in category:
        identity, audience, word_limit = "资深初中教研员", "初中生", "1300-1600"
    else:
        identity, audience, word_limit = "经验丰富的小学教师", "小学生及家长", "1000-1300"

    prompt = f"""
    请以{identity}的身份，为{audience}撰写一篇关于'{topic}'的深度解析文章。
    切入角度：{angle}。
    要求：
    1. 专业性强，语言风格符合{audience}的认知水平。
    2. 包含核心知识点讲解、经典案例、常见误区及学习建议。
    3. 字数要求：{word_limit}字。
    4. 使用 HTML 格式排版（h2, h3, p 标签）。
    5. 在文章中自然穿插 [图片1], [图片2] 占位符。
    """
    
    data = {
        "model": "glm-4",
        "messages": [{"role": "system", "content": f"你是一位擅长{category}教学的专家。"}, {"role": "user", "content": prompt}]
    }
    try:
        res = requests.post(url, headers=headers, json=data, timeout=60)
        return res.json()['choices'][0]['message']['content'].strip() if res.status_code == 200 else None
    except: return None

# --- 5. 发布功能 ---

def post_to_wordpress(title, content, category, slug):
    api_url = f"{WORDPRESS_URL.rstrip('/')}/wp-json/wp/v2/posts"
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    category_id = CATEGORY_MAP.get(category, 1)
    
    tag_names = generate_smart_tags(category, content, title)
    tag_ids = [get_or_create_tag(n) for n in tag_names if get_or_create_tag(n)]

    post_data = {
        'title': title,
        'content': content,
        'status': 'publish',
        'categories': [category_id],
        'tags': tag_ids,
        'slug': slug,
        # 自动插入下载框需要的自定义字段
        'meta': {
            'download_link': 'https://www.gogewu.com/download-center/',
            'download_code': '8888'
        }
    }
    
    res = requests.post(api_url, json=post_data, auth=auth, timeout=30)
    if res.status_code == 201:
        post_id = res.json()['id']
        print(f"✅ 文章发布成功 ID: {post_id}")
        
        # 处理图片
        img_url = get_unsplash_image(get_image_keywords(category, title, "特色图"))
        if img_url:
            media_id = upload_image_to_wordpress(img_url, title)
            if media_id:
                requests.post(f"{api_url}/{post_id}", json={'featured_media': media_id}, auth=auth)
                print("🖼️  特色图片已设置")
        return True
    return False

def main():
    print(f"🚀 开始执行发布任务: {datetime.now()}")
    jieba.initialize()
    
    # 随机选择学段和主题
    category = random.choice(list(TOPICS_BY_CATEGORY.keys()))
    topic = random.choice(TOPICS_BY_CATEGORY[category])
    
    # 获取学科关键字用于匹配角度
    subject = "数学" if "数学" in category else ("语文" if "语文" in category else ("英语" if "英语" in category else "专业课"))
    angle = random.choice(ARTICLE_ANGLES.get(subject, ["深度解析"]))
    
    print(f"📝 选定主题: {category} -> {topic} (角度: {angle})")
    
    content = get_zhipu_ai_content(topic, category, angle)
    if content:
        slug = generate_random_slug(10)
        post_to_wordpress(topic, content, category, slug)
    else:
        print("❌ AI 内容生成失败")

if __name__ == "__main__":
    main()
