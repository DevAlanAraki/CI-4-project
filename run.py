import os
import json

from flask import Flask, render_template, request, redirect, url_for, session, abort, flash
if os.path.exists("env.py"):
    import env

from flask_mail import Mail, Message
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

mail = Mail(app)

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'alanaraki90@gmail.com'
app.config['MAIL_PASSWORD'] = 'pqpk utfp fade ciji'
app.config['MAIL_DEFAULT_SENDER'] = 'alanaraki90@gmail.com'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


# Initialize an empty list to store registration
registrations = []

# Define the path to the JSON file
json_file_path = "data/members.json"

# Check if the JSON file exists, and load data if it does
if os.path.exists(json_file_path):
    with open(json_file_path, "r") as json_data:
        registrations = json.load(json_data)


def get_stored_hashed_password(email):
    for registration in registrations:
        if registration["email"] == email:
            return registration["password"]
    return None  # Return None if the email is not found


@app.route("/")
def index():
    return render_template("index.html", registrations=registrations, enumerate=enumerate)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        flash("Thanks {}, we have received your message!".format(
            request.form.get("name")))
    return render_template("contact.html", page_title="contact")

@app.route("/register", methods=["GET", "POST"])
def register():
    # Provide a default value for index
    index = None

    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        guest_name = request.form.get("guest_name")
        email = request.form.get("email")
        password = request.form.get("password")  # Ensure this line is present
        event = request.form.get("event")

        # Hash the password before storing it
        hashed_password = generate_password_hash(
            password, method='pbkdf2:sha256')

        # Create a registration dictionary
        registration = {"name": name, "guest_name": guest_name,
                        "email": email, "password": hashed_password, "event": event}

        # Add registration to the list
        registrations.append(registration)

        # Save registrations to the JSON file
        with open(json_file_path, "w") as json_file:
            json.dump(registrations, json_file, indent=4)

        # Store the user's email in the session
        session["user_email"] = email

        # Redirect to the index page with the updated registrations
        return render_template("register.html", registration_success=True)

    # Pass the index value to the template
    return render_template("register.html", registration_success=False)


def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if "user_email" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return decorated_function


def ownership_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        index = kwargs.get("index")

        if index is not None:
            registration = registrations[index]

            # Debugging statements
            print(f"User email in session: {session.get('user_email')}")
            print(f"Registration email: {registration.get('email')}")

            # Check if the logged-in user owns this registration
            if session.get("user_email") == registration["email"]:
                return func(*args, **kwargs)
            else:
                abort(403)  # User doesn't have permission

        abort(400)  # Invalid request

    return decorated_function


@app.route("/edit/<int:index>", methods=["GET", "POST"])
@login_required
@ownership_required
def edit(index):
    # Check if the user is logged in
    if "user_email" not in session:
        abort(401)  # HTTP 401 Unauthorized

    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        guest_name = request.form.get("guest_name")
        email = request.form.get("email")
        event = request.form.get("event")

        # Check if the logged-in user owns this registration
        if session["user_email"] == registrations[index]["email"]:
            # Update the registration
            registrations[index] = {
                "name": name, "guest_name": guest_name, "email": email, "event": event}

            # Redirect to the index page with the updated registrations
            return render_template("edit.html", registration=registrations, index=index, edit_success=True)
            # Pass the index value to the template
        else:
            # User doesn't have permission, handle accordingly (redirect, abort, etc.)
            abort(403)  # HTTP 403 Forbidden

    registration = registrations[index]
    return render_template("edit.html", registration=registration, index=index)


@app.route("/delete/<int:index>")
@login_required
@ownership_required
def delete(index):
    # Check if the user is logged in
    if "user_email" not in session:
        abort(401)  # HTTP 401 Unauthorized

    # Check if the logged-in user owns this registration
    if session["user_email"] == registrations[index]["email"]:
        del registrations[index]
        return redirect(url_for("index"))
    else:
        # User doesn't have permission, handle accordingly (redirect, abort, etc.)
        abort(403)  # HTTP 403 Forbidden

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Retrieve the hashed password from the stored data
        stored_hashed_password = get_stored_hashed_password(email)

        # Check if the provided password matches the stored hashed password
        if stored_hashed_password and check_password_hash(stored_hashed_password, password):
            session["user_email"] = email
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials")

    return render_template("login.html")


@app.route("/logout")
def logout():
    # Clear the user's email from the session
    session.pop("user_email", None)

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)
