# backend/utils/auth_guard.py

from flask import session, jsonify

from functools import wraps
from flask import session, jsonify

def require_role(required_role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                return jsonify({"error": "Unauthorized"}), 401

            if session.get("role") != required_role:
                return jsonify({"error": "Forbidden"}), 403

            # ✅ IMPORTANT: allow route execution
            return func(*args, **kwargs)
        return wrapper
    return decorator
