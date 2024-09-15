from flask import Blueprint, redirect, render_template, request, url_for
import database.queries as queries 
from utils.user import User
from utils.wallet import Wallet

from sqlalchemy.exc import SQLAlchemyError


onboarding_bp = Blueprint("onboarding", __name__)

BASE_ROUTE = "/onboard"


@onboarding_bp.route(BASE_ROUTE)
def onboarding():
    """
    docstring
    """
    return render_template("onboarding_template.html")

@onboarding_bp.route(f"{BASE_ROUTE}/users", methods=["POST"])
def onboard_user():
    """
    Handles onboarding of a new user.
    """
    try:
        name = request.form["name"]
        surname = request.form["surname"]
        cell_number = request.form["cellphone_number"]
        id_number = request.form["id_number"]

        flag = queries.check_if_number_exists_sqlite(cell_number)
        print(f"Check if number exists: {flag}")

        if not flag:
            user = User(name=name, surname=surname, cell_number=cell_number, id_number=id_number, wallet_id="")
            wallet = Wallet(user.id_number, user_wallet="ILP_test_string", user_balance=100)

            try:
                queries.insert_user(
                    user_id=user.id_number,
                    user_number=user.cell_number,
                    user_surname=user.surname,
                    user_name=user.name,
                    ILP_wallet=wallet.id
                )
                queries.insert_wallet(
                    user_id=user.id_number,
                    user_wallet=wallet.id,
                    userbalance=wallet.user_balance
                )

                return redirect(url_for('onboarding.success_user_creation'))

            except SQLAlchemyError as sql_error:
                print(f"SQL Error occurred during insert operations: {sql_error}")
                return redirect(url_for('onboarding.failed_user_creation'))

            except Exception as e:
                print(f"General Error occurred during insert operations: {e}")
                return redirect(url_for('onboarding.failed_user_creation'))
        
        # If the cell number already exists or other logic, handle accordingly
        return redirect(url_for('onboarding.failed_user_creation'))

    except Exception as e:
        # Exception handling for errors outside the inner try block
        print(f"Error occurred: {e}")
        return redirect(url_for('onboarding.failed_user_creation'))


@onboarding_bp.route(f"{BASE_ROUTE}/stokvels", methods=["POST"])
def onboard_stokvel():
    """
    docstring
    """
    return redirect(url_for(f'{BASE_ROUTE.removeprefix("/")}.success_stockvel_creation'))


@onboarding_bp.route("/success_user_creation")
def success_user_creation():
    """
    docstring
    """
    return render_template("user_onboarding_success.html")

@onboarding_bp.route("/failed_user_creation")
def failed_user_creation():
    """
    docstring
    """
    return render_template("user_onboarding_failed.html")


@onboarding_bp.route("/success_stockvel_creation")
def success_stockvel_creation():
    """
    docstring
    """
    return "Stockvel created successfully!"
