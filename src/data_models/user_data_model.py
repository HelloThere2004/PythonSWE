import logging
from psycopg2.extras import execute_values
from src.config.postgresql import get_db_connection

logger = logging.getLogger(__name__)

# SQL Statements
INSERT_USER = """
    INSERT INTO users (username, password_hash)
    VALUES (%s, %s)
    RETURNING id
"""

UPDATE_USER = """
    UPDATE users
    SET username = %s, password_hash = %s
    WHERE id = %s
    RETURNING id
"""

DELETE_USER = """
    DELETE FROM users
    WHERE id = %s
    RETURNING id
"""

GET_USER_BY_USERNAME = """
    SELECT * FROM users
    WHERE username = %s
"""

GET_USER_BY_ID = """
    SELECT * FROM users
    WHERE id = %s
"""

GET_ALL_USERS = """
    SELECT * FROM users
"""

def with_connection(func):
    def wrapper(*args, **kwargs):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                return func(cur, *args, **kwargs)
    return wrapper

@with_connection
def insert_user(cursor, username, password_hash):
    try:
        cursor.execute(INSERT_USER, (username, password_hash))
        user_id = cursor.fetchone()[0]
        logger.info(f"User {username} inserted with id {user_id}")
        return user_id
    except Exception as e:
        logger.error(f"Error inserting user {username}: {e}")
        raise

@with_connection
def update_user(cursor, user_id, username, password_hash):
    try:
        cursor.execute(UPDATE_USER, (username, password_hash, user_id))
        updated_id = cursor.fetchone()
        if updated_id:
            logger.info(f"User with id {user_id} updated")
            return updated_id[0]
        return None
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise

@with_connection
def delete_user(cursor, user_id):
    try:
        cursor.execute(DELETE_USER, (user_id,))
        deleted_id = cursor.fetchone()
        if deleted_id:
            logger.info(f"User with id {user_id} deleted")
            return deleted_id[0]
        return None
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise

@with_connection
def get_user_by_username(cursor, username):
    try:
        cursor.execute(GET_USER_BY_USERNAME, (username,))
        result = cursor.fetchone()
        if result:
            return dict(zip([column[0] for column in cursor.description], result))
        return None
    except Exception as e:
        logger.error(f"Error retrieving user {username}: {e}")
        raise

@with_connection
def get_user_by_id(cursor, user_id):
    """
    Retrieves a user by their ID.
    """
    try:
        cursor.execute(GET_USER_BY_ID, (user_id,))
        result = cursor.fetchone()
        if result:
            return dict(zip([column[0] for column in cursor.description], result))
        return None
    except Exception as e:
        logger.error(f"Error retrieving user with ID {user_id}: {e}")
        raise

@with_connection
def get_all_users(cursor):
    try:
        cursor.execute(GET_ALL_USERS)
        return [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Error retrieving all users: {e}")
        raise
