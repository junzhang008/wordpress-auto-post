import requests
import random
import os
import string
from datetime import datetime
from requests.auth import HTTPBasicAuth
import jieba
import jieba.analyse

# 导入完整的主题库
try:
    from topics import TOPICS_BY_CATEGORY
    print("✅ 成功加载完整主题库")
except ImportError:
    print("❌ 无法导入主题库，使用默认主题")
    TOPICS_BY_CATEGORY = {
        "一年级数学": ["10以内加减法练习", "认识数字1-100", "简单图形识别"],
        "二年级数学": ["乘法口诀记忆", "100以内加减法", "认识时间"],
        "三年级数学": ["万以内数的认识", "两位数乘法", "小数初步认识"],
        "四年级数学": ["大数的认识", "小数运算", "几何图形"],
        "五年级数学": ["分数运算", "方程初步", "立体图形"],
        "六年级数学": ["比例应用", "圆的面积", "统计图表"],
        "一年级语文": ["拼音学习", "汉字书写", "简单阅读"],
        "二年级语文": ["词语积累", "句子练习", "短文阅读"],
        "三年级语文": ["段落写作", "阅读理解", "古诗词"],
        "四年级语文": ["作文指导", "文言文入门", "修辞手法"],
        "五年级语文": ["议论文基础", "文学欣赏", "写作技巧"],
        "六年级语文": ["综合写作", "古文阅读", "文学常识"],
        "一年级英语": ["字母学习", "简单单词", "基础对话"],
        "二年级英语": ["单词记忆", "简单句型", "英语儿歌"],
        "三年级英语": ["语法入门", "阅读理解", "英语写作"],
        "四年级英语": ["时态学习", "阅读提升", "口语练习"],
        "五年级英语": ["复合句学习", "阅读策略", "写作训练"],
        "六年级英语": ["语法综合", "阅读进阶", "应试准备"]
    }

# 配置
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
WORDPRESS_URL = os.getenv('WORDPRESS_URL')
WORDPRESS_USER = os.getenv('WORDPRESS_USER')
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD')

# 分类映射（使用你提供的正确分类ID）
CATEGORY_MAP = {
    "一年级数学": 6,
    "二年级数学": 7, 
    "三年级数学": 8,
    "四年级数学": 9,
    "五年级数学": 10,
    "六年级数学": 11,
    "一年级语文": 12,
    "二年级语文": 13,
    "三年级语文": 14,
    "四年级语文": 15,
    "五年级语文": 16,
    "六年级语文": 17,
    "一年级英语": 18,
    "二年级英语": 19,
    "三年级英语": 20,
    "四年级英语": 21,
    "五年级英语": 22,
    "六年级英语": 23
}

# 标签缓存，避免重复查询
TAG_CACHE = {}

def generate_random_slug(length=8):
    """生成随机别名"""
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def extract_keywords_from_content(content, topK=5):
    """从内容中提取关键词"""
    try:
        # 使用jieba提取关键词，基于TF-IDF算法
        keywords = jieba.analyse.extract_tags(
            content, 
            topK=topK, 
            withWeight=False,
            allowPOS=('n', 'vn', 'v', 'a')  # 只提取名词、动名词、动词、形容词
        )
        
        # 过滤停用词和过短的词
        filtered_keywords = []
        for word in keywords:
            if (len(word) >= 2 and len(word) <= 6 and 
                not word.isdigit()):
                filtered_keywords.append(word)
        
        return filtered_keywords[:topK]
        
    except Exception as e:
        print(f"关键词提取失败: {e}")
        # 备用方案：简单分词
        words = content.replace('\n', ' ').replace('，', ' ').replace('。', ' ').split(' ')
        meaningful_words = [word for word in words if len(word) >= 2 and len(word) <= 6]
        return random.sample(meaningful_words, min(topK, len(meaningful_words)))

def extract_keywords_from_title(title):
    """从标题中提取关键词"""
    try:
        words = jieba.lcut(title)
        keywords = [word for word in words if len(word) >= 2]
        return keywords[:3]  # 最多取3个
    except:
        return [word for word in title if len(word) >= 2][:3]

