import logging
from datetime import datetime
from src.data_models.notification_data_model import (
    create_notification,
    get_notification,
    update_notification,
    delete_notification,
    get_device_notifications,
    get_pending_notifications
)

logger = logging.getLogger(__name__)

def create_device_notification(device_id, notification_type, message, asset_data_id=None):
    """
    Create a new notification for a device.

    Args:
        device_id: The ID of the device
        notification_type: Type of notification (must be valid notification_type enum)
        message: Notification message
        asset_data_id: Optional reference to asset_data entry

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

def get_notification_by_id(notification_id):
    """
    Retrieve a specific notification.

    Args:
        notification_id: ID of the notification to retrieve

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

def acknowledge_notification(notification_id, user_id):
    """
    Acknowledge a notification.

    Args:
        notification_id: ID of the notification to acknowledge
        user_id: ID of the user acknowledging the notification

    Returns:
        Dictionary containing updated notification details
    """
    try:
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

def update_notification_status(notification_id, status, message=None):
    """
    Update a notification's status and optionally its message.

    Args:
        notification_id: ID of the notification to update
        status: New status (must be valid notification_status enum)
        message: Optional new message

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

def remove_notification(notification_id):
    """
    Delete a notification.

    Args:
        notification_id: ID of the notification to delete

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

def get_notifications_for_device(device_id):
    """
    Get all notifications for a specific device.

    Args:
        device_id: ID of the device

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

def get_all_pending_notifications():
    """
    Get all pending notifications across all devices.

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
