import logging
from psycopg2.extras import execute_values
from src.config.postgresql import get_db_connection
from datetime import datetime

logger = logging.getLogger(__name__)

# SQL Statements
INSERT_NOTIFICATION = """
    INSERT INTO notifications (device_id, type, status, message, asset_data_id)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING notification_id
"""

GET_NOTIFICATION = """
    SELECT notification_id, device_id, type, status, message,
           created_at, updated_at, asset_data_id,
           acknowledged_at, acknowledged_by
    FROM notifications
    WHERE notification_id = %s
"""

UPDATE_NOTIFICATION = """
    UPDATE notifications
    SET status = %s,
        message = %s,
        acknowledged_at = %s,
        acknowledged_by = %s
    WHERE notification_id = %s
    RETURNING notification_id
"""

DELETE_NOTIFICATION = """
    DELETE FROM notifications
    WHERE notification_id = %s
    RETURNING notification_id
"""

GET_DEVICE_NOTIFICATIONS = """
    SELECT notification_id, device_id, type, status, message,
           created_at, updated_at, asset_data_id,
           acknowledged_at, acknowledged_by
    FROM notifications
    WHERE device_id = %s
    ORDER BY created_at DESC
"""

GET_PENDING_NOTIFICATIONS = """
    SELECT notification_id, device_id, type, status, message,
           created_at, updated_at, asset_data_id,
           acknowledged_at, acknowledged_by
    FROM notifications
    WHERE status = 'pending'
    ORDER BY created_at ASC
"""

def with_connection(func):
    def wrapper(*args, **kwargs):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                return func(cur, *args, **kwargs)
    return wrapper

@with_connection
def create_notification(cursor, device_id, notification_type, message, asset_data_id=None):
    """
    Create a new notification for a device.

    Args:
        device_id: The ID of the device
        notification_type: Type of notification (from notification_type enum)
        message: Notification message
        asset_data_id: Optional reference to asset_data entry

    Returns:
        Dictionary containing the created notification details
    """
    try:
        cursor.execute(INSERT_NOTIFICATION,
                      (device_id, notification_type, 'pending', message, asset_data_id))
        notification_id = cursor.fetchone()[0]
        logger.info(f"Created notification {notification_id} for device {device_id}")

        # Fetch and return the created notification
        cursor.execute(GET_NOTIFICATION, (notification_id,))
        result = cursor.fetchone()
        return dict(zip([column[0] for column in cursor.description], result))
    except Exception as e:
        logger.error(f"Error creating notification for device {device_id}: {e}")
        raise

@with_connection
def get_notification(cursor, notification_id):
    """
    Retrieve a specific notification by ID.
    """
    try:
        cursor.execute(GET_NOTIFICATION, (notification_id,))
        result = cursor.fetchone()
        if result:
            return dict(zip([column[0] for column in cursor.description], result))
        return None
    except Exception as e:
        logger.error(f"Error retrieving notification {notification_id}: {e}")
        raise

@with_connection
def update_notification(cursor, notification_id, status=None, message=None,
                       acknowledged_by=None):
    """
    Update a notification's status, message, and acknowledgment details.
    """
    try:
        # Get current notification data
        current = get_notification(notification_id)
        if not current:
            raise ValueError(f"Notification {notification_id} not found")

        # Update with new values or keep current ones
        new_status = status or current['status']
        new_message = message or current['message']
        acknowledged_at = datetime.now() if acknowledged_by else current['acknowledged_at']

        cursor.execute(UPDATE_NOTIFICATION,
                      (new_status, new_message, acknowledged_at,
                       acknowledged_by, notification_id))

        updated_id = cursor.fetchone()[0]
        logger.info(f"Updated notification {updated_id}")

        # Fetch and return the updated notification
        return get_notification(updated_id)
    except Exception as e:
        logger.error(f"Error updating notification {notification_id}: {e}")
        raise

@with_connection
def delete_notification(cursor, notification_id):
    """
    Delete a notification by ID.
    """
    try:
        cursor.execute(DELETE_NOTIFICATION, (notification_id,))
        deleted_id = cursor.fetchone()
        if deleted_id:
            logger.info(f"Deleted notification {notification_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting notification {notification_id}: {e}")
        raise

@with_connection
def get_device_notifications(cursor, device_id):
    """
    Retrieve all notifications for a specific device.
    """
    try:
        cursor.execute(GET_DEVICE_NOTIFICATIONS, (device_id,))
        results = cursor.fetchall()
        return [dict(zip([column[0] for column in cursor.description], row))
                for row in results]
    except Exception as e:
        logger.error(f"Error retrieving notifications for device {device_id}: {e}")
        raise

@with_connection
def get_pending_notifications(cursor):
    """
    Retrieve all pending notifications across all devices.
    """
    try:
        cursor.execute(GET_PENDING_NOTIFICATIONS)
        results = cursor.fetchall()
        return [dict(zip([column[0] for column in cursor.description], row))
                for row in results]
    except Exception as e:
        logger.error(f"Error retrieving pending notifications: {e}")
        raise
