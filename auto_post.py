import requests
import random
import os
import string
from requests.auth import HTTPBasicAuth

# --- 1. 海量主题库扩展 (覆盖全学段) ---
TOPICS = {
    "小学": {
        "一年级语文": ["拼音字母表背诵技巧", "看图写话基本句式"],
        "三年级数学": ["两位数乘法口算卡", "认识周长与面积"],
    },
    "初中": {
        "物理": ["初二物理：浮力计算实验", "电路图画法详解"],
        "数学": ["全等三角形判定定理", "勾股定理应用题"],
    },
    "高中": {
        "数学": ["圆锥曲线离心率求解模板", "导数单调性研究"],
        "物理": ["牛顿第二定律综合应用", "电磁感应楞次定律"],
    },
    "大学": {
        "高等数学": ["微积分：泰勒公式展开", "拉格朗日中值定理证明"],
        "专业课": ["Python数据结构：平衡二叉树", "宏观经济IS-LM模型分析"],
    }
}

# --- 2. 配置信息 (请务必使用纯英文用户名) ---
ZHIPU_API_KEY = str(os.getenv('ZHIPU_API_KEY', "你的APIKey")).strip()
WORDPRESS_URL = "https://www.gogewu.com/wp-json/wp/v2"
# ⚠️ 注意：这里的用户名必须是纯英文，不能带中文
WORDPRESS_USER = "your_english_username" 
WORDPRESS_PASSWORD = "your_application_password"

CATEGORY_MAP = {"小学": 6, "初中": 774, "高中": 782, "大学": 790}

# --- 3. 修复后的发布逻辑 ---

def auto_post():
    level_name = random.choice(list(TOPICS.keys()))
    subject_name = random.choice(list(TOPICS[level_name].keys()))
    topic = random.choice(TOPICS[level_name][subject_name])
    
    print(f"🚀 正在准备: {level_name} - {topic}")

    # 获取AI正文
    content = get_ai_content(topic, level_name)
    if not content: return

    # 1. 强制获取图片并上传 (解决文中无图)
    media_id, media_url = upload_media(subject_name, topic)

    # 2. 修复间距：在 HTML 开头注入 CSS (解决间距太远)
    style_fix = '<style>.entry-content { margin-top: -40px !important; } .entry-header { margin-bottom: 0 !important; }</style>'
    
    # 3. 强行在正文第一段前插入图片标签
    if media_url:
        img_html = f'<p style="text-align:center;"><img src="{media_url}" alt="{topic}" style="border-radius:12px; width:100%;" /></p>'
        content = style_fix + img_html + content
    else:
        content = style_fix + content

    # 4. 构造发布数据 (包含下载框 Meta)
    post_data = {
        'title': f"【{subject_name}】{topic}",
        'content': content,
        'status': 'publish',
        'categories': [CATEGORY_MAP.get(level_name, 1)],
        'featured_media': media_id if media_id else 0,
        'meta': {
            'download_link': 'https://www.gogewu.com/download-center/',
            'download_code': '8888'
        }
    }

    # 使用 auth 认证前确保用户名是英文，防止 UnicodeEncodeError
    auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    try:
        response = requests.post(f"{WORDPRESS_URL}/posts", json=post_data, auth=auth, timeout=30)
        if response.status_code == 201:
            print(f"✅ 发布成功！文章ID: {response.json()['id']}")
        else:
            print(f"❌ 发布失败: {response.text}")
    except Exception as e:
        print(f"❌ 网络请求异常: {e}")

# (辅助函数 get_ai_content 和 upload_media 逻辑同前，确保 key 无中文即可)
