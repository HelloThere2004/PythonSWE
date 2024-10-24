import logging
from datetime import datetime
from functools import wraps
import jwt
from src.data_models.notification_data_model import (
    create_notification,
    get_notification,
    update_notification,
    delete_notification,
    get_device_notifications,
    get_pending_notifications
)
from src.config.env_loader import SECRET_KEY

logger = logging.getLogger(__name__)

def require_auth(f):
    """Decorator to check if request has valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = kwargs.get('token')
        if not token:
            logger.error("No token provided")
            raise ValueError("Authentication token is required")

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            kwargs['user_id'] = payload['user_id']
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            logger.error("Expired token")
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            logger.error("Invalid token")
            raise ValueError("Invalid token")

    return decorated

class NotificationController:
    @staticmethod
    @require_auth
    def create_device_notification(device_id, notification_type, message, asset_data_id=None, **kwargs):
        """
        Create a new notification for a device.

        Args:
            device_id: The ID of the device
            notification_type: Type of notification (must be valid notification_type enum)
            message: Notification message
            asset_data_id: Optional reference to asset_data entry
            **kwargs: Contains token and user_id from @require_auth

        Returns:
            Dictionary containing the created notification details
        """
        try:
            notification = create_notification(
                device_id=device_id,
                notification_type=notification_type,
                message=message,
                asset_data_id=asset_data_id
            )
            logger.info(f"Controller: Created notification for device {device_id}")
            return notification
        except Exception as e:
            logger.error(f"Controller: Error creating notification: {e}")
            raise

    @staticmethod
    @require_auth
    def get_notification_by_id(notification_id, **kwargs):
        """
        Retrieve a specific notification.

        Args:
            notification_id: ID of the notification to retrieve
            **kwargs: Contains token and user_id from @require_auth

        Returns:
            Dictionary containing notification details
        """
        try:
            notification = get_notification(notification_id)
            if not notification:
                logger.warning(f"Controller: Notification {notification_id} not found")
                return None
            logger.info(f"Controller: Retrieved notification {notification_id}")
            return notification
        except Exception as e:
            logger.error(f"Controller: Error retrieving notification: {e}")
            raise

    @staticmethod
    @require_auth
    def acknowledge_notification(notification_id, **kwargs):
        """
        Acknowledge a notification.

        Args:
            notification_id: ID of the notification to acknowledge
            **kwargs: Contains token and user_id from @require_auth

        Returns:
            Dictionary containing updated notification details
        """
        try:
            user_id = kwargs.get('user_id')
            notification = update_notification(
                notification_id=notification_id,
                status='acknowledged',
                acknowledged_by=user_id
            )
            if not notification:
                logger.warning(f"Controller: Failed to acknowledge notification {notification_id}")
                return None
            logger.info(f"Controller: Notification {notification_id} acknowledged by user {user_id}")
            return notification
        except Exception as e:
            logger.error(f"Controller: Error acknowledging notification: {e}")
            raise

    @staticmethod
    @require_auth
    def update_notification_status(notification_id, status, message=None, **kwargs):
        """
        Update a notification's status and optionally its message.

        Args:
            notification_id: ID of the notification to update
            status: New status (must be valid notification_status enum)
            message: Optional new message
            **kwargs: Contains token and user_id from @require_auth

        Returns:
            Dictionary containing updated notification details
        """
        try:
            notification = update_notification(
                notification_id=notification_id,
                status=status,
                message=message
            )
            if not notification:
                logger.warning(f"Controller: Failed to update notification {notification_id}")
                return None
            logger.info(f"Controller: Updated notification {notification_id} status to {status}")
            return notification
        except Exception as e:
            logger.error(f"Controller: Error updating notification: {e}")
            raise

    @staticmethod
    @require_auth
    def remove_notification(notification_id, **kwargs):
        """
        Delete a notification.

        Args:
            notification_id: ID of the notification to delete
            **kwargs: Contains token and user_id from @require_auth

        Returns:
            Boolean indicating success
        """
        try:
            result = delete_notification(notification_id)
            if result:
                logger.info(f"Controller: Deleted notification {notification_id}")
            else:
                logger.warning(f"Controller: Failed to delete notification {notification_id}")
            return result
        except Exception as e:
            logger.error(f"Controller: Error deleting notification: {e}")
            raise

    @staticmethod
    @require_auth
    def get_notifications_for_device(device_id, **kwargs):
        """
        Get all notifications for a specific device.

        Args:
            device_id: ID of the device
            **kwargs: Contains token and user_id from @require_auth

        Returns:
            List of dictionaries containing notification details
        """
        try:
            notifications = get_device_notifications(device_id)
            logger.info(f"Controller: Retrieved {len(notifications)} notifications for device {device_id}")
            return notifications
        except Exception as e:
            logger.error(f"Controller: Error retrieving device notifications: {e}")
            raise

    @staticmethod
    @require_auth
    def get_all_pending_notifications(**kwargs):
        """
        Get all pending notifications across all devices.

        Args:
            **kwargs: Contains token and user_id from @require_auth

        Returns:
            List of dictionaries containing notification details
        """
        try:
            notifications = get_pending_notifications()
            logger.info(f"Controller: Retrieved {len(notifications)} pending notifications")
            return notifications
        except Exception as e:
            logger.error(f"Controller: Error retrieving pending notifications: {e}")
            raise
