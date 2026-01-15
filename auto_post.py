import requests
import random
import os
import string
from datetime import datetime
from requests.auth import HTTPBasicAuth
import jieba
import jieba.analyse
import time
import re

# ================= 配置区域 =================

# 🔑 1. 英伟达 API Key
NVIDIA_API_KEY = os.getenv('NVIDIA_API_KEY') 

# 🔑 2. Pexels API Key
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')

# 🔑 3. WordPress 配置
WORDPRESS_URL = os.getenv('WORDPRESS_URL')
WORDPRESS_USER = os.getenv('WORDPRESS_USER')
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD')

# 分类映射
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

# 完整主题库
TOPICS_BY_CATEGORY = {
    # 小学部分
    "一年级数学": ["10以内加减法", "认识数字1-100", "简单图形识别", "数字大小比较", "认识钟表时间"],
    "二年级数学": ["乘法口诀记忆", "100以内加减法", "认识时间", "长度单位换算", "人民币的认识"],
    "三年级数学": ["万以内数的认识", "两位数乘法", "小数初步认识", "分数的初步认识", "长方形和正方形"],
    "四年级数学": ["大数的认识", "小数运算", "几何图形", "三角形和四边形", "运算定律应用"],
    "五年级数学": ["分数运算", "方程初步", "立体图形", "多边形的面积", "因数与倍数"],
    "六年级数学": ["比例应用", "圆的面积", "统计图表", "圆柱与圆锥", "正比例反比例"],
    "一年级语文": ["拼音学习", "汉字书写", "简单阅读", "词语积累", "句子练习"],
    "二年级语文": ["词语积累", "句子练习", "短文阅读", "标点符号使用", "修辞手法入门"],
    "三年级语文": ["段落写作", "阅读理解", "古诗词", "成语运用", "修辞手法应用"],
    "四年级语文": ["作文指导", "文言文入门", "修辞手法", "阅读理解技巧", "古诗词鉴赏"],
    "五年级语文": ["议论文基础", "文学欣赏", "写作技巧", "古文阅读", "现代文阅读"],
    "六年级语文": ["综合写作", "古文阅读", "文学常识", "阅读理解", "作文表达"],
    "一年级英语": ["字母学习", "简单单词", "基础对话", "英语儿歌", "日常用语"],
    "二年级英语": ["单词记忆", "简单句型", "英语儿歌", "日常对话", "情景英语"],
    "三年级英语": ["语法入门", "阅读理解", "英语写作", "英语对话", "英语短文"],
    "四年级英语": ["时态学习", "阅读提升", "口语练习", "英语写作", "英语听力"],
    "五年级英语": ["复合句学习", "阅读策略", "写作训练", "英语语法", "英语阅读"],
    "六年级英语": ["语法综合", "阅读进阶", "应试准备", "英语写作", "英语口语"],
    
    # 初中部分
    "初中数学": ["代数基础运算", "一元一次方程", "平面几何入门", "函数初步概念", "三角形与全等"],
    "初中语文": ["文言文阅读技巧", "现代文阅读方法", "作文结构训练", "古诗词鉴赏", "修辞手法应用"],
    "初中英语": ["时态综合运用", "复合句语法", "阅读理解技巧", "英语写作训练", "听力提升方法"],
    "初中物理": ["力学基础知识", "声学现象解析", "光学基本原理", "热学基础概念", "电学入门知识"],
    "初中化学": ["化学元素认识", "化学反应基础", "化学实验安全", "化学方程式", "物质分类方法"],
    
    # 高中部分
    "高中数学": ["函数与导数", "三角函数应用", "立体几何", "解析几何", "数列与数学归纳法"],
    "高中语文": ["古诗文深度解读", "现代文阅读进阶", "议论文写作技巧", "文学类文本阅读", "语言运用技巧"],
    "高中英语": ["长难句分析", "完形填空技巧", "阅读理解进阶", "写作能力提升", "听力理解训练"],
    "高中物理": ["牛顿力学深入", "电磁学原理", "热力学定律", "光学深入", "近代物理基础"],
    "高中化学": ["有机化学基础", "化学反应原理", "物质结构与性质", "化学平衡", "电化学基础"],
    
    # 大学部分
    "大学数学": ["高等数学基础", "线性代数", "概率论与数理统计", "微积分应用", "数学分析入门"],
    "大学英语": ["学术英语写作", "英语听说进阶", "跨文化交际", "专业英语阅读", "英语演讲技巧"],
    "大学专业课": ["专业基础理论", "专业核心知识", "专业实践应用", "专业前沿发展", "专业研究方法"]
}

