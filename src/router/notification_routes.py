import logging
from flask import jsonify, request
from werkzeug.exceptions import NotFound, BadRequest
from src.middleware.auth_middleware import token_required
from src.controllers.notification_controller import NotificationController

logger = logging.getLogger(__name__)

def init_notification_routes(app):
    @app.route('/api/notifications', methods=['POST'])
    @token_required
    def create_notification():
        """Create a new notification"""
        data = request.json
        required_fields = ['device_id', 'type', 'message']

        # Validate required fields
        if not all(field in data for field in required_fields):
            logger.warning("Missing required fields in notification creation request")
            return jsonify(error="Bad Request",
                         message="Missing required fields: device_id, type, message"), 400

        try:
            notification = NotificationController.create_device_notification(
                device_id=data['device_id'],
                notification_type=data['type'],
                message=data['message'],
                asset_data_id=data.get('asset_data_id'),
                token=request.token  # Token from @token_required decorator
            )
            return jsonify(notification), 201
        except ValueError as e:
            logger.warning(f"Invalid notification data: {str(e)}")
            return jsonify(error="Bad Request", message=str(e)), 400
        except Exception as e:
            logger.error(f"Error creating notification: {str(e)}")
            return jsonify(error="Internal Server Error",
                         message="An unexpected error occurred"), 500

    @app.route('/api/notifications/<int:notification_id>', methods=['GET'])
    @token_required
    def get_notification(notification_id):
        """Get a specific notification by ID"""
        try:
            notification = NotificationController.get_notification_by_id(
                notification_id=notification_id,
                token=request.token
            )
            if not notification:
                raise NotFound("Notification not found")
            return jsonify(notification), 200
        except NotFound as e:
            logger.warning(f"Notification not found: {notification_id}")
            return jsonify(error="Not Found", message=str(e)), 404
        except Exception as e:
            logger.error(f"Error retrieving notification {notification_id}: {str(e)}")
            return jsonify(error="Internal Server Error",
                         message="An unexpected error occurred"), 500

    @app.route('/api/notifications/<int:notification_id>/acknowledge', methods=['PUT'])
    @token_required
    def acknowledge_notification(notification_id):
        """Acknowledge a notification"""
        try:
            notification = NotificationController.acknowledge_notification(
                notification_id=notification_id,
                token=request.token
            )
            if not notification:
                raise NotFound("Notification not found")
            return jsonify(notification), 200
        except NotFound as e:
            logger.warning(f"Failed to acknowledge notification: {notification_id}")
            return jsonify(error="Not Found", message=str(e)), 404
        except Exception as e:
            logger.error(f"Error acknowledging notification {notification_id}: {str(e)}")
            return jsonify(error="Internal Server Error",
                         message="An unexpected error occurred"), 500

    @app.route('/api/notifications/<int:notification_id>', methods=['PUT'])
    @token_required
    def update_notification(notification_id):
        """Update a notification's status and message"""
        data = request.json
        if 'status' not in data:
            logger.warning("Missing status in notification update request")
            return jsonify(error="Bad Request", message="Status is required"), 400

        try:
            notification = NotificationController.update_notification_status(
                notification_id=notification_id,
                status=data['status'],
                message=data.get('message'),
                token=request.token
            )
            if not notification:
                raise NotFound("Notification not found")
            return jsonify(notification), 200
        except ValueError as e:
            logger.warning(f"Invalid notification update data: {str(e)}")
            return jsonify(error="Bad Request", message=str(e)), 400
        except NotFound as e:
            logger.warning(f"Notification not found: {notification_id}")
            return jsonify(error="Not Found", message=str(e)), 404
        except Exception as e:
            logger.error(f"Error updating notification {notification_id}: {str(e)}")
            return jsonify(error="Internal Server Error",
                         message="An unexpected error occurred"), 500

    @app.route('/api/notifications/<int:notification_id>', methods=['DELETE'])
    @token_required
    def delete_notification(notification_id):
        """Delete a notification"""
        try:
            result = NotificationController.remove_notification(
                notification_id=notification_id,
                token=request.token
            )
            if not result:
                raise NotFound("Notification not found")
            return jsonify(message="Notification deleted successfully"), 200
        except NotFound as e:
            logger.warning(f"Notification not found for deletion: {notification_id}")
            return jsonify(error="Not Found", message=str(e)), 404
        except Exception as e:
            logger.error(f"Error deleting notification {notification_id}: {str(e)}")
            return jsonify(error="Internal Server Error",
                         message="An unexpected error occurred"), 500

    @app.route('/api/devices/<device_id>/notifications', methods=['GET'])
    @token_required
    def get_device_notifications(device_id):
        """Get all notifications for a specific device"""
        try:
            notifications = NotificationController.get_notifications_for_device(
                device_id=device_id,
                token=request.token
            )
            return jsonify(notifications), 200
        except Exception as e:
            logger.error(f"Error retrieving notifications for device {device_id}: {str(e)}")
            return jsonify(error="Internal Server Error",
                         message="An unexpected error occurred"), 500

    @app.route('/api/notifications/pending', methods=['GET'])
    @token_required
    def get_pending_notifications():
        """Get all pending notifications"""
        try:
            notifications = NotificationController.get_all_pending_notifications(
                token=request.token
            )
            return jsonify(notifications), 200
        except Exception as e:
            logger.error(f"Error retrieving pending notifications: {str(e)}")
            return jsonify(error="Internal Server Error",
                         message="An unexpected error occurred"), 500

    # Optional: Add batch operations endpoint
    @app.route('/api/notifications/batch/acknowledge', methods=['PUT'])
    @token_required
    def batch_acknowledge_notifications():
        """Acknowledge multiple notifications at once"""
        data = request.json
        if not data or 'notification_ids' not in data:
            logger.warning("Missing notification_ids in batch acknowledge request")
            return jsonify(error="Bad Request",
                         message="notification_ids array is required"), 400

        try:
            results = []
            for notification_id in data['notification_ids']:
                notification = NotificationController.acknowledge_notification(
                    notification_id=notification_id,
                    token=request.token
                )
                if notification:
                    results.append(notification)

            return jsonify({
                'message': f"Successfully acknowledged {len(results)} notifications",
                'notifications': results
            }), 200
        except Exception as e:
            logger.error(f"Error in batch notification acknowledgment: {str(e)}")
            return jsonify(error="Internal Server Error",
                         message="An unexpected error occurred"), 500
