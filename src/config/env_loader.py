from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

POSTGRE_PORT=int(os.getenv('POSTGRE_PORT'))
POSTGRE_HOST=os.getenv('POSTGRE_HOST')
POSTGRE_DATABASE=os.getenv('POSTGRE_DATABASE')
POSTGRE_USERNAME=os.getenv('POSTGRE_USERNAME')
POSTGRE_PASSWORD=os.getenv('POSTGRE_PASSWORD')
SECRET_KEY=os.getenv("SECRET_KEY")
