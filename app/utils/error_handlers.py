"""
統一錯誤處理模組
"""
from flask import jsonify, render_template
from app import db

def register_error_handlers(app):
    """註冊錯誤處理器"""
    
    @app.errorhandler(400)
    def bad_request(error):
        """400 Bad Request"""
        return jsonify({
            'error': 'bad_request',
            'message': '請求參數錯誤',
            'details': {}
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """401 Unauthorized"""
        return jsonify({
            'error': 'unauthorized',
            'message': '未認證，请先登录',
            'details': {}
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """403 Forbidden"""
        return jsonify({
            'error': 'forbidden',
            'message': '權限不足',
            'details': {}
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """404 Not Found"""
        return jsonify({
            'error': 'not_found',
            'message': '資源不存在',
            'details': {}
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500 Internal Server Error"""
        db.session.rollback()
        return jsonify({
            'error': 'internal_error',
            'message': '伺服器內部錯誤',
            'details': {}
        }), 500
    
    @app.errorhandler(ValueError)
    def value_error(error):
        """值錯誤處理"""
        return jsonify({
            'error': 'validation_error',
            'message': str(error),
            'details': {}
        }), 400

