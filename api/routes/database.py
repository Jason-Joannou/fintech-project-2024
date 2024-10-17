from flask import Blueprint, Response, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from database.azure_function_queries.queries import (
    dynamic_read_operation,
    dynamic_write_operation,
)

database_bp = Blueprint("database", __name__)
BASE_ROUTE = "/database"


@database_bp.route(f"{BASE_ROUTE}/query_db", methods=["POST"])
def query_db() -> Response:
    """
    Execute a Read Operation
    Executes a read operation (SELECT query) on the database using a dynamic query and parameters.
    ---
    tags:
      - Database
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - query
          properties:
            query:
              type: string
              description: SQL SELECT query to execute.
              example: "SELECT * FROM users WHERE id = :user_id"
            parameters:
              type: object
              description: Parameters to be used with the SQL query.
              example: {"user_id": 1}
    responses:
      200:
        description: Successfully retrieved data from the database.
        schema:
          type: array
          items:
            type: object
      400:
        description: Missing required query parameter.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Query parameter is required."
      500:
        description: Database error occurred.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Database error: ..."
    """
    try:
        # Extract the query and parameters from the request
        query = request.json.get("query")
        parameters = request.json.get("parameters", {})  # Default to empty dict

        # Validate input
        if not query:
            return jsonify({"error": "Query parameter is required."}), 400

        # Perform the query
        data = dynamic_read_operation(query=query, params=parameters)

        return jsonify(data), 200
    except SQLAlchemyError as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500


@database_bp.route(f"{BASE_ROUTE}/write_db", methods=["POST"])
def write_db() -> Response:
    """
    Execute a Write Operation
    Executes a write operation (INSERT, UPDATE, DELETE) on the database using a dynamic query and parameters.
    ---
    tags:
      - Database
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - query
          properties:
            query:
              type: string
              description: SQL INSERT/UPDATE/DELETE query to execute.
              example: "INSERT INTO users (name, email) VALUES (:name, :email)"
            parameters:
              type: object
              description: Parameters to be used with the SQL query.
              example: {"name": "John Doe", "email": "john@example.com"}
    responses:
      200:
        description: Successfully executed the write operation.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "success"
      400:
        description: Missing required query parameter.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Query parameter is required."
      500:
        description: Database error occurred.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Database error: ..."
    """
    try:
        # Extract the query and parameters from the request
        query = request.json.get("query")
        parameters = request.json.get("parameters", {})  # Default to empty dict

        # Validate input
        if not query:
            return jsonify({"error": "Query parameter is required."}), 400

        # Perform the query
        dynamic_write_operation(query=query, params=parameters)

        return jsonify({"message": "success"}), 200
    except SQLAlchemyError as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500