def generate_smart_tags(category, content, title):
    """生成智能标签名称"""
    tags = set()
    
    # 1. 基础分类标签
    grade = category[:3]  # 一年级、二年级等
    subject = category[3:]  # 数学、语文、英语
    
    tags.add(grade)
    tags.add(subject)
    tags.add(f"小学{subject}")
    
    # 2. 从内容中提取关键词标签
    content_keywords = extract_keywords_from_content(content, 3)
    tags.update(content_keywords)
    
    # 3. 从标题中提取关键词标签
    title_keywords = extract_keywords_from_title(title)
    tags.update(title_keywords)
    
    # 4. 学科特定标签
    if "数学" in subject:
        math_tags = ["计算题", "应用题", "数学思维", "解题技巧", "逻辑训练", "几何图形", "代数基础"]
        tags.update(random.sample(math_tags, 3))
    elif "语文" in subject:
        chinese_tags = ["阅读理解", "作文指导", "古诗词", "汉字书写", "语言表达", "文学欣赏", "写作技巧"]
        tags.update(random.sample(chinese_tags, 3))
    elif "英语" in subject:
        english_tags = ["单词记忆", "语法学习", "口语练习", "听力训练", "英语阅读", "英语写作", "发音纠正"]
        tags.update(random.sample(english_tags, 3))
    
    # 5. 通用学习标签
    learning_tags = ["学习方法", "学习资料", "家长必读", "教学资源", "知识点总结", "教育指导"]
    tags.update(random.sample(learning_tags, 2))
    
    # 6. 难度标签
    difficulty_tags = ["基础入门", "巩固练习", "提高训练", "进阶挑战"]
    tags.add(random.choice(difficulty_tags))
    
    # 7. 资源类型标签
    resource_tags = ["电子版", "可打印", "练习题", "测试卷", "知识点", "学习计划"]
    tags.add(random.choice(resource_tags))
    
    # 8. 学习方法标签
    method_tags = ["记忆方法", "理解技巧", "应用实践", "举一反三"]
    tags.add(random.choice(method_tags))
    
    # 9. 确保标签多样性，避免重复
    final_tags = []
    for tag in tags:
        if len(tag) <= 8 and len(tag) >= 2:  # 限制标签长度
            final_tags.append(tag)
    
    # 随机排序并限制数量（6-10个）
    random.shuffle(final_tags)
    final_tags = final_tags[:random.randint(6, 10)]
    
    print(f"🏷️  生成的智能标签名称({len(final_tags)}个): {final_tags}")
    return final_tags

def get_or_create_tag(tag_name):
    """获取或创建标签，返回标签ID"""
    global TAG_CACHE
    
    # 检查缓存
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
            # 精确匹配标签名称
            for tag in tags:
                if tag['name'] == tag_name:
                    TAG_CACHE[tag_name] = tag['id']
                    print(f"  ✅ 找到现有标签: {tag_name} (ID: {tag['id']})")
                    return tag['id']
        
        # 如果不存在，创建新标签
        tag_data = {
            'name': tag_name,
            'slug': tag_name  # 使用名称作为别名
        }
        
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