# 文章角度库
ARTICLE_ANGLES = {
    "数学": ["实用解题技巧", "常见错误分析", "思维训练方法", "生活应用实例", "趣味数学游戏", "考试重点解析"],
    "语文": ["阅读方法指导", "写作技巧分享", "文学欣赏方法", "语言表达训练", "传统文化学习", "阅读理解策略"],
    "英语": ["口语练习方法", "单词记忆技巧", "语法学习策略", "听力训练方法", "阅读能力提升", "写作技巧指导"],
    "物理": ["实验操作方法", "物理原理应用", "问题解决方法", "思维训练方法", "物理模型建立", "物理公式推导"],
    "化学": ["实验安全操作", "化学反应原理", "化学计算技巧", "化学思维方法", "物质性质分析", "化学实验设计"],
    "专业课": ["专业基础理论", "专业实践应用", "专业学习方法", "专业前沿动态", "专业技能训练", "专业思维培养"]
}

# 标签缓存
TAG_CACHE = {}
# 图片缓存
USED_IMAGES_CACHE = {'session': set()}

def generate_random_slug(length=8):
    """生成随机别名"""
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def select_topic_and_angle():
    """智能选择主题和角度"""
    all_categories = list(TOPICS_BY_CATEGORY.keys())
    
    # 计算各学段分类
    primary_categories = [c for c in all_categories if "一年级" in c or "二年级" in c or "三年级" in c or "四年级" in c or "五年级" in c or "六年级" in c]
    middle_categories = [c for c in all_categories if "初中" in c]
    high_categories = [c for c in all_categories if "高中" in c]
    university_categories = [c for c in all_categories if "大学" in c]
    
    print(f"📊 分类统计:")
    print(f"  小学分类: {len(primary_categories)}个")
    print(f"  初中分类: {len(middle_categories)}个")
    print(f"  高中分类: {len(high_categories)}个")
    print(f"  大学分类: {len(university_categories)}个")
    
    # 创建加权选择列表
    all_categories_groups = [primary_categories, middle_categories, high_categories, university_categories]
    valid_groups = [group for group in all_categories_groups if group]
    
    if not valid_groups:
        return "未知分类", "未知主题", "未知角度"
    
    # 随机选择一个学段
    selected_group = random.choice(valid_groups)
    category = random.choice(selected_group)
    
    # 从该分类中选择主题
    if category in TOPICS_BY_CATEGORY and TOPICS_BY_CATEGORY[category]:
        base_topic = random.choice(TOPICS_BY_CATEGORY[category])
    else:
        base_topic = f"{category}学习资料"
    
    # 根据科目选择角度
    if "初中" in category or "高中" in category or "大学" in category:
        if "初中" in category:
            subject = category[2:]
        elif "高中" in category:
            subject = category[2:]
        else:  # 大学
            subject = category[2:]
    else:
        subject = category[3:]
    
    if subject in ARTICLE_ANGLES:
        angle = random.choice(ARTICLE_ANGLES[subject])
    else:
        angle_list = ["学习方法指导", "知识深度解析", "实践应用案例", "考试重点解析"]
        angle = random.choice(angle_list)
    
    return category, base_topic, angle

