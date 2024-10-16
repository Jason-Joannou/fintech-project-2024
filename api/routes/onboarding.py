from flask import Blueprint, Response, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from api.schemas.onboarding import OnboardUserSchema
from database.user_queries.queries import insert_user, insert_wallet
from whatsapp_utils._utils.twilio_messenger import send_notification_message

onboarding_bp = Blueprint("onboarding", __name__)

BASE_ROUTE = "/onboard"


@onboarding_bp.route(BASE_ROUTE)
def onboarding() -> str:
    """
    Render the Onboarding Template
    Displays the onboarding template page for new users.
    ---
    tags:
      - Onboard
    responses:
      200:
        description: Successfully loaded the onboarding template.
    """
    return render_template("onboarding_template.html")


@onboarding_bp.route(f"{BASE_ROUTE}/users", methods=["POST"])
def onboard_user() -> Response:
    """
    Handle Onboarding of a New User
    Accepts user information, stores it in the database, and sends a welcome notification.
    ---
    tags:
      - Onboard
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - id_number
            - cellphone_number
            - surname
            - name
            - wallet_id
          properties:
            id_number:
              type: string
              description: The ID number of the user.
              example: "1234567890123"
            cellphone_number:
              type: string
              description: The user's cellphone number.
              example: "+27821234567"
            surname:
              type: string
              description: The surname of the user.
              example: "Doe"
            name:
              type: string
              description: The first name of the user.
              example: "John"
            wallet_id:
              type: string
              description: The wallet ID assigned to the user.
              example: "wallet123"
    responses:
      302:
        description: Redirects to success or failure page after processing.
      500:
        description: Internal server error during onboarding.
    """
    try:
        user_data = OnboardUserSchema(
            **request.form.to_dict()
        )  # ** unpacks the dictionary

        # verify_wallet() <- send request to the wallet for verification

        insert_user(
            user_id=user_data.id_number,
            user_number=user_data.cellphone_number,
            user_surname=user_data.surname,
            user_name=user_data.name,
            ilp_wallet=user_data.wallet_id,
        )
        insert_wallet(
            user_id=user_data.id_number,
            user_wallet=user_data.wallet_id,
            user_balance=100,  # how should we fund user wallets initially?
        )
        # Prepare the notification message
        notification_message = (
            f"Welcome {user_data.name} {user_data.surname}!\n\n"
            f"Your user ID: {user_data.id_number}\n"
            f"Your wallet ID: {user_data.wallet_id}\n"
            f"Your wallet balance: {100}\n\n"
            f"Thank you for registering with us!"
        )

        # Send the notification message
        send_notification_message(
            to=f"whatsapp:{user_data.cellphone_number}", body=notification_message
        )
        return redirect(url_for("onboarding.success_user_creation"))

    except IntegrityError as integrity_error:
        print(f"SQL Error occurred during insert operations: {integrity_error}")
        return redirect(
            url_for("onboarding.failed_user_creation", error_message=integrity_error)
        )

    except SQLAlchemyError as sql_error:
        print(f"SQL Error occurred during insert operations: {sql_error}")
        return redirect(
            url_for("onboarding.failed_user_creation", error_message=sql_error)
        )

    except Exception as e:
        print(f"General Error occurred during insert operations: {e}")
        error_string = str(e)
        if "USERS.user_id" in str(error_string):
            error_message = "A user with this ID number already exists."
        elif "USERS.user_number" in str(error_string):
            error_message = "A user with this cellphone number already exists."
        else:
            error_message = "An unknown integrity error occurred."

        return redirect(
            url_for("onboarding.failed_user_creation", error_message=error_message)
        )


@onboarding_bp.route("/success_user_creation")
def success_user_creation() -> str:
    """
    Successful User Creation Page
    Displays a success message after a user is successfully onboarded.
    ---
    tags:
      - Onboard
    responses:
      200:
        description: Successfully created user, displays success message.
    """
    action = "Onboarding"
    success_message = (
        "User onboarding successful! You are ready to start using the application."
    )
    success_next_step_message = (
        "Please navigate back to WhatsApp for further functions."
    )

    return render_template(
        "action_success_template.html",
        action=action,
        success_message=success_message,
        success_next_step_message=success_next_step_message,
    )


@onboarding_bp.route("/failed_user_creation")
def failed_user_creation() -> str:
    """
    Failed User Creation Page
    Displays an error message if user onboarding fails.
    ---
    tags:
      - Onboard
    parameters:
      - in: query
        name: error_message
        type: string
        required: false
        description: The error message to display.
    responses:
      200:
        description: Failed user onboarding, displays error message.
    """

    action = "Onboarding"
    if request.args.get("error_message"):
        error_message = request.args.get("error_message")
    else:
        error_message = "User onboarding failed. Please try again later."
    failed_message = error_message
    # Define a better message here - depending on what needs to happen next
    failed_next_step_message = "Please navigate back to WhatsApp for further functions."

    return render_template(
        "action_failed_template.html",
        action=action,
        failed_message=failed_message,
        failed_next_step_message=failed_next_step_message,
    )
