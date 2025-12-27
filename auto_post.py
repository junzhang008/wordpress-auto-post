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

# ... [前面的导入和主题库代码保持不变] ...

def generate_seo_data(title, content, tags, category):
    """生成正确的SEO数据，确保与内容匹配"""
    try:
        # 提取SEO标题 - 使用文章实际标题
        site_name = "GoGewu格物智库"
        seo_title = f"{title} - {site_name}"
        
        # 从内容中提取正确的SEO描述
        # 首先移除所有HTML标签
        plain_text = re.sub(r'<[^>]+>', '', content)
        # 移除多余空格和换行
        plain_text = re.sub(r'\s+', ' ', plain_text).strip()
        
        # 截取合适长度的描述
        if len(plain_text) > 155:
            # 尝试在句子结束处截断
            end_positions = [
                plain_text[:155].rfind('。') + 1 if plain_text[:155].rfind('。') > 0 else None,
                plain_text[:155].rfind('！') + 1 if plain_text[:155].rfind('！') > 0 else None,
                plain_text[:155].rfind('？') + 1 if plain_text[:155].rfind('？') > 0 else None,
                plain_text[:155].rfind('；') + 1 if plain_text[:155].rfind('；') > 0 else None,
                150
            ]
            
            # 找到第一个有效的结束位置
            end_pos = None
            for pos in end_positions:
                if pos is not None and pos > 50:  # 确保有足够的内容
                    end_pos = pos
                    break
            
            if end_pos:
                seo_description = plain_text[:end_pos].strip()
            else:
                seo_description = plain_text[:150].strip() + "..."
        else:
            seo_description = plain_text
        
        # 如果描述还是太长或太短，进行调整
        if len(seo_description) < 50:
            seo_description = f"本文详细讲解{title}的概念、应用和解题方法，帮助{category[:3]}学生掌握相关知识。"
        elif len(seo_description) > 160:
            seo_description = seo_description[:157] + "..."
        
        # 生成焦点关键词
        if tags and len(tags) > 0:
            # 优先从标题中提取关键词
            title_keywords = extract_keywords_from_title(title)
            if title_keywords:
                focus_keyword = title_keywords[0]
            else:
                # 从标签中选择
                focus_keyword = tags[0]
        else:
            focus_keyword = title[:6] if len(title) > 6 else title
        
        # 根据分类确定文章分类
        if "数学" in category:
            article_type = "数学学习"
        elif "语文" in category:
            article_type = "语文学习"
        elif "英语" in category:
            article_type = "英语学习"
        elif "物理" in category:
            article_type = "物理学习"
        elif "化学" in category:
            article_type = "化学学习"
        else:
            article_type = "学习资料"
        
        # 创建完整的Yoast SEO数据结构
        seo_data = {
            "yoast_wpseo_title": seo_title,
            "yoast_wpseo_metadesc": seo_description,
            "yoast_wpseo_focuskw": focus_keyword,
            "yoast_wpseo_meta-robots-noindex": "0",
            "yoast_wpseo_meta-robots-nofollow": "0",
            "yoast_wpseo_canonical": "",
            "yoast_wpseo_opengraph-title": seo_title,
            "yoast_wpseo_opengraph-description": seo_description,
            "yoast_wpseo_twitter-title": seo_title,
            "yoast_wpseo_twitter-description": seo_description,
            "yoast_wpseo_schema_article_type": "BlogPosting",
            "yoast_wpseo_schema_page_type": "WebPage",
        }
        
        print(f"🔍 生成的SEO数据:")
        print(f"  - SEO标题: {seo_title}")
        print(f"  - SEO描述: {seo_description[:60]}...")
        print(f"  - 焦点关键词: {focus_keyword}")
        print(f"  - 文章类型: {article_type}")
        
        return seo_data
        
    except Exception as e:
        print(f"❌ 生成SEO数据失败: {e}")
        # 返回基础SEO数据
        return {
            "yoast_wpseo_title": f"{title} - GoGewu格物智库",
            "yoast_wpseo_metadesc": f"本文详细讲解{title}的概念、应用和解题方法，帮助{category[:3]}学生掌握相关知识。",
            "yoast_wpseo_focuskw": title[:4] if len(title) > 4 else title,
            "yoast_wpseo_meta-robots-noindex": "0",
            "yoast_wpseo_meta-robots-nofollow": "0",
        }

