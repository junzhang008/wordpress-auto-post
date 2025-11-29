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

# 导入完整的主题库
try:
    from topics import TOPICS_BY_CATEGORY
    print("✅ 成功加载完整主题库")
except ImportError:
    print("❌ 无法导入主题库，使用增强主题库")
    TOPICS_BY_CATEGORY = {
        "一年级数学": [
            "10以内加减法练习", "认识数字1-100", "简单图形识别", "数字的大小比较", 
            "认识钟表时间", "简单的数位概念", "数字的排列组合", "生活中的数学应用",
            "数学游戏与趣味题", "数学思维训练入门"
        ],
        "二年级数学": [
            "乘法口诀记忆", "100以内加减法", "认识时间", "长度单位换算",
            "人民币的认识", "简单的统计图表", "几何图形拼组", "数学逻辑推理",
            "数学应用题解析", "数学学习方法指导"
        ],
        "三年级数学": [
            "万以内数的认识", "两位数乘法", "小数初步认识", "分数的初步认识",
            "长方形和正方形", "方向与位置", "数据的收集整理", "数学思维拓展",
            "数学竞赛入门", "数学与生活实践"
        ],
        "四年级数学": [
            "大数的认识", "小数运算", "几何图形", "三角形和四边形",
            "运算定律应用", "小数的加减法", "统计与概率", "数学建模初步",
            "数学问题解决策略", "数学创新思维"
        ],
        "五年级数学": [
            "分数运算", "方程初步", "立体图形", "多边形的面积",
            "因数与倍数", "分数的加减乘除", "数学广角", "数学思维训练",
            "数学与科学技术", "数学史话"
        ],
        "六年级数学": [
            "比例应用", "圆的面积", "统计图表", "圆柱与圆锥",
            "正比例反比例", "数学综合应用", "数学思维方法", "数学与艺术",
            "数学与编程", "中学数学衔接"
        ],
        "一年级语文": [
            "拼音学习", "汉字书写", "简单阅读", "词语积累",
            "句子练习", "看图说话", "儿歌童谣", "成语故事",
            "阅读习惯培养", "语文学习方法"
        ],
        "二年级语文": [
            "词语积累", "句子练习", "短文阅读", "标点符号使用",
            "修辞手法入门", "古诗词欣赏", "童话故事阅读", "写作基础训练",
            "语文综合能力", "文学素养培养"
        ],
        "三年级语文": [
            "段落写作", "阅读理解", "古诗词", "成语运用",
            "修辞手法应用", "作文技巧", "文学常识", "语文实践应用",
            "阅读策略指导", "写作能力提升"
        ],
        "四年级语文": [
            "作文指导", "文言文入门", "修辞手法", "阅读理解技巧",
            "古诗词鉴赏", "文学名著导读", "写作方法", "语文综合素养",
            "文学创作启蒙", "传统文化学习"
        ],
        "五年级语文": [
            "议论文基础", "文学欣赏", "写作技巧", "古文阅读",
            "现代文阅读", "作文修改", "文学评论", "语文综合应用",
            "文学素养提升", "文化传承"
        ],
        "六年级语文": [
            "综合写作", "古文阅读", "文学常识", "阅读理解",
            "作文表达", "文学鉴赏", "语文综合能力", "升学准备",
            "文学创作", "文化素养"
        ],
        "一年级英语": [
            "字母学习", "简单单词", "基础对话", "英语儿歌",
            "日常用语", "颜色形状", "数字英语", "动物世界",
            "英语游戏", "英语启蒙"
        ],
        "二年级英语": [
            "单词记忆", "简单句型", "英语儿歌", "日常对话",
            "情景英语", "英语故事", "英语歌曲", "英语绘本",
            "英语口语", "英语兴趣培养"
        ],
        "三年级英语": [
            "语法入门", "阅读理解", "英语写作", "英语对话",
            "英语短文", "英语歌曲", "英语故事", "英语文化",
            "英语学习方法", "英语能力提升"
        ],
        "四年级英语": [
            "时态学习", "阅读提升", "口语练习", "英语写作",
            "英语听力", "英语演讲", "英语戏剧", "英语阅读",
            "英语综合能力", "英语应用"
        ],
        "五年级英语": [
            "复合句学习", "阅读策略", "写作训练", "英语语法",
            "英语阅读", "英语写作", "英语口语", "英语文化",
            "英语考试技巧", "英语能力拓展"
        ],
        "六年级英语": [
            "语法综合", "阅读进阶", "应试准备", "英语写作",
            "英语口语", "英语听力", "英语阅读", "英语应用",
            "中学英语衔接", "英语综合素养"
        ]
    }

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
    "五年级英语": 22, "六年级英语": 23
}

