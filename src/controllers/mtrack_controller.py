import logging
from src.data_models.mtrack_data_model import get_last_asset_data, get_device_locations, get_all_devices
from src.config.postgresql import get_db_connection
from datetime import date, time, datetime

logger = logging.getLogger(__name__)

def serialize_data(data):
    if isinstance(data, dict):
        return {k: serialize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_data(item) for item in data]
    elif isinstance(data, (date, time, datetime)):
        return data.isoformat()
    return data

def get_device_last_data(device_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                result = get_last_asset_data(cur, device_id)
        return serialize_data(result)
    except Exception as e:
        logger.error(f"Error in get_device_last_data: {e}")
        raise

def get_device_location_history(device_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                result = get_device_locations(cur, device_id)
        return serialize_data(result)
    except Exception as e:
        logger.error(f"Error in get_device_location_history: {e}")
        raise

def get_devices():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                result = get_all_devices(cur)
        return serialize_data(result)
    except Exception as e:
        logger.error(f"Error in get_devices: {e}")
        raise
