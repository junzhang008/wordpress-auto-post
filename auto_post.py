import requests
import random
import os
import string
from datetime import datetime
from requests.auth import HTTPBasicAuth

# 配置
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
WORDPRESS_URL = os.getenv('WORDPRESS_URL')
WORDPRESS_USER = os.getenv('WORDPRESS_USER')
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD')

# 分类映射（分类名称 -> 分类ID）
# 你需要先在WordPress后台找到每个分类的ID，然后替换下面的数字
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

# 各年级各科目的主题库
TOPICS_BY_CATEGORY = {
    "一年级数学": [
        "10以内加减法练习题",
        "认识数字1-100的方法",
        "小学数学图形认识入门",
        "一年级数学应用题解析",
        "数学思维训练小游戏"
    ],
    "二年级数学": [
        "乘法口诀记忆技巧",
        "100以内加减法练习",
        "认识时钟和时间",
        "长度单位换算方法",
        "数学逻辑思维训练"
    ],
    "三年级数学": [
        "两位数乘除法技巧",
        "分数的初步认识",
        "面积和周长计算",
        "数学应用题解题思路",
        "数学趣味游戏"
    ],
    "四年级数学": [
        "小数加减法练习",
        "三角形和四边形性质",
        "数学运算定律",
        "数据统计图表分析",
        "数学思维拓展训练"
    ],
    "五年级数学": [
        "分数乘除法技巧",
        "立体图形认识",
        "方程初步解法",
        "比例和百分比",
        "数学竞赛题目解析"
    ],
    "六年级数学": [
        "代数式简化方法",
        "几何图形面积计算",
        "概率初步知识",
        "数学思维导图应用",
        "小升初数学备考"
    ],
    "一年级语文": [
        "拼音学习方法",
        "汉字笔画书写技巧",
        "看图写话训练",
        "儿童诗歌朗诵",
        "语文阅读兴趣培养"
    ],
    "二年级语文": [
        "词语积累方法",
        "句子成分认识",
        "短文阅读理解",
        "写作基础训练",
        "古诗词启蒙"
    ],
    "三年级语文": [
        "段落写作技巧",
        "修辞手法认识",
        "阅读理解策略",
        "作文开头方法",
        "成语故事学习"
    ],
    "四年级语文": [
        "记叙文写作指导",
        "文言文入门学习",
        "阅读理解深度训练",
        "作文结构安排",
        "文学常识积累"
    ],
    "五年级语文": [
        "议论文写作基础",
        "古诗词鉴赏方法",
        "阅读理解技巧",
        "作文修改提升",
        "语文知识体系构建"
    ],
    "六年级语文": [
        "各类文体写作",
        "文言文翻译技巧",
        "阅读理解综合训练",
        "作文立意深化",
        "小升初语文备考"
    ],
    "一年级英语": [
        "英语字母学习游戏",
        "基础英语单词记忆",
        "简单英语对话练习",
        "英语儿歌学习",
        "英语学习兴趣培养"
    ],
    "二年级英语": [
        "英语单词分类记忆",
        "基础句型练习",
        "英语绘本阅读",
        "英语发音纠正",
        "英语学习习惯养成"
    ],
    "三年级英语": [
        "英语语法入门",
        "英语阅读理解",
        "英语写作基础",
        "英语听力训练",
        "英语学习策略"
    ],
    "四年级英语": [
        "英语时态学习",
        "英语阅读理解提升",
        "英语写作技巧",
        "英语口语练习",
        "英语学习方法"
    ],
    "五年级英语": [
        "英语复合句学习",
        "英语阅读策略",
        "英语写作训练",
        "英语听力技巧",
        "英语应试准备"
    ],
    "六年级英语": [
        "英语语法综合",
        "英语阅读进阶",
        "英语写作提升",
        "英语口语表达",
        "小升初英语备考"
    ]
}

