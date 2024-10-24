from flask import jsonify, request
from werkzeug.exceptions import NotFound, BadRequest
from src.controllers.mtrack_controller import (
    get_device_last_data,
    get_device_location_history,
    get_devices,
    get_device_data_by_date_range
)
from src.middleware.auth_middleware import token_required
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def init_routes(app):
    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error(f"500 Internal Server Error: {str(error)}, Route: {request.url}")
        return jsonify(error="Internal Server Error", message=str(error)), 500

    @app.route('/api/devices/<string:device_id>/last-data')
    @token_required
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

    @app.route('/api/devices/<string:device_id>/locations')
    @token_required
    def device_locations(device_id):
        try:
            result = get_device_location_history(device_id)
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error in device_locations: {str(e)}")
            return jsonify(error="Internal Server Error", message="An unexpected error occurred"), 500

    @app.route('/api/devices')
    @token_required
    def all_devices():
        try:
            result = get_devices()
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error in all_devices: {str(e)}")
            return jsonify(error="Internal Server Error", message="An unexpected error occurred"), 500

    @app.route('/api/devices/<string:device_id>/data')
    @token_required
    def device_data_by_date_range(device_id):
        try:
            # Get start_date and end_date from query parameters
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')

            # Validate that both parameters are provided
            if not start_date or not end_date:
                raise BadRequest("Both start_date and end_date query parameters are required")

            try:
                # Validate date format
                start_date = datetime.fromisoformat(start_date)
                end_date = datetime.fromisoformat(end_date)
            except ValueError:
                raise BadRequest("Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")

            # Validate date range
            if end_date < start_date:
                raise BadRequest("end_date must be greater than or equal to start_date")

            result = get_device_data_by_date_range(device_id, start_date, end_date)
            if not result:
                return jsonify([])  # Return empty array if no data found

            return jsonify(result)

        except BadRequest as e:
            logger.warning(f"Bad request for device {device_id}: {str(e)}")
            return jsonify(error="Bad Request", message=str(e)), 400
        except Exception as e:
            logger.error(f"Error in device_data_by_date_range: {str(e)}")
            return jsonify(error="Internal Server Error", message="An unexpected error occurred"), 500