def get_zhipu_ai_content(topic, category):
    """使用智谱AI生成文章"""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {ZHIPU_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 根据分类定制提示词
    grade = category[:3]
    subject = category[3:]
    
    prompt = f"""
    请以专业小学教师的身份，为{grade}学生写一篇关于'{topic}'的详细学习文章。
    
    写作要求：
    1. 面向{grade}学生和家长，语言亲切易懂
    2. 科目重点：{subject}
    3. 字数：800-1000字
    4. 内容结构：
       - 开头：简单介绍主题的重要性
       - 主体：详细讲解知识点，包含具体例子和方法
       - 实践：提供2-3个练习题或实践活动
       - 结尾：总结要点，给出学习建议
    
    5. 包含实用的学习技巧和记忆方法
    6. 语言生动有趣，适合小学生阅读
    7. 使用自然段落格式，不要使用markdown
    
    请开始写作：
    """
    
    data = {
        "model": "gpt-3.5-turbo",  # 使用成本更低的模型
        "messages": [
            {
                "role": "system", 
                "content": "你是一个经验丰富的小学教师，擅长用简单易懂的语言解释复杂概念，能够激发学生的学习兴趣。"
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1500
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            print(f"✅ AI生成内容长度: {len(content)}字符")
            return content
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"错误详情: {response.text}")
            return None
    except Exception as e:
        print(f"❌ AI生成失败: {e}")
        return None

def post_to_wordpress_with_tags(title, content, category, slug):
    """发布到WordPress并自动添加标签"""
    try:
        api_url = WORDPRESS_URL.rstrip('/') + '/wp-json/wp/v2/posts'
        
        # 生成智能标签名称
        tag_names = generate_smart_tags(category, content, title)
        
        # 将标签名称转换为标签ID
        tag_ids = get_tag_ids(tag_names)
        
        # 使用 HTTPBasicAuth
        auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
        
        # 获取分类ID
        category_id = CATEGORY_MAP.get(category, 1)
        
        post_data = {
            'title': title,
            'content': content,
            'status': 'publish',
            'categories': [category_id],
            'slug': slug
        }
        
        # 只有在有标签ID时才添加tags字段
        if tag_ids:
            post_data['tags'] = tag_ids
        
        print(f"📤 发布数据准备完成:")
        print(f"  - 标题: {title}")
        print(f"  - 分类: {category}(ID:{category_id})")
        print(f"  - 别名: {slug}")
        print(f"  - 标签ID数: {len(tag_ids)}")
        
        response = requests.post(api_url, json=post_data, auth=auth, timeout=30)
        print(f"🌐 WordPress响应状态: {response.status_code}")
        
        if response.status_code == 201:
            print(f"✅ 文章发布成功！")
            return True
        else:
            print(f"❌ 发布失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 发布异常: {e}")
        return False

def main():
    print("🚀 开始自动发布文章流程...")
    print(f"📅 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查必要的环境变量
    if not all([ZHIPU_API_KEY, WORDPRESS_URL, WORDPRESS_USER, WORDPRESS_PASSWORD]):
        print("❌ 错误：缺少必要的环境变量配置")
        return False
    
    # 初始化jieba分词
    try:
        jieba.initialize()
        print("✅ jieba分词器初始化成功")
    except:
        print("⚠️  jieba初始化失败，使用简单分词模式")
    
    # 检查主题库
    total_topics = sum(len(topics) for topics in TOPICS_BY_CATEGORY.values())
    print(f"📚 主题库加载完成，共 {len(TOPICS_BY_CATEGORY)} 个分类，{total_topics} 个主题")
    
    # 每天发布3-5篇文章
    article_count = random.randint(3, 5)
    print(f"📊 今天计划发布 {article_count} 篇文章")
    
    success_count = 0
    
    # 随机选择要发布的分类
    available_categories = list(TOPICS_BY_CATEGORY.keys())
    selected_categories = random.sample(available_categories, min(article_count, len(available_categories)))
    
    for i, category in enumerate(selected_categories, 1):
        print(f"\n{'='*50}")
        print(f"📝 正在处理第 {i}/{article_count} 篇文章")
        print(f"{'='*50}")
        
        # 从完整主题库中选择主题
        if category in TOPICS_BY_CATEGORY and TOPICS_BY_CATEGORY[category]:
            topic = random.choice(TOPICS_BY_CATEGORY[category])
            print(f"📖 分类: {category}")
            print(f"🎯 主题: {topic}")
        else:
            print(f"⚠️  分类 {category} 没有可用主题，使用默认主题")
            topic = f"{category}学习资料"
        
        # 生成随机别名
        slug = generate_random_slug(random.randint(6, 10))
        print(f"🔗 文章别名: {slug}")
        
        # 获取AI生成内容
        print("🤖 正在调用AI生成内容...")
        content = get_zhipu_ai_content(topic, category)
        
        if not content:
            print("❌ 内容生成失败，跳过此文章")
            continue
            
        print(f"✅ 内容生成成功，长度: {len(content)}字符")
        
        # 发布到WordPress
        print("🌐 正在发布到 WordPress...")
        success = post_to_wordpress_with_tags(topic, content, category, slug)
        
        if success:
            success_count += 1
            print(f"🎉 第 {i} 篇文章发布成功！")
        else:
            print(f"💥 第 {i} 篇文章发布失败")
        
        # 添加延迟，避免请求过于频繁
        if i < len(selected_categories):
            delay = random.randint(10, 20)
            print(f"⏳ 等待 {delay} 秒后继续下一篇文章...")
            import time
            time.sleep(delay)
    
    print(f"\n{'='*50}")
    print(f"📈 批量发布完成！")
    print(f"✅ 成功: {success_count}篇")
    print(f"❌ 失败: {article_count - success_count}篇")
    print(f"{'='*50}")
    
    return success_count > 0

if __name__ == "__main__":
    main()
