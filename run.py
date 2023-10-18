import os
import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# In-memory data store for registrations (replace with a database in a real application)
registrations = [
    {"id": 1, "name": "Rider 1", "guest_name": "Guest 1", "email": "rider1@example.com", "event": "party"},
    {"id": 2, "name": "Rider 2", "guest_name": "Guest 2", "email": "rider2@example.com", "event": "conference"},
    {"id": 3, "name": "Rider 3", "guest_name": "Guest 3", "email": "rider3@example.com", "event": "workshop"}
]

@app.route("/")
def index():
    return render_template("index.html", registrations=registrations)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/edit")
def edit():
    return render_template("edit.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        new_registration = {
            "id": len(registrations) + 1,
            "name": request.form.get("name"),
            "guest_name": request.form.get("guest_name"),
            "email": request.form.get("email"),
            "event": request.form.get("event")
        }
        registrations.append(new_registration)
        return redirect(url_for("index"))

    return render_template("register.html")

@app.route("/edit/<int:registration_id>", methods=["GET", "POST"])
def edit(registration_id):
    registration = next((r for r in registrations if r["id"] == registration_id), None)
    if registration is None:
        return "Registration not found", 404

    if request.method == "POST":
        registration["name"] = request.form.get("name")
        registration["guest_name"] = request.form.get("guest_name")
        registration["email"] = request.form.get("email")
        registration["event"] = request.form.get("event")
        return redirect(url_for("index"))

    return render_template("edit.html", registration=registration)

@app.route("/delete/<int:registration_id>")
def delete(registration_id):
    global registrations
    registrations = [r for r in registrations if r["id"] != registration_id]
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)