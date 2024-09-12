from flask import render_template, request, redirect, url_for, Blueprint

example_template_bp = Blueprint("example_template", __name__)

BASE_ROUTE = "/example_template"


@example_template_bp.route(BASE_ROUTE)
def example_template():
    """
    docstrings
    """
    return render_template("example_template.html")

@example_template_bp.route(f'{BASE_ROUTE}/submit', methods=['POST'])
def submit():
    # Get user inputs from the form
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    # Process the data as needed (e.g., save to database, send email, etc.)
    # For this example, just print the data
    print(f"Name: {name}, Email: {email}, Message: {message}")

    # Redirect to a success page or back to the form
    return redirect(url_for(f'{BASE_ROUTE.removeprefix("/")}.success'))


@example_template_bp.route('/success')
def success():
    return "Form submitted successfully!"
