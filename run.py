import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, abort

app = Flask(__name__)

app.secret_key = os.urandom(24)

# Initialize an empty list to store registration
registrations = []

# Define the path to the JSON file
json_file_path = "data/members.json"

# Check if the JSON file exists, and load data if it does
if os.path.exists(json_file_path):
    with open(json_file_path, "r") as json_data:
        registrations = json.load(json_data)

@app.route("/")
def index():
    return render_template("index.html", registrations=registrations, enumerate=enumerate)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    # Provide a default value for index
    index = None

    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        guest_name = request.form.get("guest_name")
        email = request.form.get("email")
        event = request.form.get("event")

        # Create a registration dictionary
        registration = {"name": name, "guest_name": guest_name,
                        "email": email, "event": event}

        # Add registration to the list
        registrations.append(registration)

        # Save registrations to the JSON file
        with open(json_file_path, "w") as json_file:
            json.dump(registrations, json_file, indent=4)

        # Store the user's email in the session
        session["user_email"] = email

        # Redirect to the index page with the updated registrations
        return redirect(url_for("index"))

    # Pass the index value to the template
    return render_template("register.html", index=index)

@app.route("/edit/<int:index>", methods=["GET", "POST"])
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
            registrations[index] = {"name": name, "guest_name": guest_name, "email": email, "event": event}

            # Redirect to the index page with the updated registrations
            return redirect(url_for("index"))
        else:
            # User doesn't have permission, handle accordingly (redirect, abort, etc.)
            abort(403)  # HTTP 403 Forbidden

    registration = registrations[index]
    return render_template("edit.html", registration=registration, index=index)

@app.route("/delete/<int:index>")
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

if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)