def generate_diverse_title(base_topic, category, angle):
    """生成多样化的随机标题"""
    # 提取年级和科目
    if "初中" in category or "高中" in category or "大学" in category:
        if "初中" in category:
            grade = "初中"
            subject = category[2:]
        elif "高中" in category:
            grade = "高中"
            subject = category[2:]
        else:  # 大学
            grade = "大学"
            subject = category[2:]
    else:
        grade = "小学"
        subject = category[3:]
    
    title_templates = [
        f"{base_topic}的{angle}详解",
        f"{grade}{subject}：{base_topic}的{angle}解析",
        f"掌握{base_topic}的{angle}方法",
        f"如何高效学习{base_topic}？{angle}全解析",
        f"{base_topic}学习中的{angle}技巧",
        f"解决{base_topic}学习难题的{angle}策略",
        f"{base_topic}在实际应用中的{angle}分析",
        f"{angle}视角下的{base_topic}学习",
        f"{base_topic}的{angle}实战演练",
        f"备战{grade}考试：{base_topic}的{angle}重点",
        f"{base_topic}考点解析：{angle}应用",
        f"考试必备：{base_topic}的{angle}技巧",
        f"深入理解{base_topic}：{angle}深度解析",
        f"{base_topic}的核心{angle}探究",
        f"{angle}在{base_topic}学习中的关键作用",
        f"{grade}生必看：{base_topic}的{angle}指导",
        f"从零开始掌握{base_topic}的{angle}",
        f"{base_topic}学习方法：{angle}全攻略",
        f"轻松学习{base_topic}：{angle}趣味解析",
        f"发现{base_topic}的乐趣：{angle}探索",
        f"有趣有料的{base_topic}：{angle}讲解",
        f"全面提升{base_topic}能力：{angle}综合训练",
        f"{base_topic}学习进阶：{angle}深度训练",
        f"{angle}驱动下的{base_topic}学习提升",
        f"{base_topic}经典案例：{angle}分析",
        f"从案例看{base_topic}的{angle}应用",
        f"{base_topic}实例解析：{angle}实战",
        f"{base_topic}与传统学习方法的{angle}对比",
        f"{angle}对比分析：不同{base_topic}学习方法",
        f"{base_topic}学习新视角：{angle}对比研究"
    ]
    
    title = random.choice(title_templates)
    
    title_length = len(title)
    if title_length < 10:
        prefixes = ["深度解析：", "详细讲解：", "完全掌握：", "高效学习："]
        title = random.choice(prefixes) + title
    elif title_length > 30:
        title_words = list(title)
        if len(title_words) > 30:
            for i in range(30, 0, -1):
                if title_words[i] in ['，', '：', '、', '；', '，', '。']:
                    title = ''.join(title_words[:i+1])
                    break
            else:
                title = ''.join(title_words[:30]) + "..."
    
    print(f"📝 生成多样化标题: {title} (长度: {len(title)}字)")
    return title

