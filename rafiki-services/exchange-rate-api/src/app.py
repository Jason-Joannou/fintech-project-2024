from flask import Flask, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

# Swagger UI setup
SWAGGER_URL = '/swagger'
API_URL = '/static/openapi.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Rafiki Exchange Rates"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Sample data for exchange rates
exchange_rates = {
    'USD': {
        'EUR': 1.1602,
        'ZAR': 17.3792
    },
    'ZAR': {
        'USD': 0.0575,
        'EUR': 0.0667
    }
}

@app.route("/", methods=['GET'])
def index():
    return "Rafiki Exchange Rates"

@app.route('/rates', methods=['GET'])
def get_rates():
    base = request.args.get('base')
    if not base or base not in exchange_rates:
        return jsonify({'error': 'Base currency not found'}), 404

    rates = exchange_rates[base]
    return jsonify({
        'base': base,
        'rates': rates
    })

if __name__ == '__main__':
    app.run(debug=True)