import bcrypt
import logging

logger = logging.getLogger(__name__)

class PasswordService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            # Ensure the hashed_password is in bytes if it's a string
            if isinstance(hashed_password, str):
                hashed_password = hashed_password.encode('utf-8')
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)
        except Exception as e:
            logger.error(f"Password verification failed: {str(e)}")
            return False

    @staticmethod
    def get_password_hash(password: str) -> str:
        try:
            # Generate a salt and hash the password
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')  # Return as string for storage
        except Exception as e:
            logger.error(f"Password hashing failed: {str(e)}")
            raise ValueError("Failed to hash password")
