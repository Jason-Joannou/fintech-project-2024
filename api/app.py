from flask import Flask

from api.routes.example_template import example_template_bp
from api.routes.onboarding import onboarding_bp
from api.routes.stokvel import stokvel_bp
from api.routes.users import users_bp
from api.routes.whatsapp_controller import whatsapp_bp

app = Flask(__name__)

app.register_blueprint(stokvel_bp)
app.register_blueprint(onboarding_bp)
app.register_blueprint(users_bp)
app.register_blueprint(whatsapp_bp)
app.register_blueprint(example_template_bp)


@app.route("/")
def index() -> str:
    """
    docstring
    """
    return "Stokvel API"


if __name__ == "__main__":
    app.run(debug=True)
