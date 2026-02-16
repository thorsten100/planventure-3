import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta

def hash_password(password):
    """
    Hash a password using bcrypt with a salt.
    
    Args:
        password (str): The plaintext password to hash
        
    Returns:
        str: The hashed password
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def verify_password(password, password_hash):
    """
    Verify a plaintext password against a hashed password.
    
    Args:
        password (str): The plaintext password to verify
        password_hash (str): The hashed password to compare against
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def generate_tokens(user_id):
    """Generate access and refresh tokens for a user."""
    access_token = create_access_token(
        identity=user_id,
        expires_delta=timedelta(hours=1)
    )
    refresh_token = create_refresh_token(
        identity=user_id,
        expires_delta=timedelta(days=30)
    )
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }