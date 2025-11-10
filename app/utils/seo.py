"""
SEO 工具模块
用于生成 SEO meta 标签、结构化数据等
"""
from flask import url_for, request
from datetime import datetime
import json


def get_base_url():
    """获取网站基础 URL"""
    # 从配置中获取，如果没有则从请求中获取
    from app import app
    base_url = app.config.get('BASE_URL') or request.url_root.rstrip('/')
    return base_url


def generate_meta_tags(title, description=None, keywords=None, image=None, url=None, type='website', site_name='快點訂'):
    """
    生成 SEO meta 标签
    
    Args:
        title: 页面标题
        description: 页面描述
        keywords: 关键词（逗号分隔）
        image: 图片 URL
        url: 页面 URL
        type: Open Graph 类型（website, article, product 等）
        site_name: 网站名称
    
    Returns:
        dict: 包含所有 meta 标签的字典
    """
    base_url = get_base_url()
    
    if not url:
        url = request.url
    
    if image and not image.startswith('http'):
        image = base_url + image
    
    meta = {
        'title': title,
        'description': description or f'{site_name} - 在线订餐平台',
        'keywords': keywords or f'{site_name},订餐,外卖,在线订餐,美食',
        'url': url,
        'image': image or f'{base_url}/static/images/logo.png',
        'type': type,
        'site_name': site_name
    }
    
    return meta


def generate_structured_data_organization():
    """生成组织（Organization）结构化数据"""
    base_url = get_base_url()
    
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "快點訂",
        "url": base_url,
        "logo": f"{base_url}/static/images/logo.png",
        "description": "快點訂 - 在线订餐平台，提供便捷的外卖订餐服务",
        "sameAs": [
            # 可以添加社交媒体链接
        ]
    }


def generate_structured_data_website():
    """生成网站（WebSite）结构化数据"""
    base_url = get_base_url()
    
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "快點訂",
        "url": base_url,
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": f"{base_url}/search?q={{search_term_string}}"
            },
            "query-input": "required name=search_term_string"
        }
    }


def generate_structured_data_product(product):
    """生成产品（Product）结构化数据"""
    base_url = get_base_url()
    
    # 构建图片列表
    images = []
    if product.image_path:
        images.append(base_url + product.image_path)
    
    # 获取产品图片
    if hasattr(product, 'images') and product.images:
        for img in product.images[:5]:  # 最多5张图片
            if img.image_path:
                images.append(base_url + img.image_path)
    
    # 价格信息
    price = float(product.discounted_price if product.discounted_price else product.unit_price)
    
    data = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product.name,
        "description": product.description or product.name,
        "image": images[0] if images else None,
        "offers": {
            "@type": "Offer",
            "price": str(price),
            "priceCurrency": "TWD",
            "availability": "https://schema.org/InStock" if product.stock_quantity > 0 else "https://schema.org/OutOfStock",
            "url": f"{base_url}/store/shop/{product.shop_id}/product/{product.id}"
        }
    }
    
    if images:
        data["image"] = images if len(images) > 1 else images[0]
    
    # 添加分类信息
    if hasattr(product, 'category') and product.category:
        data["category"] = product.category.name
    
    return data


def generate_structured_data_shop(shop):
    """生成商店（Store）结构化数据"""
    base_url = get_base_url()
    
    data = {
        "@context": "https://schema.org",
        "@type": "Restaurant",
        "name": shop.name,
        "description": shop.description or shop.name,
        "url": f"{base_url}/store/shop/{shop.id}",
        "image": base_url + shop.image_path if shop.image_path else None,
        "address": {
            "@type": "PostalAddress",
            "addressCountry": "TW",
            "addressLocality": shop.district or "",
            "addressRegion": shop.county or ""
        }
    }
    
    # 添加营业时间（如果有）
    if hasattr(shop, 'opening_hours') and shop.opening_hours:
        data["openingHours"] = shop.opening_hours
    
    # 添加电话（如果有）
    if hasattr(shop, 'phone') and shop.phone:
        data["telephone"] = shop.phone
    
    return data


def generate_structured_data_article(news):
    """生成文章（Article）结构化数据"""
    base_url = get_base_url()
    
    data = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": news.name,
        "description": news.description or news.name,
        "datePublished": news.publish_date.isoformat() if news.publish_date else None,
        "dateModified": news.updated_at.isoformat() if hasattr(news, 'updated_at') and news.updated_at else None,
        "author": {
            "@type": "Organization",
            "name": "快點訂"
        },
        "publisher": {
            "@type": "Organization",
            "name": "快點訂",
            "logo": {
                "@type": "ImageObject",
                "url": f"{base_url}/static/images/logo.png"
            }
        }
    }
    
    if news.image_path:
        data["image"] = base_url + news.image_path
    
    return data


def generate_breadcrumb_list(items):
    """
    生成面包屑导航结构化数据
    
    Args:
        items: 列表，每个元素是 {'name': '名称', 'url': 'URL'}
    
    Returns:
        dict: 面包屑结构化数据
    """
    base_url = get_base_url()
    
    breadcrumb_items = []
    for i, item in enumerate(items, 1):
        breadcrumb_items.append({
            "@type": "ListItem",
            "position": i,
            "name": item['name'],
            "item": item['url'] if item['url'].startswith('http') else base_url + item['url']
        })
    
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": breadcrumb_items
    }

