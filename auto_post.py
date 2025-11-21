import requests
import random
import os
from datetime import datetime
import base64

# 配置
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
WORDPRESS_URL = os.getenv('WORDPRESS_URL')
WORDPRESS_USER = os.getenv('WORDPRESS_USER')
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD')

def debug_wordpress_connection():
    """调试 WordPress 连接"""
    print("=== WordPress 连接调试 ===")
    print(f"URL: {WORDPRESS_URL}")
    print(f"用户: {WORDPRESS_USER}")
    print(f"密码长度: {len(WORDPRESS_PASSWORD) if WORDPRESS_PASSWORD else 0}")
    
    # 测试 REST API 端点
    test_url = WORDPRESS_URL.rstrip('/') + '/wp-json/'
    try:
        response = requests.get(test_url, timeout=10)
        print(f"REST API 状态: {response.status_code}")
    except Exception as e:
        print(f"REST API 测试失败: {e}")
    
    print("=== 调试结束 ===")

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
                "content": f"请写一篇关于'{topic}'的博客文章，600字左右，要有实用价值"
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

def post_to_wordpress_simple(title, content):
    """简化版 WordPress 发布"""
    try:
        api_url = WORDPRESS_URL.rstrip('/') + '/wp-json/wp/v2/posts'
        print(f"发布到: {api_url}")
        
        # 使用 Basic Auth
        auth = (WORDPRESS_USER, WORDPRESS_PASSWORD)
        
        # 简化文章数据
        post_data = {
            'title': title,
            'content': content,
            'status': 'draft'  # 先存为草稿，测试成功后再改为 publish
        }
        
        print("发送请求...")
        response = requests.post(api_url, json=post_data, auth=auth, timeout=30)
        print(f"响应状态: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 201:
            print("✅ 文章创建成功！")
            return True
        else:
            print(f"❌ 失败响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def main():
    print("🚀 开始自动发布流程...")
    
    # 调试连接
    debug_wordpress_connection()
    
    # 检查必要的环境变量
    if not all([ZHIPU_API_KEY, WORDPRESS_URL, WORDPRESS_USER, WORDPRESS_PASSWORD]):
        print("❌ 错误：缺少必要的环境变量配置")
        return False
    
    # 使用固定主题测试
    topic = "测试文章：技术发展趋势"
    print(f"📝 测试主题: {topic}")
    
    # 获取AI生成内容
    print("🤖 正在调用AI生成内容...")
    content = get_zhipu_ai_content(topic)
    
    if not content:
        print("❌ 内容生成失败")
        return False
        
    print("✅ 内容生成成功")
    
    # 发布到WordPress
    print("🌐 正在发布到 WordPress...")
    success = post_to_wordpress_simple(topic, content)
    
    if success:
        print("🎉 测试成功！")
        return True
    else:
        print("💥 测试失败")
        return False

if __name__ == "__main__":
    main()
