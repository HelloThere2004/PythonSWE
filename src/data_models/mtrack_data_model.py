import logging
from psycopg2.extras import execute_values
from src.config.postgresql import get_db_connection

logger = logging.getLogger(__name__)

# SQL Statements
INSERT_DEVICE = """
    INSERT INTO devices (device_id)
    VALUES (%s)
    ON CONFLICT (device_id) DO NOTHING
"""

INSERT_LOCATION = """
    INSERT INTO locations (latitude, longitude)
    VALUES (%s, %s)
    RETURNING location_id
"""

INSERT_ASSET_DATA = """
    INSERT INTO asset_data (device_id, voltage, status, location_id, current_speed, gps_date, gps_time)
    VALUES %s
"""

GET_LAST_ASSET_DATA = """
    SELECT ad.*, l.latitude, l.longitude
    FROM asset_data ad
    JOIN locations l ON ad.location_id = l.location_id
    WHERE ad.device_id = %s
    ORDER BY ad.inserted_at DESC
    LIMIT 1
"""

GET_DEVICE_LOCATIONS = """
    SELECT DISTINCT ON (l.latitude, l.longitude) l.latitude, l.longitude, ad.inserted_at
    FROM asset_data ad
    JOIN locations l ON ad.location_id = l.location_id
    WHERE ad.device_id = %s
    ORDER BY l.latitude, l.longitude, ad.inserted_at DESC
"""

GET_ALL_DEVICES = """
    SELECT * FROM devices
"""

def with_connection(func):
    def wrapper(*args, **kwargs):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                return func(cur, *args, **kwargs)
    return wrapper

@with_connection
def insert_device(cursor, device_id):
    try:
        cursor.execute(INSERT_DEVICE, (device_id,))
        logger.info(f"Device {device_id} inserted or already exists")
    except Exception as e:
        logger.error(f"Error inserting device {device_id}: {e}")
        raise

@with_connection
def insert_location(cursor, latitude, longitude):
    try:
        cursor.execute(INSERT_LOCATION, (latitude, longitude))
        location_id = cursor.fetchone()[0]
        logger.info(f"Location inserted with id {location_id}")
        return location_id
    except Exception as e:
        logger.error(f"Error inserting location: {e}")
        raise

@with_connection
def insert_asset_data(cursor, data, location_id):
    try:
        values = [(
            data['deviceId'],
            data['voltage'],
            data['status'],
            location_id,
            data['currentSpeed'],
            data['gpsDate'],
            data['gpsTime']
        )]
        execute_values(cursor, INSERT_ASSET_DATA, values)
        logger.info(f"Asset data inserted for device {data['deviceId']}")
    except Exception as e:
        logger.error(f"Error inserting asset data: {e}")
        raise

@with_connection
def upload_data(cursor, parsed_data):
    try:
        # Insert or update device
        insert_device(cursor, parsed_data['deviceId'])

        # Insert location
        location_id = insert_location(cursor, parsed_data['latitude'], parsed_data['longitude'])

        # Insert asset data
        insert_asset_data(cursor, parsed_data, location_id)

        logger.info(f"Data uploaded successfully for device: {parsed_data['deviceId']}")
    except Exception as e:
        logger.error(f"Error uploading data: {e}")
        raise

@with_connection
def get_last_asset_data(cursor, device_id):
    try:
        cursor.execute(GET_LAST_ASSET_DATA, (device_id,))
        result = cursor.fetchone()
        if result:
            return dict(zip([column[0] for column in cursor.description], result))
        return None
    except Exception as e:
        logger.error(f"Error retrieving last asset data for device {device_id}: {e}")
        raise

@with_connection
def get_device_locations(cursor, device_id):
    try:
        cursor.execute(GET_DEVICE_LOCATIONS, (device_id,))
        return [{"latitude": row[0], "longitude": row[1], "timestamp": row[2]} for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Error retrieving locations for device {device_id}: {e}")
        raise

@with_connection
def get_all_devices(cursor):
    try:
        cursor.execute(GET_ALL_DEVICES)
        return [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Error retrieving all devices: {e}")
        raise
