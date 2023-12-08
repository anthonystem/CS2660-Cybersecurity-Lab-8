import config
import hashlib
import os
from string import ascii_lowercase, ascii_uppercase, digits
import secrets
import sqlite3
from typing import Union

def hash_password(password: str) -> str:
    """Hashes a given password and pre-pends a salt of
    length 40.

    Args:
        password (str): The password to hash.

    Returns:
        str: The salted and hashed password.
    """
    # Generate random salt that is 40 characters long.
    salt = os.urandom(20).hex()

    to_hash = salt + password
    to_hash = to_hash.encode("utf-8")

    password_hash = hashlib.sha256(to_hash).hexdigest()

    # Prepend salt to password_hash for storage.
    salt_and_password_hash = salt + password_hash

    return salt_and_password_hash


def authenticate(plaintext_password: str, stored: str) -> bool:
    """Verifies if a provided plaintext password matches a corresponding
    salted password, with a salt length of 40, stored in the database.

    Args:
        plaintext_password (str): The password to authenticate.
        stored (str): The salted password hash in the database.

    Returns:
        bool: True if the password matches; otherwise, False.
    """
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


def username_exists(test_username: str) -> bool:
    """Checks if the User table already contains an account with the
    supplied username.

    Args:
        test_username (str): The username to be checked.

    Returns:
        bool: True if the username already exists; otherwise, false.
    """
    connection = sqlite3.connect(config.DATABASE_FILE)
    cursor = connection.cursor()

    cursor.execute("SELECT EXISTS(SELECT 1 FROM Users WHERE username = ? LIMIT 1)", (test_username,))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return True if result[0] == 1 else False


def block_user(username: str):
    """Blocks a specified user from being able to log in.

    Args:
        username (str): The username of the user to block.
    """
    connection = sqlite3.connect(config.DATABASE_FILE)
    cursor = connection.cursor()

    cursor.execute("UPDATE Users SET blocked = 1 WHERE username = ?", (username,))
    connection.commit()

    cursor.close()
    connection.close()


def has_access_permission(user_access_level: str, minimum_access_level: str) -> bool:
    """Checks if a user has a sufficient access level for access permission.
    Access levels include the following:
    - STANDARD: Default access level. Least permissions.
    - DEPARTMENT_MANAGER: Second highest access level.
    - ADMIN: Highest access level.

    Args:
        user_access_level (str): The user's access level.
        minimum_access_level (str): The minimum access level to receive access permission.

    Returns:
        bool: True if the user meets the minimum access level; otherwise, False.
    """
    user_access_level = user_access_level.upper()
    access_levels = {"STANDARD": 0, "DEPARTMENT_MANAGER": 1, "ADMIN": 2}

    # Return False if user or minimum access level are invalid options.
    if user_access_level not in access_levels.keys() or minimum_access_level not in access_levels.keys():
        return False
    
    user_access_value = access_levels.get(user_access_level)
    minimum_access_value = access_levels.get(minimum_access_level)
    
    print(user_access_value)
    print(minimum_access_value)
    return user_access_value >= minimum_access_value    

def generate_strong_password(length=8, max_attempts=1000) -> Union[str, None]:
    """Generates a strong password of length 8 that meets the password requirements shown
    below.
    - Minimum length is 8.
    - Maximum length is 25.
    - Has at least one number.
    - Has at least one lowercase letter.
    - Has at least one uppercase letter.
    - Has at least one special character (" !\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~").


    Args:
        length (int, optional): The length of the password to generate. Defaults to 8.
        max_attempts (int, optional): Maximum number of attempts to generate a password before quitting. Defaults to 1000.

    Returns:
        Union[str, None]: The generated password or None if max_attempts exausted.
    """
    special_characters = " !\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"

    # Create charset. Has all lowercase and uppercase English alphabet letters, as well as
    # numbers 0-9, and the special characters in the variable above.
    charset = special_characters + ascii_lowercase + ascii_uppercase + digits
    print(charset)
    attempts = 0
    gen_password = None
    while attempts < max_attempts:
        attempts += 1
        gen_password = ''.join(secrets.choice(charset) for i in range(20))
        print(sum((c in special_characters) for c in gen_password))
        if(
            sum(c.islower() for c in gen_password) >= 1 and
            sum(c.isupper() for c in gen_password) >= 1 and
            sum(c.isdigit() for c in gen_password) >= 1 and 
            sum((c in special_characters) for c in gen_password) >= 1
        ):
            break
    
    if attempts >= max_attempts:
        gen_password = None
    
    return gen_password
