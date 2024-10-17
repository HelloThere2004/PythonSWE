import logging
from psycopg2.extras import execute_values

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

def insert_device(cursor, device_id):
    try:
        cursor.execute(INSERT_DEVICE, (device_id,))
        logger.info(f"Device {device_id} inserted or already exists")
    except Exception as e:
        logger.error(f"Error inserting device {device_id}: {e}")
        raise

def insert_location(cursor, latitude, longitude):
    try:
        cursor.execute(INSERT_LOCATION, (latitude, longitude))
        location_id = cursor.fetchone()[0]
        logger.info(f"Location inserted with id {location_id}")
        return location_id
    except Exception as e:
        logger.error(f"Error inserting location: {e}")
        raise

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

def upload_data(conn, parsed_data):
    try:
        with conn.cursor() as cur:
            # Insert or update device
            insert_device(cur, parsed_data['deviceId'])

            # Insert location
            location_id = insert_location(cur, parsed_data['latitude'], parsed_data['longitude'])

            # Insert asset data
            insert_asset_data(cur, parsed_data, location_id)

        conn.commit()
        logger.info(f"Data uploaded successfully for device: {parsed_data['deviceId']}")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error uploading data: {e}")
        raise
