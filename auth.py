# auth.py
import bcrypt
from flask import Blueprint, request, jsonify
from database import users_collection
from auth_utils import generate_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    weight = data.get("weight")
    gender = data.get("gender")
    age = data.get("age")

    if not username or not email or not password:
        return jsonify({"error": "Missing username, email, or password"}), 400

    existing_user = users_collection.find_one({
        "$or": [{"username": username}, {"email": email}]
    })
    if existing_user:
        return jsonify({"error": "Username or email already taken"}), 400

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    user_doc = {
        "username": username,
        "email": email,
        "passwordHash": hashed_pw,
        "first_name": first_name,
        "last_name": last_name,
        "weight": weight,
        "gender": gender,
        "age": age,
    }
    result = users_collection.insert_one(user_doc)
    user_id = str(result.inserted_id)
    token = generate_token(user_id)
    return jsonify({"message": "User registered successfully", "token": token}), 200

@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    user = users_collection.find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not bcrypt.checkpw(password.encode("utf-8"), user["passwordHash"]):
        return jsonify({"error": "Invalid credentials"}), 401

    user_id = str(user["_id"])
    token = generate_token(user_id)
    return jsonify({"message": "Login successful", "token": token}), 200