def get_nvidia_ai_content(topic, category, angle):
    """使用 NVIDIA API 生成内容"""
    if not NVIDIA_API_KEY:
        print("❌ NVIDIA API密钥未设置")
        return None, None
        
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    if "初中" in category or "高中" in category or "大学" in category:
        if "初中" in category:
            grade = "初中"
            subject = category[2:]
        elif "高中" in category:
            grade = "高中"
            subject = category[2:]
        else:  # 大学
            grade = "大学"
            subject = category[2:]
        student_type = f"{grade}学生"
    else:
        grade = category[:3]
        subject = category[3:]
        student_type = f"{grade}学生和家长"
    
    diverse_title = generate_diverse_title(topic, category, angle)
    
    # 🌟🌟🌟 重点修改的提示词：禁止重复标题，禁止总结，禁止格式化 🌟🌟🌟
    prompt = f"""
请以专业教师的身份，为{student_type}写一篇关于'{topic}'的文章。

**核心指令：**
1. **直接开始正文**：不要在文章开头重复写标题，不要写“你好”、“这篇文章将...”等开场白。
2. **禁止使用“总结”字样**：文章结尾不要使用“总结”、“结语”、“综上所述”等小标题，要自然收尾。
3. **拒绝格式化语言**：不要使用机械的列表（如“首先、其次、最后”），使用更自然、口语化的第一人称（我）进行叙述，像老师面对面交谈。
4. **内容专业**：字数2000字以上，包含核心知识、具体例子、练习题思路。
5. **纯HTML输出**：使用 <h2>, <h3>, <p>, <ul>, <li>, <strong> 标签。

**文章主题：** {diverse_title}
**切入角度：** {angle}

请直接开始写作：
    """
    
    data = {
        "model": "meta/llama-3.1-70b-instruct",
        "messages": [
            {
                "role": "system", 
                "content": f"你是一个经验丰富的{grade}教师。写作风格亲切自然，避免AI味。请直接输出HTML代码，不要包含Markdown标记，不要在开头重复标题。"
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "temperature": 0.8, # 稍微调高温度，增加多样性
        "top_p": 0.9,
        "max_tokens": 4000,
    }
    
    try:
        print(f"🤖 正在调用 NVIDIA AI 生成内容...")
        response = requests.post(url, headers=headers, json=data, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            
            # 清理 Markdown 代码块
            content = re.sub(r'^```html\s*', '', content, flags=re.IGNORECASE)
            content = re.sub(r'^```\s*', '', content)
            content = re.sub(r'\s*```$', '', content)
            
            # 🌟 后处理：强制移除可能存在的标题（如果AI不听话）
            clean_title = diverse_title.replace("?", "\\?").replace("(", "\\(").replace(")", "\\)")
            content = re.sub(f"^\s*<h1>{clean_title}</h1>", "", content, flags=re.IGNORECASE)
            content = re.sub(f"^\s*<h2>{clean_title}</h2>", "", content, flags=re.IGNORECASE)
            content = re.sub(f"^\s*{clean_title}", "", content, flags=re.IGNORECASE)

            # 🌟 后处理：移除“总结”字样的小标题
            content = re.sub(r"<h2>(总结|结语|综上所述).*?</h2>", "<h2>学习心得与建议</h2>", content)

            content_length = len(content)
            print(f"✅ AI生成内容长度: {content_length}字符")
            
            if content_length < 1000:
                print(f"⚠️  警告：生成的内容可能不完整，只有{content_length}字符")
            
            return diverse_title, content
        else:
            print(f"❌ API请求失败: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ AI生成失败: {e}")
        return None, None

def retry_ai_generation(topic, category, angle, max_retries=2):
    """重试AI生成"""
    for attempt in range(max_retries + 1):
        print(f"🔄 第{attempt+1}次尝试生成内容...")
        diverse_title, content = get_nvidia_ai_content(topic, category, angle)
        
        if content and len(content) > 1500:
            print(f"✅ 第{attempt+1}次尝试成功")
            return diverse_title, content
        elif content:
            print(f"⚠️  内容过短，重试...")
            time.sleep(2)
        else:
            print(f"❌ 失败，重试...")
            time.sleep(2)
    
    return diverse_title, content

def generate_smart_tags(category, content, title):
    """生成智能标签"""
    tags = set()
    
    if "初中" in category or "高中" in category or "大学" in category:
        if "初中" in category:
            tags.add("初中")
            subject = category[2:]
        elif "高中" in category:
            tags.add("高中")
            subject = category[2:]
        else:
            tags.add("大学")
            subject = category[2:]
        tags.add(subject)
    else:
        grade = category[:3]
        subject = category[3:]
        tags.add(grade)
        tags.add(subject)
    
    try:
        keywords = jieba.analyse.extract_tags(content, topK=4, withWeight=False, allowPOS=('n', 'vn', 'v', 'a'))
        filtered_keywords = [word for word in keywords if len(word) >= 2 and len(word) <= 6 and not word.isdigit()]
        tags.update(filtered_keywords[:4])
    except:
        pass
    
    # 随机排序并限制数量
    final_tags = list(tags)
    random.shuffle(final_tags)
    final_tags = final_tags[:random.randint(6, 10)]
    
    print(f"🏷️  标签: {final_tags}")
    return final_tags

def get_or_create_tag(tag_name):
    """获取或创建标签"""
    global TAG_CACHE
    if tag_name in TAG_CACHE: return TAG_CACHE[tag_name]
    
    try:
        api_url = WORDPRESS_URL.rstrip('/') + '/wp-json/wp/v2/tags'
        auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
        
        # 搜索
        response = requests.get(f"{api_url}?search={tag_name}", auth=auth, timeout=10)
        if response.status_code == 200:
            for tag in response.json():
                if tag['name'] == tag_name:
                    TAG_CACHE[tag_name] = tag['id']
                    return tag['id']
        
        # 创建
        response = requests.post(api_url, json={'name': tag_name}, auth=auth, timeout=10)
        if response.status_code == 201:
            tag_id = response.json()['id']
            TAG_CACHE[tag_name] = tag_id
            return tag_id
            
    except Exception:
        return None
    return None

def get_tag_ids(tag_names):
    tag_ids = []
    for tag_name in tag_names:
        tag_id = get_or_create_tag(tag_name)
        if tag_id: tag_ids.append(tag_id)
    return tag_ids

def generate_complete_seo_data(title, content, tags, category):
    """生成SEO数据"""
    try:
        plain_text = re.sub(r'<[^>]+>', '', content).strip()
        seo_desc = plain_text[:150] + "..." if len(plain_text) > 150 else plain_text
        focus_kw = tags[0] if tags else title
        
        return {
            "_yoast_wpseo_title": title,
            "_yoast_wpseo_metadesc": seo_desc,
            "_yoast_wpseo_focuskw": focus_kw
        }
    except:
        return None

def get_pexels_image(query):
    """从 Pexels 获取图片"""
    if not PEXELS_API_KEY: return None
        
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 15, "locale": "zh-CN"} # per_page 设大一点避免重复
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['photos']:
                return random.choice(data['photos'])['src']['large']
    except Exception as e:
        print(f"⚠️ Pexels 搜索失败: {e}")
    return None

def upload_image_to_wordpress(image_url, title, alt_text=""):
    """上传图片"""
    try:
        response = requests.get(image_url, timeout=15)
        if response.status_code != 200: return None
        
        upload_url = WORDPRESS_URL.rstrip('/') + '/wp-json/wp/v2/media'
        auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
        filename = f"{generate_random_slug(10)}.jpg"
        
        headers = {
            'Content-Disposition': f'attachment; filename={filename}',
            'Content-Type': 'image/jpeg'
        }
        
        res = requests.post(upload_url, headers=headers, data=response.content, auth=auth, timeout=30)
        
        if res.status_code == 201:
            media_data = res.json()
            return {
                'media_id': media_data['id'],
                'media_url': media_data.get('source_url'),
                'alt_text': alt_text or title,
                'caption': title
            }
    except Exception:
        pass
    return None

def add_featured_image(post_id, media_id):
    try:
        url = f"{WORDPRESS_URL.rstrip('/')}/wp-json/wp/v2/posts/{post_id}"
        requests.post(url, json={'featured_media': media_id}, auth=HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD), timeout=10)
    except: pass

def insert_images_into_content(content, images_data):
    if not images_data: return content
    
    image_template = '''
<div class="article-image" style="margin: 20px 0; text-align: center;">
    <img src="{image_url}" alt="{alt_text}" style="max-width: 100%; height: auto; border-radius: 8px;">
    <p style="text-align: center; color: #666; font-size: 14px;">{caption}</p>
</div>
'''
    paragraphs = re.split(r'(</p>)', content)
    content_with_images = ""
    img_idx = 0
    
    # 每隔 4 个段落插一张图
    p_count = 0
    for part in paragraphs:
        content_with_images += part
        if part == "</p>":
            p_count += 1
            if p_count % 4 == 0 and img_idx < len(images_data):
                img = images_data[img_idx]
                content_with_images += image_template.format(
                    image_url=img['media_url'],
                    alt_text=img['alt_text'],
                    caption=img['caption']
                )
                img_idx += 1
                
    return content_with_images

def process_images_for_article(category, topic, content, post_id):
    """处理图片流程"""
    try:
        images_data = []
        used_urls = set()
        
        # 1. 确定搜索关键词 (优先用具体的 Topic，搜不到再用 Category)
        # 清洗 Topic，去掉特殊字符，Pexels 搜索更准
        clean_topic = re.sub(r'[^\w\s]', '', topic)
        
        # 获取 2-3 张图
        for i in range(random.randint(2, 3)):
            # 策略：第一张尝试搜具体的 Topic，后面的搜 Category
            if i == 0:
                query = clean_topic
            else:
                # 提取学科关键词
                if "数学" in category: query = "mathematics education"
                elif "语文" in category: query = "chinese writing study"
                elif "英语" in category: query = "english learning"
                elif "物理" in category: query = "physics experiment"
                elif "化学" in category: query = "chemistry science"
                else: query = "student studying"
            
            img_url = get_pexels_image(query)
            
            # 如果没搜到，兜底用通用词
            if not img_url:
                img_url = get_pexels_image("education book student")
            
            if img_url and img_url not in used_urls:
                used_urls.add(img_url)
                print(f"✅ 找到图片: {query}")
                
                upload_res = upload_image_to_wordpress(img_url, f"{topic}配图{i}", topic)
                if upload_res:
                    images_data.append(upload_res)
                    if i == 0: # 第一张设为特色图
                        add_featured_image(post_id, upload_res['media_id'])
                        
        if images_data:
            return insert_images_into_content(content, images_data), images_data
            
    except Exception as e:
        print(f"❌ 图片处理出错: {e}")
    
    return content, []

def post_to_wordpress_with_complete_seo(title, content, category, slug):
    try:
        api_url = WORDPRESS_URL.rstrip('/') + '/wp-json/wp/v2/posts'
        tag_names = generate_smart_tags(category, content, title)
        tag_ids = get_tag_ids(tag_names)
        category_id = CATEGORY_MAP.get(category, 1)
        seo_data = generate_complete_seo_data(title, content, tag_names, category)
        
        post_data = {
            'title': title,
            'content': content,
            'status': 'draft',
            'categories': [category_id],
            'slug': slug,
            'tags': tag_ids,
            'meta': seo_data
        }
        
        auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
        response = requests.post(api_url, json=post_data, auth=auth, timeout=30)
        
        if response.status_code == 201:
            post_id = response.json()['id']
            print(f"✅ 草稿创建成功 ID: {post_id}")
            
            # 处理图片
            updated_content, _ = process_images_for_article(category, title, content, post_id)
            
            # 发布
            requests.post(f"{api_url}/{post_id}", json={'content': updated_content, 'status': 'publish'}, auth=auth, timeout=10)
            return True, post_id, tag_names
            
    except Exception as e:
        print(f"❌ 发布出错: {e}")
    return False, None, None

def main():
    print("🚀 开始流程...")
    if not all([NVIDIA_API_KEY, WORDPRESS_URL, WORDPRESS_USER, WORDPRESS_PASSWORD, PEXELS_API_KEY]):
        print("❌ 缺少配置")
        return False
    
    category, base_topic, angle = select_topic_and_angle()
    slug = generate_random_slug(8)
    
    print(f"📖 主题: {category} - {base_topic}")
    
    diverse_title, content = retry_ai_generation(base_topic, category, angle)
    
    if content:
        success, post_id, _ = post_to_wordpress_with_complete_seo(diverse_title, content, category, slug)
        if success:
            print(f"🎉 成功! {WORDPRESS_URL.rstrip('/')}/?p={post_id}")
            return True
            
    return False

if __name__ == "__main__":
    main()
