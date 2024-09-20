from flask import Blueprint, Response, redirect, render_template, request, url_for
from database.sqlite_connection import SQLiteConnection
from sqlalchemy import text
example_template_bp = Blueprint("example_template", __name__)


BASE_ROUTE = "/example_template"
db_conn = SQLiteConnection(database= "./database/test_db.db")

@example_template_bp.route(BASE_ROUTE)
def example_template() -> str:
    """
    docstring
    """
    return render_template("onboarding_template.html")


@example_template_bp.route(f"{BASE_ROUTE}/submit", methods=["POST"])
def submit() -> Response:
    """
    docstring
    """
    # Get user inputs from the form
    name = request.form["name"]
    email = request.form["email"]
    message = request.form["message"]

    with db_conn.connect() as conn: 
        #query = f"INSERT INTO comments (name, email, comment) VALUES ('{name}', '{email}', '{message}');"
        query= 'INSERT INTO comments (name, email, comment) VALUES (:name, :email, :message);'
        conn.execute(text(query), parameters= {"name":name, "email":email, "message":message})
        conn.commit()

    # Process the data as needed (e.g., save to database, send email, etc.)
    # For this example, just print the data
    print(f"Name: {name}, Email: {email}, Message: {message}")

    # Redirect to a success page or back to the form
    return redirect(url_for(f'{BASE_ROUTE.removeprefix("/")}.success'))


@example_template_bp.route("/success")
def success() -> str:
    """
    docstring
    """
    return "Form submitted successfully!"