# 增强的图片关键词映射
TOPIC_IMAGE_KEYWORDS = {
    "数学": ["数学", "计算", "几何", "公式", "数字", "逻辑", "思维", "图形", "代数", "统计"],
    "语文": ["语文", "阅读", "写作", "书籍", "文学", "汉字", "书法", "诗词", "故事", "文化"],
    "英语": ["英语", "学习", "国际", "字母", "单词", "对话", "外语", "交流", "文化", "阅读"],
    "一年级": ["儿童", "基础", "入门", "简单", "趣味", "启蒙", "游戏", "卡通", "色彩"],
    "二年级": ["儿童", "学习", "成长", "进步", "探索", "发现", "趣味", "互动"],
    "三年级": ["学生", "学习", "教育", "校园", "思考", "进步", "成长", "探索"],
    "四年级": ["学生", "教育", "学习", "课堂", "思考", "创造", "实践", "应用"],
    "五年级": ["学生", "学习", "教育", "思考", "分析", "创新", "拓展", "深入"],
    "六年级": ["学生", "毕业", "升学", "考试", "总结", "提升", "准备", "未来"]
}

# 文章角度库 - 让内容更加丰富
ARTICLE_ANGLES = {
    "数学": [
        "实用解题技巧", "常见错误分析", "思维训练方法", "生活应用实例",
        "趣味数学游戏", "考试重点解析", "学习方法指导", "知识点深度解析",
        "数学思维培养", "实际应用案例"
    ],
    "语文": [
        "阅读方法指导", "写作技巧分享", "文学欣赏方法", "语言表达训练",
        "传统文化学习", "阅读理解策略", "作文构思方法", "诗词鉴赏技巧",
        "语言运用能力", "文学素养提升"
    ],
    "英语": [
        "口语练习方法", "单词记忆技巧", "语法学习策略", "听力训练方法",
        "阅读能力提升", "写作技巧指导", "文化交流知识", "学习方法分享",
        "实际应用场景", "考试准备策略"
    ]
}

# 图片类型库
IMAGE_TYPES = [
    "概念图解", "实例演示", "步骤说明", "对比分析", 
    "应用场景", "趣味插图", "知识总结", "思维导图"
]

# 标签缓存
TAG_CACHE = {}

