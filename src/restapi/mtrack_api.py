from flask import Flask
import json
from datetime import date, time, datetime
from src.router.mtrack_routes import init_routes  # Import the mtrack route initializer
from src.router.user_routes import init_user_routes  # Import the user route initializer
from src.router.notification_routes import init_notification_routes

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, time, datetime)):
            return obj.isoformat()
        return super().default(obj)

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

# Initialize routes for devices and user login
init_routes(app)          # Device-related routes
init_user_routes(app)     # User-related routes (login, update, delete)
init_notification_routes(app)

# This function stays here for starting the app externally
def start_flask_app():
    app.run(host='0.0.0.0', port=5000)
