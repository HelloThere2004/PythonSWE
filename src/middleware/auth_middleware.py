# auth_middleware.py
from functools import wraps
from flask import request, jsonify
import jwt
from datetime import datetime, timedelta
from src.controllers.users_controller import find_user_by_id
import logging
from src.config.env_loader import SECRET_KEY

logger = logging.getLogger(__name__)



def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            logger.warning("Token is missing in the request")
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token.split(' ')[1]

            # Decode the token
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = data['user_id']

            # Verify user exists
            user = find_user_by_id(user_id)
            if not user:
                logger.warning(f"User with ID {user_id} not found in the database")
                return jsonify({'message': 'User not found!'}), 401

            # Add user to the request context
            request.user = user
            request.user_id = user_id
        except jwt.ExpiredSignatureError:
            logger.warning("Expired token received")
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            logger.warning("Invalid token received")
            return jsonify({'message': 'Invalid token!'}), 401
        except Exception as e:
            logger.error(f"Error in token verification: {str(e)}")
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(*args, **kwargs)
    return decorated

def apply_middleware(app):
    @app.before_request
    def require_token():
        if request.endpoint != 'login':
            return token_required(lambda: None)()
