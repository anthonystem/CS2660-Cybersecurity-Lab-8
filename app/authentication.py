import hashlib
import os
from string import ascii_lowercase, ascii_uppercase

def hash_password(password: str) -> str:
    # Generate random salt that is 40 characters long.
    salt = os.urandom(20).hex()

    to_hash = salt + password
    to_hash = to_hash.encode("utf-8")

    password_hash = hashlib.sha256(to_hash).hexdigest()

    # Prepend salt to password_hash for storage.
    salt_and_password_hash = salt + password_hash

    return salt_and_password_hash


def authenticate(plaintext_password: str, stored: str) -> bool:
    salt_length = 40

    # Get salt and password hash from stored salt + hashed password.
    salt = stored[:salt_length]
    password_hash = stored[salt_length:]

    # Hash salt + plaintext password from user input.
    to_hash = salt + plaintext_password
    to_hash = to_hash.encode("utf-8")
    attempt_hash = hashlib.sha256(to_hash).hexdigest()

    return attempt_hash == password_hash


def validate_username(username: str) -> bool:
    """Verifies if username meets username requirements.
    The username requirements are as follows:
    - Minimum length is 3.
    - Maximum length is 16.

    Args:
        username (str): The username string to validate.

    Returns:
        bool: True if username meets requirements; otherwise, False.
    """
    if len(username) < 3 or len(username) > 16:
        return False
    
    return True


def validate_password(password: str) -> bool:
    """Checks that the password meets all the password requirements.
    These requirements include the following:
    - Minimum length is 8.
    - Maximum length is 25.
    - Has at least one number.
    - Has at least one lowercase letter.
    - Has at least one uppercase letter.
    - Has at least one special character (" !\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~").

    Args:
        password (str): The password string being validated.

    Returns:
        bool: True if the password meets the requirements; otherwise, False.
    """
    special_characters = " !\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"

    # Verify length requirement.
    if len(password) < 8 or len(password) > 25:
        return False
    
    # Verify character requirements.
    has_number = False
    has_lower = False
    has_upper = False
    has_special = False
    for char in password:
        if char.isdigit():
            has_number = True
        elif char in ascii_lowercase:
            has_lower = True
        elif char in ascii_uppercase:
            has_upper = True
        elif char in special_characters:
            has_special = True

    if not has_number or not has_lower or not has_upper or not has_special:
        return False
    
    return True
