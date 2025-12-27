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
        # 小学部分
        "一年级数学": [
            "10以内加减法练习", "认识数字1-100", "简单图形识别", "数字的大小比较", 
            "认识钟表时间", "简单的数位概念", "数字的排列组合", "生活中的数学应用",
            "数学游戏与趣味题", "数学思维训练入门", "简单的利润问题"
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
        ],
        
        # 初中部分
        "初中数学": [
            "代数基础运算", "一元一次方程", "平面几何入门", "函数初步概念",
            "三角形与全等", "平行线与相交线", "二次根式运算", "勾股定理应用",
            "统计与概率基础", "数学思维方法训练", "中考数学考点解析", "数学竞赛入门"
        ],
        "初中语文": [
            "文言文阅读技巧", "现代文阅读方法", "作文结构训练", "古诗词鉴赏",
            "修辞手法应用", "文学常识积累", "写作素材收集", "阅读速度提升",
            "名著导读精析", "中考语文备考", "文学鉴赏方法", "语言表达训练"
        ],
        "初中英语": [
            "时态综合运用", "复合句语法", "阅读理解技巧", "英语写作训练",
            "听力提升方法", "口语表达训练", "词汇记忆策略", "英语文化学习",
            "中考英语备考", "英语学习方法", "语法难点突破", "英语应用能力"
        ],
        "初中物理": [
            "力学基础知识", "声学现象解析", "光学基本原理", "热学基础概念",
            "电学入门知识", "物理实验方法", "物理思维培养", "物理与生活",
            "物理公式应用", "中考物理考点", "物理学习方法", "科学探究方法"
        ],
        "初中化学": [
            "化学元素认识", "化学反应基础", "化学实验安全", "化学方程式",
            "物质分类方法", "化学计算技巧", "化学与生活", "化学实验操作",
            "化学思维训练", "中考化学备考", "化学学习方法", "科学探究素养"
        ],
        
        # 高中部分
        "高中数学": [
            "函数与导数", "三角函数应用", "立体几何", "解析几何",
            "数列与数学归纳法", "概率统计进阶", "向量运算", "复数应用",
            "数学建模方法", "高考数学策略", "竞赛数学基础", "高等数学衔接"
        ],
        "高中语文": [
            "古诗文深度解读", "现代文阅读进阶", "议论文写作技巧", "文学类文本阅读",
            "语言运用技巧", "文学常识系统", "作文素材运用", "高考作文指导",
            "文言文翻译技巧", "文学鉴赏能力", "文化传承理解", "高考语文备考"
        ],
        "高中英语": [
            "长难句分析", "完形填空技巧", "阅读理解进阶", "写作能力提升",
            "听力理解训练", "口语表达进阶", "词汇拓展记忆", "语法综合运用",
            "高考英语策略", "英语思维能力", "跨文化交际", "英语应用实践"
        ],
        "高中物理": [
            "牛顿力学深入", "电磁学原理", "热力学定律", "光学深入",
            "近代物理基础", "物理模型建立", "物理实验设计", "物理竞赛基础",
            "高考物理考点", "物理思维方法", "物理与科技", "科学前沿了解"
        ],
        "高中化学": [
            "有机化学基础", "化学反应原理", "物质结构与性质", "化学平衡",
            "电化学基础", "化学实验设计", "化学计算进阶", "化学竞赛入门",
            "高考化学备考", "化学思维培养", "化学与生活", "绿色化学理念"
        ],
        
        # 大学部分
        "大学数学": [
            "高等数学基础", "线性代数", "概率论与数理统计", "微积分应用",
            "数学分析入门", "常微分方程", "复变函数", "数值计算方法",
            "数学建模实践", "离散数学", "数学思维培养", "数学与专业应用"
        ],
        "大学英语": [
            "学术英语写作", "英语听说进阶", "跨文化交际", "专业英语阅读",
            "英语演讲技巧", "翻译基础训练", "英语研究方法", "英语文学欣赏",
            "英语能力考试", "英语实际应用", "英语思维培养", "国际交流能力"
        ],
        "大学专业课": [
            "专业基础理论", "专业核心知识", "专业实践应用", "专业前沿发展",
            "专业研究方法", "专业软件应用", "专业实验技能", "专业论文写作",
            "专业与就业", "专业与行业", "专业与创新", "专业素养培养"
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
    "五年级英语": 22, "六年级英语": 23,
    "初中数学": 774, "初中语文": 773, "初中英语": 775, "初中物理": 776, "初中化学": 777,
    "高中数学": 782, "高中语文": 781, "高中英语": 783, "高中物理": 784, "高中化学": 785,
    "大学数学": 790, "大学英语": 789, "大学专业课": 792
}

