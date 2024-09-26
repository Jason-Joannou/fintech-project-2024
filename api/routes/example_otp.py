from flask import Blueprint, jsonify, render_template, request

from api._utils.otp import send_otp_to_number, verify_otp

otp_bp = Blueprint("otp", __name__)

BASE_ROUTE = "/otp"  # This wont be otp, this will be admin for example and then we utilize the otp methods in the admin endpoints


# OTP SHOULD BE A UTILS FILE TO USE IN ENDPOINTS


@otp_bp.route(f"{BASE_ROUTE}/")
def index():
    return render_template("otp_example_template.html")


# Step 1: Enter phone number (capture next step here)
@otp_bp.route(f"{BASE_ROUTE}/send_otp", methods=["POST"])
def send_otp():
    phone_number = request.form.get("user_number")

    if not phone_number:
        return jsonify({"status": "error", "message": "Phone number is required"}), 400

    result = send_otp_to_number(phone_number)

    if result == "otp_sent":
        return jsonify({"status": "otp_sent", "message": "OTP sent successfully."})
    elif result == "otp_pending":
        return jsonify(
            {
                "status": "otp_pending",
                "message": "An OTP is already pending. Please check your messages.",
            }
        )
    else:
        return jsonify({"status": "error", "message": "Failed to send OTP."}), 500


@otp_bp.route(f"{BASE_ROUTE}/verify_otp", methods=["POST"])
def verify_otp_endpoint():
    phone_number = request.form.get("user_number")
    otp = request.form.get("user_otp")

    if not phone_number or not otp:
        return (
            jsonify(
                {"status": "error", "message": "Phone number and OTP are required"}
            ),
            400,
        )

    result = verify_otp(phone_number, otp)

    if result == "otp_valid":
        print(result)
        return jsonify(
            {"status": "otp_verified", "message": "OTP verified successfully."}
        )
    elif result == "otp_expired":
        print(result)
        return jsonify(
            {
                "status": "otp_expired",
                "message": "OTP has expired. Please request a new one.",
            }
        )
    else:
        print("invalid")
        return (
            jsonify(
                {"status": "otp_invalid", "message": "Invalid OTP. Please try again."}
            ),
            400,
        )
