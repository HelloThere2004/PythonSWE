import logging
from src.data_models.mtrack_data_model import upload_data

logger = logging.getLogger(__name__)

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

def process_message(message):
    parsed_data = parse_device_message(message)
    if parsed_data:
        try:
            upload_data(parsed_data)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    else:
        logger.warning("Failed to parse message, invalid format.")