# 增强的图片关键词映射
TOPIC_IMAGE_KEYWORDS = {
    "数学": ["数学", "计算", "几何", "公式", "数字", "逻辑", "思维", "图形", "代数", "统计"],
    "语文": ["语文", "阅读", "写作", "书籍", "文学", "汉字", "书法", "诗词", "故事", "文化"],
    "英语": ["英语", "学习", "国际", "字母", "单词", "对话", "外语", "交流", "文化", "阅读"],
    "物理": ["物理", "实验", "力学", "电磁", "光学", "科学", "公式", "实验设备", "物理现象"],
    "化学": ["化学", "实验", "分子", "原子", "化学反应", "实验室", "化学式", "元素周期表"],
    "专业课": ["专业", "学术", "研究", "实验室", "技术", "创新", "实践", "应用"],
    "一年级": ["儿童", "基础", "入门", "简单", "趣味", "启蒙", "游戏", "卡通", "色彩"],
    "二年级": ["儿童", "学习", "成长", "进步", "探索", "发现", "趣味", "互动"],
    "三年级": ["学生", "学习", "教育", "校园", "思考", "进步", "成长", "探索"],
    "四年级": ["学生", "教育", "学习", "课堂", "思考", "创造", "实践", "应用"],
    "五年级": ["学生", "学习", "教育", "思考", "分析", "创新", "拓展", "深入"],
    "六年级": ["学生", "毕业", "升学", "考试", "总结", "提升", "准备", "未来"],
    "初中": ["初中生", "青少年", "中学", "校园", "成长", "学习", "教育", "青春期"],
    "高中": ["高中生", "青少年", "中学", "校园", "学习", "高考", "教育", "青春"],
    "大学": ["大学生", "青年", "大学", "校园", "学术", "研究", "图书馆", "实验室", "未来"]
}

