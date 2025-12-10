import os
import uuid
import hashlib
import hmac
import base64
from square.client import Client
from square.environment import SquareEnvironment
from square.core.api_error import ApiError
from flask import Flask, jsonify, request
import json

app = Flask(__name__)

EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'

# Load Square configuration from environment variables or set here
SQUARE_ACCESS_TOKEN = os.getenv('SQUARE_ACCESS_TOKEN', 'EAAAlzRMgIWxXM897f1rIomyWEAN10MLEvr2-9OO1MRQZ-1MQ9dE4kms2SNdmrjd')  # Replace with your token
SQUARE_WEBHOOK_SIGNATURE_KEY = os.getenv("SQUARE_SIGNATURE", "LOdifFiRGfJy_jY_tHGQnQ")

# Initialize Square client
client = Client(
    access_token=SQUARE_ACCESS_TOKEN,  # Replace with your token
    environment=SquareEnvironment.SANDBOX  # Use SquareEnvironment.PRODUCTION for live
)

# Webhook signature verification
def is_valid_signature(request):
    signature_header = request.headers.get('x-square-signature')
    if not signature_header:
        return False

    # Square signs this as: base64(HMAC-SHA1(webhook_key, body))
    raw_body = request.data
    calculated_signature = base64.b64encode(
        hmac.new(
            SQUARE_WEBHOOK_SIGNATURE_KEY.encode(),
            raw_body,
            hashlib.sha1
        ).digest()
    ).decode()

    return hmac.compare_digest(calculated_signature, signature_header)

@app.route("/webhook/payment", methods=["POST"])
def handle_payment_webhook():
    if not is_valid_signature(request):
        return "Invalid signature", 403

    payload = request.json
    event_type = payload.get("event_type")
    print("✅ Received Event:", event_type)

    if event_type == "payment.created" or event_type == "payment.updated":
        payment = payload["data"]["object"]["payment"]

        status = payment.get("status")
        if status == "COMPLETED":
            amount = payment["amount_money"]["amount"]
            currency = payment["amount_money"]["currency"]
            note = payment.get("note", "No note provided")
            reference = payment.get("reference_id", "No reference")
            buyer_email = payment.get("buyer_email_address", "Unknown")
            customer_id = payment.get("customer_id", "No customer ID")
            receipt_url = payment.get("receipt_url", "No receipt")

            print("💰 Payment Completed:")
            print(f"  Amount: {amount} {currency}")
            print(f"  Note / Project: {note}")
            print(f"  Reference ID: {reference}")
            print(f"  Buyer Email: {buyer_email}")
            print(f"  Customer ID: {customer_id}")
            print(f"  Receipt: {receipt_url}")

            # Optionally: save to DB, send email, etc.

    return jsonify({"ok": True})

# Simulate a customer payment
def simulate_payment():
    body = {
        "source_id": "cnon:card-nonce-ok",  # Square test card nonce
        "idempotency_key": str(uuid.uuid4()),  # Unique key to ensure idempotency
        "amount_money": {
            "amount": 300000,  # $3000.00 in cents
            "currency": "USD"
        },
        "note": "Web design service for ACME Corp",
        "reference_id": "PO-123456",
        "buyer_email_address": "client@acmecorp.com"
    }

    # Access the Payments API using client.payments
    payments_api = client.payments

    try:
        result = payments_api.create_payment(body)
        print(f"✅ Test Payment Created {result}")
        # Check if the payment was successful
        if result.is_success():
            print("✅ Test Payment Created")
            print(result.body['payment'])  # Payment details
        elif result.is_error():
            print("❌ Error:", result.errors)
    except ApiError as e:
        # Handle Square API error
        print(f"❌ Square API Error: {e.errors}")
    except Exception as e:
        print(f"❌ Exception occurred: {e}")

# Routes for other features
@app.route("/generate-report", methods=["GET"])
def generate_report():
    # Replace with your actual logic for generating reports
    return jsonify({"status": "Report generated"})

@app.route('/click-app-workload', methods=['GET'])
def calculate_workload():
    start_date = request.args.get("start_date", default="2025-07-20")  # string, expected format: YYYY-MM-DD
    original_budget = float(request.args.get("original_budget", 3000))  # convert to float
    margin_profit = float(request.args.get("margin_profit", 0.30))  # convert to float (e.g. 0.30 for 30%)
    labor_per_hour = float(request.args.get("labor_per_hour", 80))  # convert to float
    client_name = request.args.get("client_name", default="Company XYZ")  # string

    profit = original_budget * margin_profit
    budget_after_profit_margin = original_budget - profit

    if budget_after_profit_margin <= 0:
        return {
            "status": "error",
            "message": "Adjusted budget after profit margin must be positive.",
            "original_budget": f"${original_budget:,.2f}",
            "profit": f"${profit:,.2f}",
            "adjusted_budget_exclude_profit": f"${budget_after_profit_margin:,.2f}"
        }
    return jsonify({"status": "success", "calculated_budget": budget_after_profit_margin})

if __name__ == "__main__":
    simulate_payment()
    app.run(host='127.0.0.1', port=7000, debug=True)
