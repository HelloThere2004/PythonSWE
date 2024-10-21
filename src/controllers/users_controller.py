import logging
import jwt
from werkzeug.security import check_password_hash, generate_password_hash
from src.data_models.user_data_model import get_user_by_username, update_user, delete_user, get_user_by_id
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Secret key for JWT (use a strong, secure secret key)
SECRET_KEY = 'innov@ti0n'

def generate_token(user_id, username):
    """
    Generates a JWT token for the authenticated user, including user ID and username.
    """
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def login_user(username, password):
    try:
        user = get_user_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            logger.info(f"User {username} successfully logged in.")
            token = generate_token(user['id'], user['username'])  # Include both user_id and username in the token
            return {'token': token}  # Return only the token
        else:
            logger.warning(f"Login failed for {username}. Incorrect credentials.")
            return None
    except Exception as e:
        logger.error(f"Error during login for {username}: {e}")
        raise

def update_user_profile(user_id, new_username, new_password):
    try:
        password_hash = generate_password_hash(new_password)
        updated_user_id = update_user(user_id, new_username, password_hash)
        if updated_user_id:
            logger.info(f"User {user_id} successfully updated their profile.")
            return updated_user_id
        else:
            logger.warning(f"Failed to update profile for user {user_id}.")
            return None
    except Exception as e:
        logger.error(f"Error updating profile for user {user_id}: {e}")
        raise

def delete_user_account(user_id):
    try:
        deleted_user_id = delete_user(user_id)
        if deleted_user_id:
            logger.info(f"User {user_id} successfully deleted their account.")
            return deleted_user_id
        else:
            logger.warning(f"Failed to delete account for user {user_id}.")
            return None
    except Exception as e:
        logger.error(f"Error deleting account for user {user_id}: {e}")
        raise

def find_user_by_id(user_id):
    """
    Finds a user by their ID.
    """
    try:
        user = get_user_by_id(user_id)
        if user:
            logger.info(f"User with ID {user_id} found.")
            return user
        else:
            logger.warning(f"User with ID {user_id} not found.")
            return None
    except Exception as e:
        logger.error(f"Error retrieving user with ID {user_id}: {e}")
        raise
