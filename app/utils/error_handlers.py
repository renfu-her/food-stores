"""
統一錯誤處理模組
"""
from flask import jsonify, render_template, request
from app import db

def register_error_handlers(app):
    """註冊錯誤處理器"""
    
    @app.errorhandler(KeyError)
    def handle_key_error(error):
        """處理 KeyError，特別是 Socket.IO 的會話斷開錯誤"""
        if 'Session is disconnected' in str(error):
            # Socket.IO 會話斷開，靜默處理
            return '', 200
        # 其他 KeyError 當作 400 處理
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'key_error',
                'message': '缺少必要參數',
                'details': {'key': str(error)}
            }), 400
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(400)
    def bad_request(error):
        """400 Bad Request"""
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'bad_request',
                'message': '請求參數錯誤',
                'details': {}
            }), 400
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """401 Unauthorized"""
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'unauthorized',
                'message': '未認證，请先登录',
                'details': {}
            }), 401
        return render_template('errors/401.html'), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """403 Forbidden"""
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'forbidden',
                'message': '權限不足',
                'details': {}
            }), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """404 Not Found"""
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'not_found',
                'message': '資源不存在',
                'details': {}
            }), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500 Internal Server Error"""
        db.session.rollback()
        # 忽略 Socket.IO 的會話斷開錯誤
        if 'Session is disconnected' in str(error):
            return '', 200
        if request.path.startswith('/api/') or request.path.startswith('/socket.io/'):
            return jsonify({
                'error': 'internal_error',
                'message': '伺服器內部錯誤',
                'details': {}
            }), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(ValueError)
    def value_error(error):
        """值錯誤處理"""
        return jsonify({
            'error': 'validation_error',
            'message': str(error),
            'details': {}
        }), 400

