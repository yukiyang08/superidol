"""
Security utility functions.
"""

import bcrypt
import jwt
from functools import wraps
from flask import request, jsonify
from app.config import Config
from typing import Union
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token


def is_bcrypt_hash(value: str) -> bool:
    """Return True when the stored hash looks like a bcrypt hash."""
    if not isinstance(value, str):
        return False
    return value.startswith("$2a$") or value.startswith("$2b$") or value.startswith("$2y$")

def get_password_hash(password: str) -> str:
    """生成密碼哈希"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """驗證密碼。

    Notes:
    - Returns False (instead of raising) for invalid/legacy hash formats.
    - This keeps login flow stable when old records are not bcrypt encoded.
    """
    if not isinstance(hashed_password, str) or not hashed_password:
        return False

    if not is_bcrypt_hash(hashed_password):
        return False

    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except ValueError:
        return False

def create_token(identity: Union[int, str], expires_delta: timedelta = None) -> str:
    """創建 JWT token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=1)
    
    return create_access_token(
        identity=identity,
        expires_delta=expires_delta
    )

def hash_password(password):
    """
    Hash a password using bcrypt.
    
    Args:
        password (str): Plain text password
        
    Returns:
        str: Hashed password
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def token_required(f):
    """
    Decorator to make a route require a valid JWT token.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is provided in the header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
            
        try:
            # Decode the token
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            
            # Add user_id to kwargs
            kwargs['user_id'] = user_id
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
            
        return f(*args, **kwargs)
        
    return decorated 