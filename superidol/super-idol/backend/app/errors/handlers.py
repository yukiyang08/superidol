from flask import jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    """註冊錯誤處理器"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': str(error)
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': str(error)
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Forbidden',
            'message': str(error)
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': str(error)
        }), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(error)
        }), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        """處理所有未捕獲的異常"""
        if isinstance(error, HTTPException):
            return jsonify({
                'error': error.name,
                'message': str(error)
            }), error.code
            
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(error)
        }), 500 