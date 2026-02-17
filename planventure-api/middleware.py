from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps

def token_required(f):
    """Decorator to require a valid JWT token for route access."""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            return f(current_user_id, *args, **kwargs)
        except Exception as e:
            return jsonify({"error": "Unauthorized", "details": str(e)}), 401
    return decorated

def token_optional(f):
    """Decorator to optionally verify JWT token (allows both authenticated and unauthenticated requests)."""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
            current_user_id = get_jwt_identity()
            return f(current_user_id, *args, **kwargs)
        except Exception as e:
            return jsonify({"error": "Invalid token", "details": str(e)}), 401
    return decorated
