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

# 配置
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
WORDPRESS_URL = os.getenv('WORDPRESS_URL')
WORDPRESS_USER = os.getenv('WORDPRESS_USER')
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD')
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY')

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
    "一年级数学": ["10以内加减法", "认识数字1-100", "简单图形识别", "数字大小比较"],
    "二年级数学": ["乘法口诀记忆", "100以内加减法", "认识时间", "长度单位换算"],
    "三年级数学": ["万以内数的认识", "两位数乘法", "小数初步认识", "分数的初步认识"],
    "四年级数学": ["大数的认识", "小数运算", "几何图形", "三角形和四边形"],
    "五年级数学": ["分数运算", "方程初步", "立体图形", "多边形的面积"],
    "六年级数学": ["比例应用", "圆的面积", "统计图表", "圆柱与圆锥"],
    "一年级语文": ["拼音学习", "汉字书写", "简单阅读", "词语积累"],
    "二年级语文": ["词语积累", "句子练习", "短文阅读", "标点符号使用"],
    "三年级语文": ["段落写作", "阅读理解", "古诗词", "成语运用"],
    "四年级语文": ["作文指导", "文言文入门", "修辞手法", "阅读理解技巧"],
    "五年级语文": ["议论文基础", "文学欣赏", "写作技巧", "古文阅读"],
    "六年级语文": ["综合写作", "古文阅读", "文学常识", "阅读理解"],
    "一年级英语": ["字母学习", "简单单词", "基础对话", "英语儿歌"],
    "二年级英语": ["单词记忆", "简单句型", "英语儿歌", "日常对话"],
    "三年级英语": ["语法入门", "阅读理解", "英语写作", "英语对话"],
    "四年级英语": ["时态学习", "阅读提升", "口语练习", "英语写作"],
    "五年级英语": ["复合句学习", "阅读策略", "写作训练", "英语语法"],
    "六年级英语": ["语法综合", "阅读进阶", "应试准备", "英语写作"],
    
    # 初中部分
    "初中数学": ["代数基础运算", "一元一次方程", "平面几何入门", "函数初步概念"],
    "初中语文": ["文言文阅读技巧", "现代文阅读方法", "作文结构训练", "古诗词鉴赏"],
    "初中英语": ["时态综合运用", "复合句语法", "阅读理解技巧", "英语写作训练"],
    "初中物理": ["力学基础知识", "声学现象解析", "光学基本原理", "热学基础概念"],
    "初中化学": ["化学元素认识", "化学反应基础", "化学实验安全", "化学方程式"],
    
    # 高中部分
    "高中数学": ["函数与导数", "三角函数应用", "立体几何", "解析几何"],
    "高中语文": ["古诗文深度解读", "现代文阅读进阶", "议论文写作技巧", "文学类文本阅读"],
    "高中英语": ["长难句分析", "完形填空技巧", "阅读理解进阶", "写作能力提升"],
    "高中物理": ["牛顿力学深入", "电磁学原理", "热力学定律", "光学深入"],
    "高中化学": ["有机化学基础", "化学反应原理", "物质结构与性质", "化学平衡"],
    
    # 大学部分
    "大学数学": ["高等数学基础", "线性代数", "概率论与数理统计", "微积分应用"],
    "大学英语": ["学术英语写作", "英语听说进阶", "跨文化交际", "专业英语阅读"],
    "大学专业课": ["专业基础理论", "专业核心知识", "专业实践应用", "专业前沿发展"]
}

