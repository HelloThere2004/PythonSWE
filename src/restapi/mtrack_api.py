from flask import Flask, jsonify, request
from werkzeug.exceptions import NotFound, InternalServerError
from src.controllers.mtrack_controller import get_device_last_data, get_device_location_history, get_devices
import logging
from datetime import date, time, datetime
import json

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, time, datetime)):
            return obj.isoformat()
        return super().default(obj)

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

logger = logging.getLogger(__name__)

@app.errorhandler(500)
def internal_server_error(error):
    logger.error(f"500 Internal Server Error: {str(error)}, Route: {request.url}")
    return jsonify(error="Internal Server Error", message=str(error)), 500

@app.route('/devices/<string:device_id>/last_data')
def device_last_data(device_id):
    try:
        result = get_device_last_data(device_id)
        if result:
            return jsonify(result)
        raise NotFound("Device not found or no data available")
    except NotFound as e:
        logger.warning(f"Device not found: {device_id}")
        return jsonify(error="Not Found", message=str(e)), 404
    except Exception as e:
        logger.error(f"Error in device_last_data: {str(e)}")
        return jsonify(error="Internal Server Error", message="An unexpected error occurred"), 500

@app.route('/devices/<string:device_id>/locations')
def device_locations(device_id):
    try:
        result = get_device_location_history(device_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in device_locations: {str(e)}")
        return jsonify(error="Internal Server Error", message="An unexpected error occurred"), 500

@app.route('/devices')
def all_devices():
    try:
        result = get_devices()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in all_devices: {str(e)}")
        return jsonify(error="Internal Server Error", message="An unexpected error occurred"), 500

def start_flask_app():
    app.run(host='0.0.0.0', port=5000)
