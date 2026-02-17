from flask import Blueprint, request, jsonify
from app import db
from models import User
from utils import generate_tokens
from middleware import token_required
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength (minimum 8 characters)."""
    return len(password) >= 8

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400
    
    email = data.get('email').strip().lower()
    password = data.get('password')
    
    # Validate email format
    if not validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400
    
    # Validate password strength
    if not validate_password(password):
        return jsonify({"error": "Password must be at least 8 characters long"}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409
    
    try:
        # Create new user
        user = User(email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Generate tokens
        tokens = generate_tokens(user.id)
        
        return jsonify({
            "message": "User registered successfully",
            "user_id": user.id,
            "email": user.email,
            "tokens": tokens
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Registration failed", "details": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT tokens."""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400
    
    email = data.get('email').strip().lower()
    password = data.get('password')
    
    # Find user by email
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401
    
    try:
        # Generate tokens
        tokens = generate_tokens(user.id)
        
        return jsonify({
            "message": "Login successful",
            "user_id": user.id,
            "email": user.email,
            "tokens": tokens
        }), 200
    except Exception as e:
        return jsonify({"error": "Login failed", "details": str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user_id):
    """Get current user's profile (protected route)."""
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "user_id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat()
    }), 200