# 文章角度库
ARTICLE_ANGLES = {
    "数学": ["实用解题技巧", "常见错误分析", "思维训练方法", "生活应用实例"],
    "语文": ["阅读方法指导", "写作技巧分享", "文学欣赏方法", "语言表达训练"],
    "英语": ["口语练习方法", "单词记忆技巧", "语法学习策略", "听力训练方法"],
    "物理": ["实验操作方法", "物理原理应用", "问题解决方法", "思维训练方法"],
    "化学": ["实验安全操作", "化学反应原理", "化学计算技巧", "化学思维方法"],
    "专业课": ["专业基础理论", "专业实践应用", "专业学习方法", "专业前沿动态"]
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
    # 将所有分类按学段分组
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

def generate_extended_title(base_topic, category, angle):
    """生成扩展的标题（10-20字）"""
    # 定义标题模板
    templates = [
        "【{grade}{subject}】{base_topic}：{angle}的详细讲解与实用指南",
        "{grade}{subject}必备：{base_topic}的{angle}与学习方法全解析",
        "深度解析{base_topic}：{grade}{subject}的{angle}与应用技巧",
        "{grade}{subject}学习指南：{base_topic}的{angle}与实用技巧",
        "全面掌握{base_topic}：{grade}{subject}的{angle}与解题方法"
    ]
    
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
    
    # 从模板中随机选择一个
    template = random.choice(templates)
    
    # 生成标题
    title = template.format(
        grade=grade,
        subject=subject,
        base_topic=base_topic,
        angle=angle
    )
    
    # 确保标题长度在10-20字之间
    title_length = len(title)
    if title_length < 10:
        prefixes = ["深度解析：", "详细讲解：", "完全掌握：", "高效学习："]
        title = random.choice(prefixes) + title
    elif title_length > 20:
        title_words = list(title)
        if len(title_words) > 20:
            for i in range(20, 0, -1):
                if title_words[i] in ['，', '：', '、', '；']:
                    title = ''.join(title_words[:i+1])
                    break
            else:
                title = ''.join(title_words[:20]) + "..."
    
    print(f"📝 生成扩展标题: {title} (长度: {len(title)}字)")
    return title

def get_zhipu_ai_content(topic, category, angle):
    """使用智谱AI生成丰富内容的文章"""
    if not ZHIPU_API_KEY:
        print("❌ 智谱API密钥未设置")
        return None, None
        
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {"Authorization": f"Bearer {ZHIPU_API_KEY}", "Content-Type": "application/json"}
    
    # 根据分类定制提示词
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
    
    # 扩展标题
    extended_title = generate_extended_title(topic, category, angle)
    
    # 修复提示词
    prompt = f"""
请以专业教师的身份，为{student_type}写一篇关于'{topic}'的详细学习文章，重点角度是：{angle}。

**文章标题：{extended_title}**

**写作要求：**
1. 面向{student_type}
2. 科目重点：{subject}，角度重点：{angle}
3. 字数：至少2000字
4. 内容结构必须包含：
   - 引言：生动开头，说明学习重要性
   - 核心知识：详细讲解3-5个核心知识点，每个有具体例子
   - 学习方法：提供3-4种实用的学习方法
   - 实践练习：设计5-6个练习题，包含详细解答
   - 常见问题：列出5-6个常见问题及解决方法
   - 拓展学习：推荐学习资源和进阶知识
   - 总结：回顾重点，给出学习建议

5. 使用干净的HTML格式，只使用：<h2>, <h3>, <p>, <ul>, <li>, <strong>, <em>
6. 确保文章完整，不要中途停止
7. 文章内容要与标题'{extended_title}'保持一致

请直接开始文章写作：
    """
    
    data = {
        "model": "glm-4",
        "messages": [
            {
                "role": "system", 
                "content": f"你是一个经验丰富的{grade}教师，擅长用适当的语言解释复杂概念，能够激发学生的学习兴趣。特别注意：1. 必须生成完整的长文章，至少2000字，包含所有要求的部分；2. 文章标题是'{extended_title}'，请围绕这个标题展开内容。"
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 4000,
    }
    
    try:
        print(f"🤖 正在调用AI生成内容...")
        response = requests.post(url, headers=headers, json=data, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            content_length = len(content)
            print(f"✅ AI生成内容长度: {content_length}字符")
            
            if content_length < 1000:
                print(f"⚠️  警告：生成的内容可能不完整，只有{content_length}字符")
            
            # 清理HTML
            cleaned_content = clean_html_content(content)
            
            if cleaned_content != content:
                print(f"✅ 已清理HTML，从{len(content)}字符减少到{len(cleaned_content)}字符")
            
            return extended_title, cleaned_content
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"错误详情: {response.text[:200]}")
            return None, None
    except Exception as e:
        print(f"❌ AI生成失败: {e}")
        return None, None

def retry_ai_generation(topic, category, angle, max_retries=2):
    """重试AI生成，直到获得足够长度的内容"""
    for attempt in range(max_retries + 1):
        print(f"🔄 第{attempt+1}次尝试生成内容...")
        extended_title, content = get_zhipu_ai_content(topic, category, angle)
        
        if content and len(content) > 1500:
            print(f"✅ 第{attempt+1}次尝试成功，获得{len(content)}字符的内容")
            return extended_title, content
        elif content and len(content) > 0:
            print(f"⚠️  第{attempt+1}次尝试内容长度{len(content)}字符，尝试重试...")
            if attempt < max_retries:
                time.sleep(2)
        else:
            print(f"❌ 第{attempt+1}次尝试失败")
            if attempt < max_retries:
                time.sleep(2)
    
    return extended_title, content

def clean_html_content(content):
    """清理HTML内容，移除无效标签"""
    if not content:
        return content
    
    cleaned_content = content
    
    # 只清理特定的无效标签
    invalid_patterns = [
        r'<pFig[^>]*>',
        r'</pFig>',
        r'<quad[^>]*>',
        r'</quad>',
        r'<pos_\d+[^>]*>',
    ]
    
    for pattern in invalid_patterns:
        cleaned_content = re.sub(pattern, '', cleaned_content)
    
    # 清理多余的空行
    cleaned_content = re.sub(r'\n{3,}', '\n\n', cleaned_content)
    
    if cleaned_content.strip() == '':
        print("⚠️  清理后内容为空，返回原始内容")
        return content
    
    return cleaned_content

def generate_smart_tags(category, content, title):
    """生成智能标签名称"""
    tags = set()
    
    # 1. 基础分类标签
    if "初中" in category or "高中" in category or "大学" in category:
        if "初中" in category:
            tags.add("初中")
            subject = category[2:]
        elif "高中" in category:
            tags.add("高中")
            subject = category[2:]
        else:  # 大学
            tags.add("大学")
            subject = category[2:]
        
        tags.add(subject)
        tags.add(f"{subject}学习")
    else:
        grade = category[:3]
        subject = category[3:]
        tags.add(grade)
        tags.add(subject)
        tags.add(f"小学{subject}")
    
    # 2. 从内容中提取关键词标签
    try:
        keywords = jieba.analyse.extract_tags(content, topK=4, withWeight=False, allowPOS=('n', 'vn', 'v', 'a'))
        filtered_keywords = [word for word in keywords if len(word) >= 2 and len(word) <= 6 and not word.isdigit()]
        tags.update(filtered_keywords[:4])
    except:
        pass
    
    # 3. 学科特定标签
    if "数学" in subject:
        math_tags = ["计算题", "应用题", "数学思维", "解题技巧", "几何图形", "代数基础"]
        tags.update(random.sample(math_tags, 4))
    elif "语文" in subject:
        chinese_tags = ["阅读理解", "作文指导", "古诗词", "汉字书写", "写作技巧", "文学常识"]
        tags.update(random.sample(chinese_tags, 4))
    elif "英语" in subject:
        english_tags = ["单词记忆", "语法学习", "口语练习", "听力训练", "英语阅读", "英语写作"]
        tags.update(random.sample(english_tags, 4))
    
    # 4. 通用学习标签
    learning_tags = ["学习方法", "学习资料", "教学资源", "知识点总结", "教育指导", "复习方法", "考试技巧"]
    tags.update(random.sample(learning_tags, 3))
    
    # 5. 难度标签
    if "初中" in category or "高中" in category or "大学" in category:
        difficulty_tags = ["基础知识", "进阶学习", "提高训练", "深度解析", "专业拓展"]
    else:
        difficulty_tags = ["基础入门", "巩固练习", "提高训练", "进阶挑战", "拓展学习"]
    tags.add(random.choice(difficulty_tags))
    
    # 6. 确保标签多样性
    final_tags = []
    for tag in tags:
        if len(tag) <= 8 and len(tag) >= 2:
            final_tags.append(tag)
    
    # 随机排序并限制数量（8-12个）
    random.shuffle(final_tags)
    final_tags = final_tags[:random.randint(8, 12)]
    
    print(f"🏷️  生成的智能标签名称({len(final_tags)}个): {final_tags}")
    return final_tags

def get_or_create_tag(tag_name):
    """获取或创建标签，返回标签ID"""
    global TAG_CACHE
    
    if tag_name in TAG_CACHE:
        return TAG_CACHE[tag_name]
    
    try:
        api_url = WORDPRESS_URL.rstrip('/') + '/wp-json/wp/v2/tags'
        auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
        
        # 先搜索是否已存在该标签
        search_url = f"{api_url}?search={tag_name}"
        response = requests.get(search_url, auth=auth, timeout=10)
        
        if response.status_code == 200:
            tags = response.json()
            for tag in tags:
                if tag['name'] == tag_name:
                    TAG_CACHE[tag_name] = tag['id']
                    print(f"  ✅ 找到现有标签: {tag_name} (ID: {tag['id']})")
                    return tag['id']
        
        # 如果不存在，创建新标签
        tag_data = {'name': tag_name, 'slug': tag_name}
        response = requests.post(api_url, json=tag_data, auth=auth, timeout=10)
        
        if response.status_code == 201:
            tag_id = response.json()['id']
            TAG_CACHE[tag_name] = tag_id
            print(f"  ✅ 创建新标签: {tag_name} (ID: {tag_id})")
            return tag_id
        else:
            print(f"  ⚠️  创建标签失败: {tag_name}, 状态码: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"  ❌ 标签操作异常: {tag_name}, 错误: {e}")
        return None

def get_tag_ids(tag_names):
    """将标签名称列表转换为标签ID列表"""
    tag_ids = []
    
    for tag_name in tag_names:
        tag_id = get_or_create_tag(tag_name)
        if tag_id:
            tag_ids.append(tag_id)
    
    print(f"🔢 转换后的标签ID({len(tag_ids)}个): {tag_ids}")
    return tag_ids

def generate_complete_seo_data(title, content, tags, category):
    """生成完整的SEO数据"""
    try:
        site_name = "格物智库"
        seo_title = f"{title} - {site_name}"
        
        # 从内容中提取纯文本
        plain_text = re.sub(r'<[^>]+>', '', content)
        plain_text = re.sub(r'\s+', ' ', plain_text).strip()
        
        # 生成SEO描述
        if len(plain_text) > 155:
            if '.' in plain_text[:155]:
                end_pos = plain_text[:155].rfind('.') + 1
                seo_description = plain_text[:end_pos].strip()
            else:
                seo_description = plain_text[:150].strip() + "..."
        else:
            seo_description = plain_text
        
        if not seo_description or len(seo_description) < 20:
            seo_description = f"本文详细讲解{title}的概念、应用和解题方法，帮助{category[:3]}学生掌握相关知识。"
        
        # 生成焦点关键词
        if tags and len(tags) > 0:
            focus_keyword = tags[0]
        else:
            focus_keyword = title[:6] if len(title) > 6 else title
        
        # 创建完整的Yoast SEO数据结构
        seo_data = {
            "_yoast_wpseo_title": seo_title,
            "_yoast_wpseo_metadesc": seo_description,
            "_yoast_wpseo_focuskw": focus_keyword,
            "_yoast_wpseo_meta-robots-noindex": "0",
            "_yoast_wpseo_meta-robots-nofollow": "0",
            "_yoast_wpseo_opengraph-title": seo_title,
            "_yoast_wpseo_opengraph-description": seo_description,
            "_yoast_wpseo_twitter-title": seo_title,
            "_yoast_wpseo_twitter-description": seo_description,
            "_yoast_wpseo_canonical": "",
            "_yoast_wpseo_meta-robots-adv": "",
            "_yoast_wpseo_schema_article_type": "Article",
            "_yoast_wpseo_schema_page_type": "WebPage",
        }
        
        print(f"🔍 生成SEO数据:")
        print(f"  - SEO标题: {seo_title}")
        print(f"  - SEO描述: {seo_description[:60]}...")
        print(f"  - 焦点关键词: {focus_keyword}")
        
        return seo_data
        
    except Exception as e:
        print(f"❌ 生成SEO数据失败: {e}")
        return None

def post_to_wordpress_with_complete_seo(title, content, category, slug):
    """发布到WordPress，包含完整的SEO信息"""
    try:
        api_url = WORDPRESS_URL.rstrip('/') + '/wp-json/wp/v2/posts'
        
        # 检查内容长度
        if len(content) < 800:
            print(f"⚠️  警告：文章内容过短，只有{len(content)}字符")
        
        # 生成智能标签名称
        tag_names = generate_smart_tags(category, content, title)
        
        # 将标签名称转换为标签ID
        tag_ids = get_tag_ids(tag_names)
        
        auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
        
        # 获取分类ID
        category_id = CATEGORY_MAP.get(category, 1)
        
        # 生成完整的SEO数据
        seo_data = generate_complete_seo_data(title, content, tag_names, category)
        
        # 构建文章数据
        post_data = {
            'title': title,
            'content': content,
            'status': 'draft',
            'categories': [category_id],
            'slug': slug
        }
        
        # 添加标签
        if tag_ids:
            post_data['tags'] = tag_ids
        
        # 添加完整的SEO数据
        if seo_data:
            post_data['meta'] = seo_data
        
        print(f"📤 发布数据准备完成:")
        print(f"  - 标题: {title}")
        print(f"  - 分类: {category}(ID:{category_id})")
        print(f"  - 别名: {slug}")
        print(f"  - 标签数量: {len(tag_ids)}")
        print(f"  - 文章长度: {len(content)}字符")
        
        # 发布文章
        response = requests.post(api_url, json=post_data, auth=auth, timeout=30)
        print(f"🌐 WordPress响应状态: {response.status_code}")
        
        if response.status_code == 201:
            post_data = response.json()
            post_id = post_data['id']
            print(f"✅ 文章保存为草稿成功！文章ID: {post_id}")
            
            # 更新文章为发布状态
            update_data = {'status': 'publish'}
            update_response = requests.post(f"{api_url}/{post_id}", json=update_data, auth=auth, timeout=10)
            
            if update_response.status_code == 200:
                print("✅ 文章已发布")
            else:
                print(f"⚠️  文章状态更新失败: {update_response.status_code}")
            
            return True, post_id, tag_names
        else:
            print(f"❌ 发布失败: {response.status_code}")
            print(f"错误详情: {response.text[:200]}")
            return False, None, None
            
    except Exception as e:
        print(f"❌ 发布异常: {e}")
        return False, None, None

def main():
    print("🚀 开始自动发布文章流程...")
    print(f"📅 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 清空本次会话的图片缓存
    USED_IMAGES_CACHE['session'].clear()
    
    # 检查环境变量
    if not all([ZHIPU_API_KEY, WORDPRESS_URL, WORDPRESS_USER, WORDPRESS_PASSWORD]):
        print("❌ 错误：缺少必要的环境变量配置")
        return False
    
    # 检查主题库
    total_topics = sum(len(topics) for topics in TOPICS_BY_CATEGORY.values())
    print(f"📚 主题库加载完成，共 {len(TOPICS_BY_CATEGORY)} 个分类，{total_topics} 个主题")
    
    # 发布新文章
    print("\n📝 正在选择文章主题...")
    category, base_topic, angle = select_topic_and_angle()
    
    print(f"\n{'='*50}")
    print(f"📖 分类: {category}")
    print(f"🎯 基础主题: {base_topic}")
    print(f"📐 角度: {angle}")
    
    # 生成别名
    slug = generate_random_slug(random.randint(6, 10))
    print(f"🔗 文章别名: {slug}")
    
    # 获取AI内容（带重试机制）
    print("\n🤖 正在调用AI生成内容...")
    extended_title, content = retry_ai_generation(base_topic, category, angle, max_retries=2)
    
    if not content or not extended_title:
        print("❌ 内容生成失败")
        return False
    
    print(f"✅ 内容生成成功，标题: {extended_title}")
    print(f"✅ 文章长度: {len(content)}字符")
    
    # 发布文章
    print("\n🌐 正在发布到WordPress...")
    success, post_id, tag_names = post_to_wordpress_with_complete_seo(extended_title, content, category, slug)
    
    if success:
        print("\n🎉 文章发布成功！")
        print(f"🔗 文章链接: {WORDPRESS_URL.rstrip('/')}/?p={post_id}")
        return True
    else:
        print("💥 文章发布失败")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