def generate_random_slug(length=8):
    """生成随机别名"""
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def get_zhipu_ai_content(topic, category):
    """使用智谱AI生成文章"""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {ZHIPU_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 根据分类定制提示词
    grade = category[:3]  # 提取年级
    subject = category[3:]  # 提取科目
    
    prompt = f"""
    请以专业小学教师的角度，写一篇关于'{topic}'的详细文章。
    
    要求：
    1. 面向{grade}学生和家长
    2. 科目：{subject}
    3. 字数800-1000字
    4. 包含具体的学习方法、练习题或实例
    5. 语言亲切易懂，有实用性
    6. 结构清晰：引言、方法介绍、实例分析、总结建议
    7. 包含2-3个实用的学习技巧
    
    请开始写作：
    """
    
    data = {
        "model": "glm-4",
        "messages": [
            {
                "role": "system", 
                "content": "你是一个经验丰富的小学教师，擅长用简单易懂的语言解释复杂概念。"
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            print(f"API请求失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"AI生成失败: {e}")
        return None

def post_to_wordpress(title, content, category, slug):
    """发布到WordPress指定分类"""
    try:
        api_url = WORDPRESS_URL.rstrip('/') + '/wp-json/wp/v2/posts'
        
        # 使用 HTTPBasicAuth
        auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
        
        # 获取分类ID
        category_id = CATEGORY_MAP.get(category, 1)  # 默认分类ID为1
        
        post_data = {
            'title': title,
            'content': content,
            'status': 'publish',
            'categories': [category_id],
            'slug': slug
        }
        
        response = requests.post(api_url, json=post_data, auth=auth, timeout=30)
        print(f"发布到分类 [{category}]，响应状态: {response.status_code}")
        
        if response.status_code == 201:
            print(f"✅ 文章发布成功！别名: {slug}")
            return True
        else:
            print(f"❌ 失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False

def main():
    print("🚀 开始批量发布文章...")
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查必要的环境变量
    if not all([ZHIPU_API_KEY, WORDPRESS_URL, WORDPRESS_USER, WORDPRESS_PASSWORD]):
        print("❌ 错误：缺少必要的环境变量配置")
        return False
    
    # 每天发布3-5篇文章
    article_count = random.randint(3, 5)
    print(f"📊 今天计划发布 {article_count} 篇文章")
    
    success_count = 0
    
    # 随机选择要发布的分类
    available_categories = list(TOPICS_BY_CATEGORY.keys())
    selected_categories = random.sample(available_categories, min(article_count, len(available_categories)))
    
    for i, category in enumerate(selected_categories, 1):
        print(f"\n--- 正在处理第 {i} 篇文章 ---")
        
        # 从该分类中随机选择主题
        topic = random.choice(TOPICS_BY_CATEGORY[category])
        print(f"📝 分类: {category}, 主题: {topic}")
        
        # 生成随机别名
        slug = generate_random_slug(random.randint(6, 10))
        print(f"🔗 生成别名: {slug}")
        
        # 获取AI生成内容
        print("🤖 正在调用AI生成内容...")
        content = get_zhipu_ai_content(topic, category)
        
        if not content:
            print("❌ 内容生成失败，跳过此文章")
            continue
            
        print("✅ 内容生成成功")
        
        # 发布到WordPress
        print("🌐 正在发布到 WordPress...")
        success = post_to_wordpress(topic, content, category, slug)
        
        if success:
            success_count += 1
            print(f"🎉 第 {i} 篇文章发布成功！")
        else:
            print(f"💥 第 {i} 篇文章发布失败")
        
        # 添加延迟，避免请求过于频繁
        if i < len(selected_categories):
            delay = random.randint(5, 10)
            print(f"⏳ 等待 {delay} 秒后继续...")
            import time
            time.sleep(delay)
    
    print(f"\n📈 批量发布完成！成功: {success_count}/{article_count} 篇")
    return success_count > 0

if __name__ == "__main__":
    main()
