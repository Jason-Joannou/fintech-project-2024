# This webhook class is responsivle for the events that happen on our rafiki instance
# Listed below are the events that occur when transcations occur on our rafiki instance
# We will need to have event listeners to handle these events in our rafiki instance

# USE openAPI specification examples provided to build necessary endpoints for rafiki instance

from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class WebhookEvent(Base):
    __tablename__ = 'webhook_events'
    id = Column(Integer, primary_key=True)
    event_id = Column(String, unique=True, nullable=False)
    event_type = Column(String, nullable=False)
    data = Column(JSON, nullable=False)
    received_at = Column(DateTime, default=datetime.now())

def handle_incoming_payment_created(data):
    print(f"Incoming payment created: {data}")

def handle_incoming_payment_completed(data):
    print(f"Incoming payment completed: {data}")

def handle_incoming_payment_expired(data):
    print(f"Incoming payment expired: {data}")

def handle_outgoing_payment_created(data):
    print(f"Outgoing payment created: {data}")

def handle_outgoing_payment_completed(data):
    print(f"Outgoing payment completed: {data}")

def handle_outgoing_payment_failed(data):
    print(f"Outgoing payment failed: {data}")

def handle_wallet_address_not_found(data):
    print(f"Wallet address not found: {data}")

def handle_wallet_address_web_monetization(data):
    print(f"Wallet address web monetization: {data}")

def handle_asset_liquidity_low(data):
    print(f"Asset liquidity low: {data}")

def handle_peer_liquidity_low(data):
    print(f"Peer liquidity low: {data}")