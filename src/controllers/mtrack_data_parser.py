import logging
from src.data_models.mtrack_data_model import upload_data
from src.data_models.notification_data_model import (
    create_notification,
    get_device_notifications
)

logger = logging.getLogger(__name__)

# Battery threshold constants
BATTERY_CRITICAL = 33.0
BATTERY_LOW = 35.0
BATTERY_MEDIUM = 37.0

def check_battery_status(voltage):
    """
    Determine battery status based on voltage thresholds.
    Returns tuple of (status_type, message) or (None, None) if no notification needed.
    """
    if voltage <= BATTERY_CRITICAL:
        return ('low_battery', f'CRITICAL: Device battery at critical level ({voltage / 10}V)')
    elif voltage < BATTERY_LOW:
        return ('low_battery', f'WARNING: Device battery is low ({voltage / 10}V)')
    elif voltage < BATTERY_MEDIUM:
        return ('low_battery', f'NOTICE: Device battery is at medium level ({voltage / 10}V)')
    return None, None

def should_create_battery_notification(device_id, voltage):
    """
    Check if a new battery notification should be created based on existing notifications.
    """
    try:
        # Get recent notifications for the device
        device_notifications = get_device_notifications(device_id)

        # Filter for active battery notifications
        battery_notifications = [
            n for n in device_notifications
            if n['type'] == 'low_battery'
            and n['status'] in ('pending', 'sent')
        ]

        if not battery_notifications:
            return True

        # Get the most recent battery notification
        latest_notification = max(
            battery_notifications,
            key=lambda x: x['created_at']
        )

        # Extract voltage from the latest notification message
        # Assuming message format includes voltage in parentheses like "... (35.5V)"
        current_notif_voltage = float(
            latest_notification['message']
            .split('(')[1]
            .split('V')[0]
        )

        # Determine voltage threshold categories
        def get_threshold_category(v):
            if v <= BATTERY_CRITICAL:
                return "critical"
            elif v < BATTERY_LOW:
                return "low"
            elif v < BATTERY_MEDIUM:
                return "medium"
            return "normal"

        # Only create new notification if voltage category has changed
        current_category = get_threshold_category(current_notif_voltage)
        new_category = get_threshold_category(voltage)

        return current_category != new_category

    except Exception as e:
        logger.error(f"Error checking battery notifications: {e}")
        return True  # Create notification if there's an error checking

def parse_device_message(msg):
    try:
        parts = msg.split("#")
        device_id = parts[1]
        voltage = parts[6].split("$")[0]
        gprmc_raw = parts[6].split("$")[1].split(",")

        time_utc = gprmc_raw[1] or "0"
        status = gprmc_raw[2]
        status_message = {
            "A": "valid_position",
            "L": "last_known_position",
            "V": "invalid_position"
        }.get(status, "invalid_position")

        latitude_raw = gprmc_raw[3] or "0"
        latitude_direction = gprmc_raw[4] or "N"
        longitude_raw = gprmc_raw[5] or "0"
        longitude_direction = gprmc_raw[6] or "E"
        speed_knots = gprmc_raw[7] or "0"
        date = gprmc_raw[9] or "0"

        def convert_to_decimal(degree_minutes, direction):
            degrees = float(degree_minutes[:-7]) if degree_minutes else 0
            minutes = float(degree_minutes[-7:]) / 60 if degree_minutes else 0
            decimal = degrees + minutes
            return -decimal if direction in ['S', 'W'] else decimal

        latitude = convert_to_decimal(latitude_raw, latitude_direction)
        longitude = convert_to_decimal(longitude_raw, longitude_direction)

        return {
            "deviceId": device_id,
            "voltage": float(voltage),
            "status": status_message,
            "latitude": latitude,
            "longitude": longitude,
            "currentSpeed": float(speed_knots),
            "gpsDate": f"20{date[4:6]}-{date[2:4]}-{date[:2]}",
            "gpsTime": f"{time_utc[:2]}:{time_utc[2:4]}:{time_utc[4:6]}"
        }

    except Exception as e:
        logger.error(f"Error parsing message: {e}")
        return None

def handle_battery_notification(device_id, voltage, asset_data_id):
    """
    Handle battery notification creation based on voltage levels.
    """
    try:
        notification_type, message = check_battery_status(voltage)

        if notification_type and should_create_battery_notification(device_id, voltage):
            notification = create_notification(
                device_id=device_id,
                notification_type=notification_type,
                message=message,
                asset_data_id=asset_data_id
            )
            logger.info(f"Created battery notification for device {device_id}: {message}")
            return notification
        return None
    except Exception as e:
        logger.error(f"Error handling battery notification: {e}")
        return None

def process_message(message):
    parsed_data = parse_device_message(message)
    if parsed_data:
        try:
            # Upload data and get the asset_data_id
            asset_data_id = upload_data(parsed_data)

            # Handle battery notifications
            voltage = parsed_data['voltage']
            device_id = parsed_data['deviceId']

            handle_battery_notification(device_id, voltage, asset_data_id)

        except Exception as e:
            logger.error(f"Error processing message: {e}")
    else:
        logger.warning("Failed to parse message, invalid format.")
