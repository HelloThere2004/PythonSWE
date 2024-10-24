import logging
from src.data_models.mtrack_data_model import (
    get_last_asset_data,
    get_device_locations,
    get_all_devices,
    get_asset_data_by_date_range
)
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
        result = get_last_asset_data(device_id)
        return serialize_data(result)
    except Exception as e:
        logger.error(f"Error in get_device_last_data: {e}")
        raise

def get_device_location_history(device_id):
    try:
        result = get_device_locations(device_id)
        return serialize_data(result)
    except Exception as e:
        logger.error(f"Error in get_device_location_history: {e}")
        raise

def get_devices():
    try:
        result = get_all_devices()
        return serialize_data(result)
    except Exception as e:
        logger.error(f"Error in get_devices: {e}")
        raise

def get_device_data_by_date_range(device_id, start_date, end_date):
    """
    Get asset data with location for a specific device within a date range.

    Args:
        device_id (str): The ID of the device to query
        start_date (str or datetime): The start date of the range
        end_date (str or datetime): The end date of the range

    Returns:
        list: Serialized list of asset data with location information
    """
    try:
        # Convert string dates to datetime if needed
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)

        result = get_asset_data_by_date_range(device_id, start_date, end_date)
        return serialize_data(result)
    except Exception as e:
        logger.error(f"Error in get_device_data_by_date_range: {e}")
        raise
