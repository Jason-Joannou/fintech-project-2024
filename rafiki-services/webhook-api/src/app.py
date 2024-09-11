import uuid

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

# Sample data for demonstration purposes
user_accounts = {
    'user1': {'balance': 1000},
    'user2': {'balance': 500}
}

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook_listener():
    event = request.json
    event_id = event.get('id')
    event_type = event.get('type')
    event_data = event.get('data')

    # Process the event based on its type
    if event_type == 'incoming_payment.created':
        handle_incoming_payment_created(event_data)
    elif event_type == 'incoming_payment.completed':
        handle_incoming_payment_completed(event_data)
    elif event_type == 'incoming_payment.expired':
        handle_incoming_payment_expired(event_data)
    elif event_type == 'outgoing_payment.created':
        handle_outgoing_payment_created(event_data)
    elif event_type == 'outgoing_payment.completed':
        handle_outgoing_payment_completed(event_data)
    elif event_type == 'outgoing_payment.failed':
        handle_outgoing_payment_failed(event_data)
    elif event_type == 'wallet_address.web_monetization':
        handle_wallet_address_web_monetization(event_data)
    elif event_type == 'wallet_address.not_found':
        handle_wallet_address_not_found(event_data)
    elif event_type == 'asset.liquidity_low':
        handle_asset_liquidity_low(event_data)
    elif event_type == 'peer.liquidity_low':
        handle_peer_liquidity_low(event_data)
    else:
        return jsonify({'error': 'Unknown event type'}), 400

    # Respond with a 200 status code to acknowledge receipt of the event
    return jsonify({'status': 'success'}), 200

# Event handlers
def handle_incoming_payment_created(data):
    print(f"Incoming payment created: {data}")

def handle_incoming_payment_completed(data):
    print(f"Incoming payment completed: {data}")
    # Example: Credit the user's account with the received amount
    wallet_address_id = data.get('walletAddressId')
    received_amount = data.get('receivedAmount', {}).get('value', 0)
    user_id = get_user_id_from_wallet_address(wallet_address_id)
    if user_id and user_id in user_accounts:
        user_accounts[user_id]['balance'] += received_amount

def handle_incoming_payment_expired(data):
    print(f"Incoming payment expired: {data}")

def handle_outgoing_payment_created(data):
    print(f"Outgoing payment created: {data}")

def handle_outgoing_payment_completed(data):
    print(f"Outgoing payment completed: {data}")

def handle_outgoing_payment_failed(data):
    print(f"Outgoing payment failed: {data}")

def handle_wallet_address_web_monetization(data):
    print(f"Wallet address web monetization: {data}")

def handle_wallet_address_not_found(data):
    print(f"Wallet address not found: {data}")

def handle_asset_liquidity_low(data):
    print(f"Asset liquidity low: {data}")

def handle_peer_liquidity_low(data):
    print(f"Peer liquidity low: {data}")

def get_user_id_from_wallet_address(wallet_address_id):
    # Mock function to get user ID from wallet address ID
    # In a real implementation, this would query your database or another data source
    return 'user1' if wallet_address_id == 'some-wallet-address-id' else None

if __name__ == '__main__':
    app.run(debug=True)