"""
SEO 相关路由（sitemap.xml, robots.txt）
"""
from flask import Blueprint, Response, url_for, request
from app import db
from app.models import Shop, Product, News
from datetime import datetime
from app.config import Config

seo_bp = Blueprint('seo', __name__)


@seo_bp.route('/sitemap.xml')
def sitemap():
    """生成 sitemap.xml"""
    base_url = Config.BASE_URL.rstrip('/')
    
    urls = []
    
    # 添加静态页面
    urls.append({
        'loc': base_url + '/',
        'changefreq': 'daily',
        'priority': '1.0',
        'lastmod': datetime.now().strftime('%Y-%m-%d')
    })
    
    urls.append({
        'loc': base_url + url_for('customer.about'),
        'changefreq': 'weekly',
        'priority': '0.8',
        'lastmod': datetime.now().strftime('%Y-%m-%d')
    })
    
    urls.append({
        'loc': base_url + url_for('customer.news'),
        'changefreq': 'daily',
        'priority': '0.8',
        'lastmod': datetime.now().strftime('%Y-%m-%d')
    })
    
    # 添加店铺页面
    shops = Shop.query.filter_by(status='active', deleted_at=None).all()
    for shop in shops:
        urls.append({
            'loc': base_url + url_for('customer.shop', shop_id=shop.id),
            'changefreq': 'daily',
            'priority': '0.9',
            'lastmod': shop.updated_at.strftime('%Y-%m-%d') if shop.updated_at else datetime.now().strftime('%Y-%m-%d')
        })
        
        # 添加店铺的产品页面
        products = Product.query.filter_by(
            shop_id=shop.id,
            is_active=True,
            deleted_at=None
        ).all()
        
        for product in products:
            urls.append({
                'loc': base_url + url_for('customer.product', product_id=product.id),
                'changefreq': 'weekly',
                'priority': '0.7',
                'lastmod': product.updated_at.strftime('%Y-%m-%d') if product.updated_at else datetime.now().strftime('%Y-%m-%d')
            })
    
    # 添加新闻详情页面
    news_list = News.query.filter_by(is_active=True).all()
    for news in news_list:
        urls.append({
            'loc': base_url + url_for('customer.news_detail', news_id=news.id),
            'changefreq': 'monthly',
            'priority': '0.6',
            'lastmod': news.publish_date.strftime('%Y-%m-%d') if news.publish_date else datetime.now().strftime('%Y-%m-%d')
        })
    
    # 生成 XML
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    for url_data in urls:
        xml.append('  <url>')
        xml.append(f'    <loc>{url_data["loc"]}</loc>')
        xml.append(f'    <changefreq>{url_data["changefreq"]}</changefreq>')
        xml.append(f'    <priority>{url_data["priority"]}</priority>')
        if 'lastmod' in url_data:
            xml.append(f'    <lastmod>{url_data["lastmod"]}</lastmod>')
        xml.append('  </url>')
    
    xml.append('</urlset>')
    
    return Response('\n'.join(xml), mimetype='application/xml')


@seo_bp.route('/robots.txt')
def robots():
    """生成 robots.txt"""
    base_url = Config.BASE_URL.rstrip('/')
    
    robots_content = f"""User-agent: *
Allow: /
Disallow: /api/
Disallow: /backend/
Disallow: /shop/
Disallow: /admin/
Disallow: /guest/

Sitemap: {base_url}/sitemap.xml
"""
    
    return Response(robots_content, mimetype='text/plain')

