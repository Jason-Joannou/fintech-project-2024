from flasgger import Swagger
from flask import Flask
from flask_cors import CORS  # Import Flask-CORS

from api.routes.database import database_bp
from api.routes.example_template import example_template_bp
from api.routes.onboarding import onboarding_bp
from api.routes.stokvel import stokvel_bp
from api.routes.users import users_bp
from api.routes.whatsapp_controller import whatsapp_bp

app = Flask(__name__)

# Enable CORS for all routes and all origins
CORS(app)  # Add this line to enable CORS for the entire app

# Initialize Swagger
app.config["SWAGGER"] = {
    "title": "Stokvel API",
    "uiversion": 3,  # Use Swagger UI version 3 for better compatibility
    "version": "1.0",
    "description": "API documentation for the Stokvel system",
}
swagger = Swagger(app)

# Registering blueprints
app.register_blueprint(stokvel_bp)
app.register_blueprint(onboarding_bp)
app.register_blueprint(users_bp)
app.register_blueprint(whatsapp_bp)
app.register_blueprint(example_template_bp)
app.register_blueprint(database_bp)


@app.route("/")
def index() -> str:
    """
    Root route
    ---
    responses:
      200:
        description: Returns a welcome message for the Stokvel API.
    """
    return "Stokvel API"


if __name__ == "__main__":
    app.run(debug=True)