# 文章角度库 - 让内容更加丰富
ARTICLE_ANGLES = {
    "数学": [
        "实用解题技巧", "常见错误分析", "思维训练方法", "生活应用实例",
        "趣味数学游戏", "考试重点解析", "学习方法指导", "知识点深度解析",
        "数学思维培养", "实际应用案例", "解题思路分析", "知识点串联"
    ],
    "语文": [
        "阅读方法指导", "写作技巧分享", "文学欣赏方法", "语言表达训练",
        "传统文化学习", "阅读理解策略", "作文构思方法", "诗词鉴赏技巧",
        "语言运用能力", "文学素养提升", "名著导读解析", "文化内涵解读"
    ],
    "英语": [
        "口语练习方法", "单词记忆技巧", "语法学习策略", "听力训练方法",
        "阅读能力提升", "写作技巧指导", "文化交流知识", "学习方法分享",
        "实际应用场景", "考试准备策略", "语言运用实践", "跨文化交际"
    ],
    "物理": [
        "实验操作方法", "物理原理应用", "问题解决方法", "思维训练方法",
        "物理模型建立", "物理公式推导", "实验设计思路", "物理现象解释",
        "物理与科技", "物理学习方法", "科学探究方法", "物理思维培养"
    ],
    "化学": [
        "实验安全操作", "化学反应原理", "化学计算技巧", "化学思维方法",
        "物质性质分析", "化学实验设计", "化学与生活", "化学学习方法",
        "化学现象解释", "化学方程式书写", "化学与环保", "科学探究素养"
    ],
    "专业课": [
        "专业基础理论", "专业实践应用", "专业学习方法", "专业前沿动态",
        "专业技能训练", "专业思维培养", "专业与就业", "专业与创新",
        "专业素养提升", "专业与行业", "专业与科技", "专业与未来"
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
    if "初中" in category or "高中" in category or "大学" in category:
        # 初中、高中、大学分类处理
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
        # 小学分类处理
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
    elif "物理" in subject:
        physics_tags = ["力学", "电磁学", "光学", "实验", "物理公式", "物理模型", "科学探究", "物理思维", "物理现象"]
        tags.update(random.sample(physics_tags, 4))
    elif "化学" in subject:
        chemistry_tags = ["化学反应", "化学实验", "化学方程式", "元素周期", "化学计算", "物质性质", "化学思维", "科学探究", "化学与生活"]
        tags.update(random.sample(chemistry_tags, 4))
    elif "专业课" in subject:
        major_tags = ["专业基础", "专业实践", "专业技能", "专业理论", "专业应用", "专业创新", "专业发展", "专业素养", "专业前沿"]
        tags.update(random.sample(major_tags, 4))
    
    # 5. 通用学习标签
    learning_tags = ["学习方法", "学习资料", "教学资源", "知识点总结", "教育指导", "学习计划", "复习方法", "考试技巧"]
    tags.update(random.sample(learning_tags, 3))
    
    # 6. 难度标签
    if "初中" in category or "高中" in category or "大学" in category:
        difficulty_tags = ["基础知识", "进阶学习", "提高训练", "深度解析", "专业拓展", "学术研究"]
    else:
        difficulty_tags = ["基础入门", "巩固练习", "提高训练", "进阶挑战", "拓展学习"]
    tags.add(random.choice(difficulty_tags))
    
    # 7. 资源类型标签
    resource_tags = ["电子版", "可打印", "练习题", "测试卷", "知识点", "学习计划", "教学视频", "互动学习"]
    tags.add(random.choice(resource_tags))
    
    # 8. 学习方法标签
    method_tags = ["记忆方法", "理解技巧", "应用实践", "举一反三", "思维训练", "自主学习", "探究学习", "合作学习"]
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
    if "初中" in category or "高中" in category or "大学" in category:
        # 初中、高中、大学分类处理
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
        # 小学分类处理
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
            "learning " + keywords[1],
            keywords[0] + " student",
            keywords[0] + " school"
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
    # 根据关键词选择合适的图片
    if "数学" in keywords or "计算" in keywords or "公式" in keywords:
        math_images = [
            "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=800",
            "https://images.unsplash.com/photo-1596495577886-d920f1fb7238?w=800",
            "https://images.unsplash.com/photo-1509228468518-180dd4864904?w=800",
            "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800"
        ]
        return random.choice(math_images)
    elif "语文" in keywords or "阅读" in keywords or "书籍" in keywords:
        chinese_images = [
            "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=800",
            "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800",
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800",
            "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=800"
        ]
        return random.choice(chinese_images)
    elif "英语" in keywords or "字母" in keywords or "单词" in keywords:
        english_images = [
            "https://images.unsplash.com/photo-1523580494863-6f3031224c94?w=800",
            "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=800",
            "https://images.unsplash.com/photo-1523580494863-6f3031224c94?w=800",
            "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=800"
        ]
        return random.choice(english_images)
    elif "物理" in keywords or "实验" in keywords or "科学" in keywords:
        physics_images = [
            "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=800",
            "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800",
            "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=800",
            "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800"
        ]
        return random.choice(physics_images)
    elif "化学" in keywords or "实验" in keywords or "实验室" in keywords:
        chemistry_images = [
            "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800",
            "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=800",
            "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800",
            "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=800"
        ]
        return random.choice(chemistry_images)
    elif "大学" in keywords or "学术" in keywords or "研究" in keywords:
        university_images = [
            "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=800",
            "https://images.unsplash.com/photo-1523580494863-6f3031224c94?w=800",
            "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=800",
            "https://images.unsplash.com/photo-1523580494863-6f3031224c94?w=800"
        ]
        return random.choice(university_images)
    else:
        # 默认返回学习相关图片
        education_images = [
            "https://images.unsplash.com/photo-1497636577773-f1231844b336?w=800",
            "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800",
            "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=800",
            "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=800"
        ]
        return random.choice(education_images)

def upload_image_to_wordpress(image_url, title, alt_text=""):
    """上传图片到WordPress并返回媒体ID和图片信息"""
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
            
            # 获取上传到WordPress后的图片URL
            media_url = media_data.get('source_url')
            if not media_url:
                media_url = media_data.get('guid', {}).get('rendered', image_url)
            
            print(f"✅ 图片上传成功，媒体ID: {media_id}")
            print(f"   WordPress图片URL: {media_url}")
            
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
            
            return {
                'media_id': media_id,
                'media_url': media_url,
                'title': title,
                'alt_text': alt_text or title
            }
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
    
    # 图片HTML模板 - 使用WordPress媒体库的URL
    image_template = '''
<div class="article-image" style="margin: 20px 0; text-align: center;">
    <img src="{image_url}" alt="{alt_text}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
    <p style="text-align: center; color: #666; font-size: 14px; margin-top: 8px; font-style: italic;">{caption}</p>
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
                image_url=image_info['media_url'],  # 使用WordPress媒体库的URL
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
    if "初中" in category or "高中" in category or "大学" in category:
        # 初中、高中、大学分类处理
        if "初中" in category:
            grade = "初中"
            subject = category[2:]
        elif "高中" in category:
            grade = "高中"
            subject = category[2:]
        else:  # 大学
            grade = "大学"
            subject = category[2:]
        
        if "初中" in category or "高中" in category:
            student_type = f"{grade}学生"
        else:
            student_type = f"{grade}学生"
    else:
        # 小学分类处理
        grade = category[:3]
        subject = category[3:]
        student_type = f"{grade}学生和家长"
    
    # 根据不同学段调整写作要求
    if "初中" in category or "高中" in category or "大学" in category:
        if "初中" in category:
            difficulty = "适合初中生阅读，有一定深度但仍需简明易懂"
        elif "高中" in category:
            difficulty = "适合高中生阅读，内容要深入且有深度"
        else:  # 大学
            difficulty = "适合大学生阅读，内容要有专业深度和学术性"
    else:
        difficulty = "适合小学生阅读，语言亲切易懂但专业"
    
    # 修改提示词：去除图片标记说明，强调紧凑格式
    prompt = f"""
请以专业教师的身份，为{student_type}写一篇关于'{topic}'的详细学习文章，重点角度是：{angle}。

写作要求：
1. 面向{student_type}，{difficulty}
2. 科目重点：{subject}，角度重点：{angle}
3. 字数：1200-1500字
4. 内容结构要求：
   - 开头：直接生动引入主题，说明学习重要性（不要有空行间隔）
   - 知识讲解：详细讲解核心知识点，包含2-3个具体例子
   - 方法指导：提供实用的学习方法和技巧
   - 实践应用：设计3-4个练习题或实践活动
   - 常见问题：分析学生常见错误和解决方法
   - 拓展学习：提供相关的拓展知识和资源推荐
   - 总结：回顾重点，给出学习建议

5. 包含丰富的实例和案例分析
6. 语言生动有趣，适合{student_type}阅读但内容专业
7. 使用HTML格式，包含适当的标题和段落
8. 特别注意：文章开头不要有过多空行，标题和正文之间最多只能有1行空行
9. 文章内容要紧凑，段落之间使用正常的间距

请直接开始文章写作，不要有任何前言或说明：
    """
    
    data = {
        "model": "glm-4",
        "messages": [
            {
                "role": "system", 
                "content": f"你是一个经验丰富的{grade}教师，擅长用适当的语言解释复杂概念，能够激发学生的学习兴趣，同时保持内容的专业性和深度。特别注意：文章开头要紧凑，不要有多余空行。"
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
            
            # 清理多余的空行：将连续3个或以上的换行符替换为2个
            cleaned_content = re.sub(r'\n{3,}', '\n\n', content)
            # 清理段落标签之间的多余空行
            cleaned_content = re.sub(r'(</p>)\s*(\n\s*){3,}(<p>|</?h[1-6]>)', r'\1\n\n\3', cleaned_content)
            
            if cleaned_content != content:
                print(f"✅ 已清理多余空行，从{len(content)}字符减少到{len(cleaned_content)}字符")
            
            return cleaned_content
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"错误详情: {response.text}")
            return None
    except Exception as e:
        print(f"❌ AI生成失败: {e}")
        return None

def generate_seo_data(title, content, tags):
    """生成Yoast SEO相关数据"""
    try:
        # 提取SEO标题
        site_name = "GoGewu格物智库"
        seo_title = f"{title} - {site_name}"
        
        # 从内容中提取纯文本前155个字符作为描述
        plain_text = re.sub(r'<[^>]+>', '', content)
        plain_text = re.sub(r'\s+', ' ', plain_text)  # 将多个空格/换行符替换为单个空格
        plain_text = plain_text.strip()
        
        # 截取合适的描述长度
        if len(plain_text) > 155:
            # 寻找句子结束点
            if '.' in plain_text[:155]:
                end_pos = plain_text[:155].rfind('.') + 1
                seo_description = plain_text[:end_pos].strip()
            else:
                seo_description = plain_text[:150].strip() + "..."
        else:
            seo_description = plain_text
        
        # 生成焦点关键词（从标题或标签中选择）
        focus_keyword = ""
        if tags and len(tags) > 0:
            # 优先选择较短的标签作为关键词
            short_tags = [tag for tag in tags if len(tag) <= 6]
            if short_tags:
                focus_keyword = short_tags[0]
            else:
                focus_keyword = tags[0]
        else:
            # 从标题中提取关键词
            title_words = jieba.lcut(title)
            focus_keyword = title_words[0] if title_words else title[:4]
        
        # 创建完整的Yoast SEO数据结构
        seo_data = {
            "yoast_wpseo_title": seo_title,
            "yoast_wpseo_metadesc": seo_description,
            "yoast_wpseo_focuskw": focus_keyword,
            "yoast_wpseo_meta-robots-noindex": "0",  # 0表示不禁止索引
            "yoast_wpseo_meta-robots-nofollow": "0",  # 0表示允许跟踪
            "yoast_wpseo_canonical": "",  # 留空表示使用默认
            "yoast_wpseo_opengraph-title": seo_title,
            "yoast_wpseo_opengraph-description": seo_description,
            "yoast_wpseo_opengraph-image": "",
            "yoast_wpseo_twitter-title": seo_title,
            "yoast_wpseo_twitter-description": seo_description,
            "yoast_wpseo_twitter-image": "",
        }
        
        print(f"🔍 生成SEO数据:")
        print(f"  - SEO标题: {seo_title}")
        print(f"  - SEO描述: {seo_description}")
        print(f"  - 焦点关键词: {focus_keyword}")
        
        return seo_data
        
    except Exception as e:
        print(f"❌ 生成SEO数据失败: {e}")
        return None

def update_yoast_seo(post_id, seo_data):
    """更新文章的Yoast SEO信息"""
    try:
        update_url = WORDPRESS_URL.rstrip('/') + f'/wp-json/wp/v2/posts/{post_id}'
        auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
        
        if not seo_data:
            print("⚠️  没有SEO数据需要更新")
            return False
        
        # WordPress REST API中，Yoast SEO数据通常通过meta字段设置
        update_data = {
            'meta': seo_data
        }
        
        response = requests.post(update_url, json=update_data, auth=auth, timeout=10)
        
        if response.status_code == 200:
            print("✅ Yoast SEO信息更新成功")
            return True
        else:
            print(f"⚠️  Yoast SEO信息更新失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 更新Yoast SEO异常: {e}")
        return False

def fix_existing_post_seo(post_id, title, content, tags):
    """修复已有文章的SEO信息"""
    try:
        print(f"🔧 修复文章SEO信息: ID={post_id}, 标题='{title}'")
        
        # 生成正确的SEO数据
        seo_data = generate_seo_data(title, content, tags)
        
        if not seo_data:
            print("❌ 无法生成SEO数据")
            return False
        
        # 更新SEO信息
        success = update_yoast_seo(post_id, seo_data)
        
        if success:
            print(f"✅ 文章ID {post_id} 的SEO信息已修复")
            return True
        else:
            print(f"❌ 无法修复文章ID {post_id} 的SEO信息")
            return False
            
    except Exception as e:
        print(f"❌ 修复SEO信息异常: {e}")
        return False

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
                
                # 获取上传结果，包含media_id和media_url
                upload_result = upload_image_to_wordpress(image_url, f"{topic}_{image_type}", alt_text)
                
                if upload_result:
                    images_data.append({
                        'media_url': upload_result['media_url'],  # 使用WordPress媒体库的URL
                        'alt_text': alt_text,
                        'caption': caption,
                        'media_id': upload_result['media_id'],
                        'type': image_type
                    })
                    print(f"✅ 成功处理图片 {i+1}: {image_type}")
                
                # 如果是第一张图片，设置为特色图片
                if i == 0 and upload_result and 'media_id' in upload_result:
                    add_featured_image(post_id, upload_result['media_id'])
            
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
    """发布到WordPress并自动添加标签和SEO"""
    try:
        api_url = WORDPRESS_URL.rstrip('/') + '/wp-json/wp/v2/posts'
        
        # 生成智能标签名称
        tag_names = generate_smart_tags(category, content, title)
        
        # 将标签名称转换为标签ID
        tag_ids = get_tag_ids(tag_names)
        
        auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
        
        # 获取分类ID
        category_id = CATEGORY_MAP.get(category, 1)
        
        # 生成SEO数据
        seo_data = generate_seo_data(title, content, tag_names)
        
        # 构建文章数据
        post_data = {
            'title': title,
            'content': content,
            'status': 'draft',  # 先保存为草稿
            'categories': [category_id],
            'slug': slug
        }
        
        # 添加标签
        if tag_ids:
            post_data['tags'] = tag_ids
        
        # 添加Yoast SEO数据
        if seo_data:
            post_data['meta'] = seo_data
        
        print(f"📤 发布数据准备完成:")
        print(f"  - 标题: {title}")
        print(f"  - 分类: {category}(ID:{category_id})")
        print(f"  - 别名: {slug}")
        print(f"  - 标签ID数: {len(tag_ids)}")
        print(f"  - 包含SEO数据: {'是' if seo_data else '否'}")
        
        # 发布文章
        response = requests.post(api_url, json=post_data, auth=auth, timeout=30)
        print(f"🌐 WordPress响应状态: {response.status_code}")
        
        if response.status_code == 201:
            post_data = response.json()
            post_id = post_data['id']
            print(f"✅ 文章保存为草稿成功！文章ID: {post_id}")
            
            # 处理图片（在文章发布后）
            print("🖼️  开始处理文章图片...")
            updated_content, images_data = process_images_for_article(category, title, content, post_id)
            
            # 更新文章内容，包含图片，并发布
            update_needed = False
            update_data = {'status': 'publish'}
            
            if updated_content != content and images_data:
                update_data['content'] = updated_content
                update_needed = True
            
            if update_needed:
                update_response = requests.post(
                    f"{api_url}/{post_id}",
                    json=update_data,
                    auth=auth,
                    timeout=10
                )
                if update_response.status_code == 200:
                    print("✅ 文章已更新包含图片并发布")
                else:
                    print(f"⚠️  文章内容更新失败: {update_response.status_code}")
                    # 如果更新失败，至少将草稿发布
                    update_data = {'status': 'publish'}
                    update_response = requests.post(
                        f"{api_url}/{post_id}",
                        json=update_data,
                        auth=auth,
                        timeout=10
                    )
                    if update_response.status_code == 200:
                        print("✅ 文章已发布（不含图片更新）")
            else:
                # 如果没有图片更新，直接发布草稿
                update_response = requests.post(
                    f"{api_url}/{post_id}",
                    json=update_data,
                    auth=auth,
                    timeout=10
                )
                if update_response.status_code == 200:
                    print("✅ 文章已发布（不含图片）")
            
            return True, post_id, tag_names
        else:
            print(f"❌ 发布失败: {response.text}")
            return False, None, None
            
    except Exception as e:
        print(f"❌ 发布异常: {e}")
        return False, None, None

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
        # 如果学科不在角度库中，使用通用角度
        angle_list = ["学习方法指导", "知识深度解析", "实践应用案例", "考试重点解析"]
        angle = random.choice(angle_list)
    
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
    success, post_id, tag_names = post_to_wordpress_with_tags(topic, content, category, slug)
    
    if success:
        print("🎉 文章发布成功！")
        
        # 如果需要修复已有的文章（例如您提到的文章）
        print("\n⚠️  如果需要修复已有文章的SEO信息，请运行修复函数")
        print("   调用方式: fix_existing_post_seo(post_id, title, content, tags)")
        
        return True
    else:
        print("💥 文章发布失败")
        return False

def fix_problematic_article():
    """修复有问题的文章"""
    print("🔧 开始修复有问题的文章...")
    
    # 您需要替换以下信息为实际值
    problem_post_id = 12345  # 替换为您的文章ID
    problem_title = "探索神秘的'利润'世界"  # 替换为正确的标题
    problem_content = "亲爱的小朋友们和家长们，你们知道什么是'利润'吗？它就像是我们小口袋里的零花钱..."  # 替换为实际内容
    problem_tags = ["利润", "数学", "一年级数学", "计算", "应用题"]  # 替换为实际标签
    
    success = fix_existing_post_seo(problem_post_id, problem_title, problem_content, problem_tags)
    
    if success:
        print("✅ 问题文章已修复")
    else:
        print("❌ 无法修复问题文章")

if __name__ == "__main__":
    # 正常发布新文章
    success = main()
    
    # 如果需要修复已有的问题文章，取消下面的注释并填写正确信息
    # fix_problematic_article()
    
    exit(0 if success else 1)
