import requests
import random
import os
from datetime import datetime
import base64

# 配置
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
WORDPRESS_URL = os.getenv('WORDPRESS_URL')  # 应该是 https://你的网站.com
WORDPRESS_USER = os.getenv('WORDPRESS_USER')
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD')  # 应用密码

# 文章主题库
TOPICS = [
    "如何提高工作效率的10个技巧",
    "人工智能对日常生活的影响", 
    "健康饮食的简单实践方法",
    "学习新技能的有效途径",
    "数字时代的个人成长策略"
]

def get_zhipu_ai_content(topic):
    """使用智谱AI生成文章"""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {ZHIPU_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "glm-4",
        "messages": [
            {
                "role": "user", 
                "content": f"请写一篇关于'{topic}'的博客文章，800字左右，要有实用价值，使用自然段落格式"
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
            print(f"错误详情: {response.text}")
            return None
    except Exception as e:
        print(f"AI生成失败: {e}")
        return None

def post_to_wordpress_app_password(title, content):
    """使用 WordPress 应用密码发布"""
    try:
        # 构建 REST API 端点
        api_url = WORDPRESS_URL.rstrip('/') + '/wp-json/wp/v2/posts'
        print(f"发布到: {api_url}")
        
        # 使用应用密码认证
        auth = (WORDPRESS_USER, WORDPRESS_PASSWORD)
        
        post_data = {
            'title': title,
            'content': content,
            'status': 'publish',  # 直接发布
            'categories': [1]     # 默认分类
        }
        
        response = requests.post(api_url, json=post_data, auth=auth, timeout=30)
        print(f"WordPress响应状态: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ 文章发布成功！")
            return True
        elif response.status_code == 401:
            print("❌ 认证失败，请检查应用密码")
            return False
        elif response.status_code == 404:
            print("❌ REST API 未找到，请检查固定链接设置")
            return False
        else:
            print(f"❌ 发布失败，响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 发布失败: {e}")
        return False

def main():
    print("🚀 开始自动发布流程...")
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查必要的环境变量
    if not all([ZHIPU_API_KEY, WORDPRESS_URL, WORDPRESS_USER, WORDPRESS_PASSWORD]):
        print("❌ 错误：缺少必要的环境变量配置")
        return False
    
    # 随机选择主题
    topic = random.choice(TOPICS)
    print(f"📝 生成主题: {topic}")
    
    # 获取AI生成内容
    print("🤖 正在调用AI生成内容...")
    content = get_zhipu_ai_content(topic)
    
    if not content:
        print("❌ 内容生成失败")
        return False
        
    print("✅ 内容生成成功")
    
    # 发布到WordPress（使用应用密码）
    print("🌐 正在通过应用密码发布到 WordPress...")
    success = post_to_wordpress_app_password(topic, content)
    
    if success:
        print("🎉 文章发布成功！")
        return True
    else:
        print("💥 文章发布失败")
        return False

if __name__ == "__main__":
    main()
