import hashlib
import secrets
from django.conf import settings
from cryptography.fernet import Fernet
import base64
import logging

logger = logging.getLogger(__name__)

def generate_secure_token(length=32):
    """Generate a cryptographically secure token"""
    return secrets.token_urlsafe(length)

def hash_sensitive_data(data):
    """Hash sensitive data using SHA-256"""
    return hashlib.sha256(
        str(data).encode('utf-8')
    ).hexdigest()

class DataEncryption:
    def __init__(self):
        self.fernet = Fernet(settings.ENCRYPTION_KEY)

    def encrypt(self, data):
        """Encrypt sensitive data"""
        try:
            if isinstance(data, str):
                data = data.encode()
            return self.fernet.encrypt(data)
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            return None

    def decrypt(self, encrypted_data):
        """Decrypt encrypted data"""
        try:
            return self.fernet.decrypt(encrypted_data)
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            return None

def mask_sensitive_data(data, fields_to_mask):
    """Mask sensitive data in logs and responses"""
    masked_data = data.copy()
    for field in fields_to_mask:
        if field in masked_data:
            value = str(masked_data[field])
            masked_data[field] = f"{value[:4]}{'*' * (len(value)-4)}"
    return masked_data 