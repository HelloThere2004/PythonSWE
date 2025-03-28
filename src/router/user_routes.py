import logging
from flask import jsonify, request, abort
from werkzeug.security import generate_password_hash
from src.controllers.users_controller import login_user, update_user_profile, delete_user_account
from werkzeug.exceptions import NotFound, BadRequest
from src.middleware.auth_middleware import token_required

logger = logging.getLogger(__name__)

def init_user_routes(app):
    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            logger.warning("Missing username or password in login request")
            return jsonify(error="Bad Request", message="Missing username or password"), 400

        try:
            result = login_user(username, password)
            if result:
                return jsonify(result), 200
            else:
                raise BadRequest("Invalid username or password")
        except BadRequest as e:
            logger.warning(f"Login failed for username: {username}")
            return jsonify(error="Bad Request", message=str(e)), 400
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            return jsonify(error="Internal Server Error", message="An unexpected error occurred"), 500

    @app.route('/api/profile/update', methods=['PUT'])
    @token_required
    def update_profile():
        data = request.json
        user_id = data.get('user_id')
        new_username = data.get('new_username')
        new_password = data.get('new_password')

        if not user_id or not new_username or not new_password:
            logger.warning("Missing required data in profile update request")
            return jsonify(error="Bad Request", message="Missing user ID, username, or password"), 400

        try:
            updated_user_id = update_user_profile(user_id, new_username, new_password)
            if updated_user_id:
                return jsonify(message="Profile updated successfully", user_id=updated_user_id), 200
            else:
                raise NotFound("User not found or update failed")
        except NotFound as e:
            logger.warning(f"Profile update failed for user_id: {user_id}")
            return jsonify(error="Not Found", message=str(e)), 404
        except Exception as e:
            logger.error(f"Error updating profile for user_id {user_id}: {str(e)}")
            return jsonify(error="Internal Server Error", message="An unexpected error occurred"), 500

    @app.route('/api/profile/delete', methods=['DELETE'])
    @token_required
    def delete_account():
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            logger.warning("Missing user_id in delete request")
            return jsonify(error="Bad Request", message="Missing user ID"), 400

        try:
            deleted_user_id = delete_user_account(user_id)
            if deleted_user_id:
                return jsonify(message="Account deleted successfully", user_id=deleted_user_id), 200
            else:
                raise NotFound("User not found or deletion failed")
        except NotFound as e:
            logger.warning(f"Account deletion failed for user_id: {user_id}")
            return jsonify(error="Not Found", message=str(e)), 404
        except Exception as e:
            logger.error(f"Error deleting account for user_id {user_id}: {str(e)}")
            return jsonify(error="Internal Server Error", message="An unexpected error occurred"), 500
