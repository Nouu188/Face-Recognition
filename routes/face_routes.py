from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from routes.face_recognize import recognize_handler

face_bp = Blueprint("face_bp", __name__)

@face_bp.route("/")
def root_redirect():
    return redirect("/login")

@face_bp.route("/login")
def login_page():
    return render_template("login.html")

@face_bp.route("/welcome")
def welcome():
    user_id = request.args.get("user_id")
    return render_template("welcome.html", user_id=user_id)

@face_bp.route("/recognize", methods=["POST"])
def recognize():
    return recognize_handler()
