from flask import Flask
from routes import join_stokvel, onboarding, user_info, whatsapp_controller, stokvel_info

app = Flask(__name__)

app.register_blueprint(join_stokvel)
app.register_blueprint(onboarding)
app.register_blueprint(user_info)
app.register_blueprint(whatsapp_controller)
app.register_blueprint(stokvel_info)

if __name__ == '__main__':
    app.run(debug=True)