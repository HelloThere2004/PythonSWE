import psycopg2
import logging
from src.config.env_loader import POSTGRE_HOST, POSTGRE_PORT, POSTGRE_DATABASE, POSTGRE_USERNAME, POSTGRE_PASSWORD

logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        connection = psycopg2.connect(
            host=POSTGRE_HOST,
            port=POSTGRE_PORT,
            database=POSTGRE_DATABASE,
            user=POSTGRE_USERNAME,
            password=POSTGRE_PASSWORD
        )
        logger.info("Database connection established successfully")
        return connection
    except (Exception, psycopg2.Error) as error:
        logger.error(f"Error while connecting to PostgreSQL: {error}")
        raise