def generate_random_slug(length=8):
    """生成随机别名"""
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def extract_keywords_from_content(content, topK=5):
    """从内容中提取关键词"""
    try:
        # 使用jieba提取关键词
        keywords = jieba.analyse.extract_tags(
            content, 
            topK=topK, 
            withWeight=False,
            allowPOS=('n', 'vn', 'v', 'a')
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
        words = content.replace('\n', ' ').replace('，', ' ').replace('。', ' ').split(' ')
        meaningful_words = [word for word in words if len(word) >= 2 and len(word) <= 6]
        return random.sample(meaningful_words, min(topK, len(meaningful_words)))

def extract_keywords_from_title(title):
    """从标题中提取关键词"""
    try:
        words = jieba.lcut(title)
        keywords = [word for word in words if len(word) >= 2]
        return keywords[:3]
    except:
        return [word for word in title if len(word) >= 2][:3]

def generate_smart_tags(category, content, title):
    """生成智能标签名称"""
    tags = set()
    
    # 1. 基础分类标签
    grade = category[:3]
    subject = category[3:]
    
    tags.add(grade)
    tags.add(subject)
    tags.add(f"小学{subject}")
    
    # 2. 从内容中提取关键词标签
    content_keywords = extract_keywords_from_content(content, 4)
    tags.update(content_keywords)
    
    # 3. 从标题中提取关键词标签
    title_keywords = extract_keywords_from_title(title)
    tags.update(title_keywords)
    
    # 4. 学科特定标签
    if "数学" in subject:
        math_tags = ["计算题", "应用题", "数学思维", "解题技巧", "逻辑训练", "几何图形", "代数基础", "数据分析", "数学建模"]
        tags.update(random.sample(math_tags, 4))
    elif "语文" in subject:
        chinese_tags = ["阅读理解", "作文指导", "古诗词", "汉字书写", "语言表达", "文学欣赏", "写作技巧", "修辞手法", "文学常识"]
        tags.update(random.sample(chinese_tags, 4))
    elif "英语" in subject:
        english_tags = ["单词记忆", "语法学习", "口语练习", "听力训练", "英语阅读", "英语写作", "发音纠正", "情景对话", "英语文化"]
        tags.update(random.sample(english_tags, 4))
    
    # 5. 通用学习标签
    learning_tags = ["学习方法", "学习资料", "家长必读", "教学资源", "知识点总结", "教育指导", "学习计划", "复习方法"]
    tags.update(random.sample(learning_tags, 3))
    
    # 6. 难度标签
    difficulty_tags = ["基础入门", "巩固练习", "提高训练", "进阶挑战", "拓展学习"]
    tags.add(random.choice(difficulty_tags))
    
    # 7. 资源类型标签
    resource_tags = ["电子版", "可打印", "练习题", "测试卷", "知识点", "学习计划", "教学视频", "互动学习"]
    tags.add(random.choice(resource_tags))
    
    # 8. 学习方法标签
    method_tags = ["记忆方法", "理解技巧", "应用实践", "举一反三", "思维训练", "自主学习"]
    tags.add(random.choice(method_tags))
    
    # 9. 确保标签多样性
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
        tag_data = {
            'name': tag_name,
            'slug': tag_name
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

def get_image_keywords(category, topic, image_type):
    """根据分类、主题和图片类型生成图片搜索关键词"""
    keywords = []
    
    # 提取年级和科目
    grade = category[:3]
    subject = category[3:]
    
    # 添加基础关键词
    keywords.extend(TOPIC_IMAGE_KEYWORDS.get(grade, []))
    keywords.extend(TOPIC_IMAGE_KEYWORDS.get(subject, []))
    
    # 从主题中提取关键词
    topic_words = jieba.lcut(topic)
    keywords.extend([word for word in topic_words if len(word) >= 2])
    
    # 根据图片类型添加关键词
    if image_type == "概念图解":
        keywords.extend(["图解", "说明", "解析", "示意图"])
    elif image_type == "实例演示":
        keywords.extend(["实例", "演示", "示例", "案例"])
    elif image_type == "步骤说明":
        keywords.extend(["步骤", "流程", "顺序", "方法"])
    elif image_type == "对比分析":
        keywords.extend(["对比", "比较", "分析", "差异"])
    elif image_type == "应用场景":
        keywords.extend(["应用", "场景", "实践", "使用"])
    elif image_type == "趣味插图":
        keywords.extend(["趣味", "插图", "卡通", "生动"])
    elif image_type == "知识总结":
        keywords.extend(["总结", "归纳", "要点", "重点"])
    elif image_type == "思维导图":
        keywords.extend(["思维", "导图", "结构", "关系"])
    
    # 添加教育相关通用关键词
    keywords.extend(["教育", "学习", "学校", "课堂", "学生"])
    
    # 去重并限制数量
    unique_keywords = list(set(keywords))[:6]
    
    print(f"🖼️  图片搜索关键词({image_type}): {unique_keywords}")
    return unique_keywords

def get_unsplash_image(keywords):
    """从Unsplash获取相关图片"""
    if not UNSPLASH_ACCESS_KEY:
        return None
        
    try:
        # 随机选择一个关键词组合
        keyword_combinations = [
            " ".join(keywords[:2]),
            " ".join(keywords[2:4]),
            keywords[0] + " education",
            "learning " + keywords[1]
        ]
        
        keyword = random.choice(keyword_combinations)
        
        url = "https://api.unsplash.com/photos/random"
        params = {
            "query": keyword,
            "orientation": "landscape",
            "content_filter": "high"
        }
        headers = {
            "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            image_url = data['urls']['regular']
            print(f"✅ 从Unsplash获取图片: {image_url}")
            return image_url
        else:
            print(f"⚠️  Unsplash API请求失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Unsplash图片获取失败: {e}")
        return None

def get_stock_image(keywords):
    """获取免费库存图片（备用方案）"""
    # 使用多个免费图库源
    education_images = [
        # 学习相关
        "https://images.unsplash.com/photo-1497636577773-f1231844b336?w=800",
        "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800",
        "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=800",
        "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=800",
        "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=800",
        # 数学相关
        "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=800",
        "https://images.unsplash.com/photo-1596495577886-d920f1fb7238?w=800",
        # 语文相关
        "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=800",
        "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800",
        # 英语相关
        "https://images.unsplash.com/photo-1523580494863-6f3031224c94?w=800",
        "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=800"
    ]
    
    return random.choice(education_images)

def upload_image_to_wordpress(image_url, title, alt_text=""):
    """上传图片到WordPress并返回媒体ID"""
    try:
        # 下载图片
        response = requests.get(image_url, timeout=15)
        if response.status_code != 200:
            print(f"❌ 图片下载失败: {image_url}")
            return None
        
        # 准备上传到WordPress
        upload_url = WORDPRESS_URL.rstrip('/') + '/wp-json/wp/v2/media'
        auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
        
        # 生成文件名
        file_extension = image_url.split('.')[-1].lower()
        if file_extension not in ['jpg', 'jpeg', 'png', 'gif']:
            file_extension = 'jpg'
        
        filename = f"{generate_random_slug(10)}.{file_extension}"
        
        # 上传图片
        headers = {
            'Content-Disposition': f'attachment; filename={filename}',
            'Content-Type': f'image/{file_extension}'
        }
        
        upload_response = requests.post(
            upload_url,
            headers=headers,
            data=response.content,
            auth=auth,
            timeout=30
        )
        
        if upload_response.status_code == 201:
            media_data = upload_response.json()
            media_id = media_data['id']
            print(f"✅ 图片上传成功，媒体ID: {media_id}")
            
            # 更新图片的alt文本和标题
            update_data = {
                'title': title,
                'alt_text': alt_text or title
            }
            
            update_response = requests.post(
                f"{upload_url}/{media_id}",
                json=update_data,
                auth=auth,
                timeout=10
            )
            
            return media_id
        else:
            print(f"❌ 图片上传失败: {upload_response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 图片上传异常: {e}")
        return None

def add_featured_image(post_id, media_id):
    """设置文章的特色图片"""
    try:
        update_url = WORDPRESS_URL.rstrip('/') + f'/wp-json/wp/v2/posts/{post_id}'
        auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
        
        update_data = {
            'featured_media': media_id
        }
        
        response = requests.post(update_url, json=update_data, auth=auth, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ 特色图片设置成功")
            return True
        else:
            print(f"⚠️  特色图片设置失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 设置特色图片异常: {e}")
        return False

def insert_images_into_content(content, images_data):
    """在文章内容中插入多张图片"""
    if not images_data:
        return content
    
    # 图片HTML模板
    image_template = '''
<div class="article-image" style="margin: 30px 0; text-align: center;">
    <img src="{image_url}" alt="{alt_text}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
    <p style="text-align: center; color: #666; font-size: 14px; margin-top: 10px; font-style: italic;">{caption}</p>
</div>
'''
    
    # 将内容分段
    paragraphs = re.split(r'(</p>|</h2>|</h3>)', content)
    
    # 计算插入位置（在1/3、2/3处插入图片）
    insert_positions = [
        max(1, len(paragraphs) // 3),
        max(1, len(paragraphs) * 2 // 3)
    ]
    
    content_with_images = ""
    image_index = 0
    
    for i, para in enumerate(paragraphs):
        content_with_images += para
        
        # 在指定位置插入图片
        if i in insert_positions and image_index < len(images_data):
            image_info = images_data[image_index]
            image_html = image_template.format(
                image_url=image_info['url'],
                alt_text=image_info['alt_text'],
                caption=image_info['caption']
            )
            content_with_images += image_html
            image_index += 1
            print(f"✅ 插入图片: {image_info['caption']}")
    
    return content_with_images

def get_zhipu_ai_content(topic, category, angle):
    """使用智谱AI生成丰富内容的文章"""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {ZHIPU_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 根据分类定制提示词
    grade = category[:3]
    subject = category[3:]
    
    prompt = f"""
    请以专业小学教师的身份，为{grade}学生写一篇关于'{topic}'的详细学习文章，重点角度是：{angle}。
    
    写作要求：
    1. 面向{grade}学生和家长，语言亲切易懂但专业
    2. 科目重点：{subject}，角度重点：{angle}
    3. 字数：1200-1500字
    4. 内容结构要求：
       - 开头：生动引入主题，说明学习重要性
       - 知识讲解：详细讲解核心知识点，包含2-3个具体例子
       - 方法指导：提供实用的学习方法和技巧
       - 实践应用：设计3-4个练习题或实践活动
       - 常见问题：分析学生常见错误和解决方法
       - 拓展学习：提供相关的拓展知识和资源推荐
       - 总结：回顾重点，给出学习建议
    
    5. 包含丰富的实例和案例分析
    6. 语言生动有趣，适合小学生阅读但内容专业
    7. 使用HTML格式，包含适当的标题和段落
    8. 在适当位置标注图片插入位置，用[图片1]、[图片2]表示
    
    请开始写作：
    """
    
    data = {
        "model": "glm-4",
        "messages": [
            {
                "role": "system", 
                "content": "你是一个经验丰富的小学教师，擅长用简单易懂的语言解释复杂概念，能够激发学生的学习兴趣，同时保持内容的专业性和深度。"
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "temperature": 0.8,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
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

def process_images_for_article(category, topic, content, post_id):
    """为文章处理多张图片"""
    try:
        images_data = []
        
        # 为文章生成2-3张不同类型的图片
        num_images = random.randint(2, 3)
        selected_image_types = random.sample(IMAGE_TYPES, num_images)
        
        for i, image_type in enumerate(selected_image_types):
            # 生成图片关键词
            image_keywords = get_image_keywords(category, topic, image_type)
            
            # 获取图片URL
            image_url = get_unsplash_image(image_keywords)
            if not image_url:
                image_url = get_stock_image(image_keywords)
            
            if image_url:
                # 上传图片到WordPress
                alt_text = f"{topic} - {image_type}"
                caption = f"{image_type}: {topic}"
                
                media_id = upload_image_to_wordpress(image_url, f"{topic}_{image_type}", alt_text)
                
                if media_id:
                    images_data.append({
                        'url': image_url,
                        'alt_text': alt_text,
                        'caption': caption,
                        'media_id': media_id,
                        'type': image_type
                    })
                    print(f"✅ 成功处理图片 {i+1}: {image_type}")
                
                # 如果是第一张图片，设置为特色图片
                if i == 0 and media_id:
                    add_featured_image(post_id, media_id)
            
            # 添加延迟避免请求过快
            time.sleep(1)
        
        # 在内容中插入所有图片
        if images_data:
            content_with_images = insert_images_into_content(content, images_data)
            return content_with_images, images_data
        else:
            print("⚠️  无法获取图片，使用原内容")
            return content, []
            
    except Exception as e:
        print(f"❌ 图片处理异常: {e}")
        return content, []

def post_to_wordpress_with_tags(title, content, category, slug):
    """发布到WordPress并自动添加标签"""
    try:
        api_url = WORDPRESS_URL.rstrip('/') + '/wp-json/wp/v2/posts'
        
        # 生成智能标签名称
        tag_names = generate_smart_tags(category, content, title)
        
        # 将标签名称转换为标签ID
        tag_ids = get_tag_ids(tag_names)
        
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
            post_data = response.json()
            post_id = post_data['id']
            print(f"✅ 文章发布成功！文章ID: {post_id}")
            
            # 处理图片（在文章发布后）
            print("🖼️  开始处理文章图片...")
            updated_content, images_data = process_images_for_article(category, title, content, post_id)
            
            # 如果有图片且内容被更新，更新文章内容
            if updated_content != content and images_data:
                update_data = {
                    'content': updated_content
                }
                update_response = requests.post(
                    f"{api_url}/{post_id}",
                    json=update_data,
                    auth=auth,
                    timeout=10
                )
                if update_response.status_code == 200:
                    print("✅ 文章内容已更新包含图片")
                else:
                    print("⚠️  文章内容更新失败")
            
            return True
        else:
            print(f"❌ 发布失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 发布异常: {e}")
        return False

def select_topic_and_angle():
    """智能选择主题和角度"""
    # 随机选择分类
    available_categories = list(TOPICS_BY_CATEGORY.keys())
    category = random.choice(available_categories)
    
    # 从该分类中选择主题
    if category in TOPICS_BY_CATEGORY and TOPICS_BY_CATEGORY[category]:
        topic = random.choice(TOPICS_BY_CATEGORY[category])
    else:
        topic = f"{category}学习资料"
    
    # 根据科目选择角度
    subject = category[3:]
    if subject in ARTICLE_ANGLES:
        angle = random.choice(ARTICLE_ANGLES[subject])
    else:
        angle = "学习方法指导"
    
    return category, topic, angle

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
    
    # 每小时发布1篇文章
    print("📊 本次发布1篇文章")
    
    # 智能选择主题和角度
    category, topic, angle = select_topic_and_angle()
    
    print(f"\n{'='*50}")
    print(f"📝 正在处理文章")
    print(f"{'='*50}")
    print(f"📖 分类: {category}")
    print(f"🎯 主题: {topic}")
    print(f"📐 角度: {angle}")
    
    # 生成随机别名
    slug = generate_random_slug(random.randint(6, 10))
    print(f"🔗 文章别名: {slug}")
    
    # 获取AI生成内容
    print("🤖 正在调用AI生成内容...")
    content = get_zhipu_ai_content(topic, category, angle)
    
    if not content:
        print("❌ 内容生成失败，跳过此文章")
        return False
        
    print(f"✅ 内容生成成功，长度: {len(content)}字符")
    
    # 发布到WordPress
    print("🌐 正在发布到 WordPress...")
    success = post_to_wordpress_with_tags(topic, content, category, slug)
    
    if success:
        print("🎉 文章发布成功！")
        return True
    else:
        print("💥 文章发布失败")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
