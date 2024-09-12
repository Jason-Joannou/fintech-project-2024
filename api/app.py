from flask import Flask
from api.routes.join_stokvel import join_stokvel_bp
from api.routes.onboarding import onboarding_bp
from api.routes.user_info import user_info_bp
from api.routes.whatsapp_controller import whatsapp_bp
from api.routes.stokvel_info import stokvel_info_bp

app = Flask(__name__)

app.register_blueprint(join_stokvel_bp)
app.register_blueprint(onboarding_bp)
app.register_blueprint(user_info_bp)
app.register_blueprint(whatsapp_bp)
app.register_blueprint(stokvel_info_bp)


@app.route('/')
def index():
    return "Stokvel API"

if __name__ == '__main__':
    app.run(debug=True)