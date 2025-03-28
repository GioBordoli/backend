# auth_utils.py
import os
import jwt
from datetime import datetime, timedelta
from flask import request, jsonify

SECRET_KEY = os.getenv("JWT_SECRET", "your_default_secret")  # change this in production

def generate_token(user_id: str):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=7),  # token valid for 7 days
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Decorator for routes that require token authentication
from functools import wraps
from flask import request

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Token can be in the Authorization header as Bearer token
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            parts = auth_header.split()
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]
        if not token:
            return jsonify({"error": "Token is missing!"}), 401
        user_id = verify_token(token)
        if not user_id:
            return jsonify({"error": "Token is invalid or expired!"}), 401
        # Pass user_id to the route via kwargs
        return f(user_id, *args, **kwargs)
    return decorated