def update_seo_after_publish(post_id, title, content, tags, category):
    """发布文章后单独更新SEO信息，确保正确性"""
    try:
        print(f"🔧 正在为文章ID {post_id} 更新SEO信息...")
        
        # 生成正确的SEO数据
        seo_data = generate_seo_data(title, content, tags, category)
        
        if not seo_data:
            print(f"❌ 无法生成SEO数据，跳过更新")
            return False
        
        # 获取文章当前信息进行验证
        api_url = WORDPRESS_URL.rstrip('/') + f'/wp-json/wp/v2/posts/{post_id}'
        auth = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
        
        # 先获取当前文章数据
        response = requests.get(api_url, auth=auth, timeout=10)
        if response.status_code != 200:
            print(f"❌ 无法获取文章数据: {response.status_code}")
            return False
        
        current_post = response.json()
        current_title = current_post.get('title', {}).get('rendered', '')
        
        # 验证标题是否匹配
        print(f"  📝 验证标题:")
        print(f"    - 当前标题: {re.sub(r'<[^>]+>', '', current_title)}")
        print(f"    - 目标标题: {title}")
        
        # 更新SEO数据
        update_data = {
            'meta': seo_data
        }
        
        update_response = requests.post(api_url, json=update_data, auth=auth, timeout=10)
        
        if update_response.status_code == 200:
            print(f"✅ SEO信息更新成功！")
            print(f"   - 标题: {seo_data.get('yoast_wpseo_title')}")
            print(f"   - 描述: {seo_data.get('yoast_wpseo_metadesc')[:60]}...")
            print(f"   - 关键词: {seo_data.get('yoast_wpseo_focuskw')}")
            return True
        else:
            print(f"❌ SEO信息更新失败: {update_response.status_code}")
            print(f"   响应: {update_response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ 更新SEO信息异常: {e}")
        return False

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
        seo_data = generate_seo_data(title, content, tag_names, category)
        
        # 清理HTML内容，确保格式正确
        # 移除可能的多余空行
        cleaned_content = re.sub(r'\n{3,}', '\n\n', content)
        # 确保内容以正确的HTML格式开始
        if not cleaned_content.strip().startswith('<'):
            cleaned_content = f"<p>{cleaned_content.strip()}</p>"
        
        # 构建文章数据
        post_data = {
            'title': title,
            'content': cleaned_content,
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
        print(f"  - 标签数量: {len(tag_ids)}")
        print(f"  - SEO标题: {seo_data.get('yoast_wpseo_title') if seo_data else '无'}")
        
        # 验证数据一致性
        print(f"🔍 数据一致性检查:")
        print(f"  标题匹配: {'✅ 正确' if title in seo_data.get('yoast_wpseo_title', '') else '❌ 错误'}")
        print(f"  分类匹配: {'✅ 正确' if category[:2] in seo_data.get('yoast_wpseo_title', '') else '⚠️ 可能不匹配'}")
        
        # 发布文章
        response = requests.post(api_url, json=post_data, auth=auth, timeout=30)
        print(f"🌐 WordPress响应状态: {response.status_code}")
        
        if response.status_code == 201:
            post_data = response.json()
            post_id = post_data['id']
            print(f"✅ 文章保存为草稿成功！文章ID: {post_id}")
            print(f"🔗 文章链接: {WORDPRESS_URL.rstrip('/')}/?p={post_id}")
            
            # 处理图片（在文章发布后）
            print("🖼️  开始处理文章图片...")
            updated_content, images_data = process_images_for_article(category, title, cleaned_content, post_id)
            
            # 更新文章内容，包含图片，并发布
            update_needed = False
            update_data = {'status': 'publish'}
            
            if updated_content != cleaned_content and images_data:
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
            
            # 发布后再次验证和更新SEO信息
            print("🔍 发布后SEO信息验证...")
            time.sleep(2)  # 等待WordPress处理
            
            seo_updated = update_seo_after_publish(post_id, title, updated_content or cleaned_content, tag_names, category)
            if seo_updated:
                print("✅ SEO信息已正确设置")
            else:
                print("⚠️  SEO信息可能未正确设置，请手动检查")
            
            return True, post_id, tag_names
        else:
            print(f"❌ 发布失败: {response.text[:200]}")
            return False, None, None
            
    except Exception as e:
        print(f"❌ 发布异常: {e}")
        return False, None, None

def fix_specific_article():
    """修复具体的文章SEO问题"""
    print("🔧 开始修复特定的文章SEO问题...")
    
    # 根据您的图片，我需要知道：
    # 1. 文章ID（从URL或WordPress后台获取）
    # 2. 正确的标题和内容
    
    # 示例：修复文章ID为12345的文章
    # 请替换为实际的ID和内容
    article_id = 12345  # 请替换为实际的文章ID
    correct_title = "简单的利润问题"
    correct_content = """
    <h2>探索神秘的"利润"世界</h2>
    <p>亲爱的小朋友们和家长们，你们知道什么是"利润"吗？它就像是我们小口袋里的零花钱，当我们帮助妈妈做家务时，妈妈可能会给我们一些奖励。在这个故事里，我们要学习的"利润"，就是通过做"小生意"赚到的钱哦！</p>
    <p>今天，让我们一起探索这个有趣的"利润"世界吧！</p>
    <h3>什么是利润？</h3>
    <p>利润就是卖出东西后，赚到的钱。比如，小明花5元买了一支笔，然后以8元的价格卖给了同学。那么，小明的利润就是8 - 5 = 3元。</p>
    <h3>利润怎么计算？</h3>
    <p>计算利润的公式很简单：利润 = 卖出价格 - 成本价格</p>
    <p>让我们来看几个例子...</p>
    """
    correct_tags = ["利润", "数学", "一年级数学", "计算题", "应用题", "基础入门", "教学方法", "家长指导"]
    correct_category = "一年级数学"
    
    success = update_seo_after_publish(article_id, correct_title, correct_content, correct_tags, correct_category)
    
    if success:
        print(f"✅ 文章ID {article_id} 的SEO信息已修复")
        print(f"🔗 请访问链接查看: {WORDPRESS_URL.rstrip('/')}/?p={article_id}")
    else:
        print(f"❌ 无法修复文章ID {article_id} 的SEO信息")
    
    return success

# 在main函数中，可以选择修复或创建新文章
def main():
    print("🚀 开始自动发布文章流程...")
    print(f"📅 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查必要的环境变量
    if not all([ZHIPU_API_KEY, WORDPRESS_URL, WORDPRESS_USER, WORDPRESS_PASSWORD]):
        print("❌ 错误：缺少必要的环境变量配置")
        return False
    
    # 询问用户要做什么
    print("\n请选择操作:")
    print("1. 发布新文章")
    print("2. 修复已有文章的SEO问题")
    choice = input("请输入选择 (1 或 2): ").strip()
    
    if choice == "2":
        return fix_specific_article()
    
    # 以下是发布新文章的代码（保持不变）
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
        return True
    else:
        print("💥 文章发布失败")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
