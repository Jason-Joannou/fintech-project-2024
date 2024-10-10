from flask import Blueprint, Response, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from database.azure_function_queries.queries import dynamic_query

database_bp = Blueprint("database", __name__)
BASE_ROUTE = "/database"


@database_bp.route(f"{BASE_ROUTE}/query_db", methods=["POST"])
def query_db() -> Response:
    try:
        # Extract the query and parameters from the request
        query = request.json.get("query")
        parameters = request.json.get("parameters", {})  # Default to empty dict

        # Validate input
        if not query:
            return jsonify({"error": "Query parameter is required."}), 400

        # Perform the query
        data = dynamic_query(query=query, params=parameters)

        return jsonify(data), 200
    except SQLAlchemyError as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500
