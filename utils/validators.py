import re

EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

def validate_email(email):
    """Checks if the email string is valid."""
    if not email:
        return False
    return bool(re.match(EMAIL_REGEX, email))

def validate_role(role):
    """Ensures role is either viewer or editor."""
    return role.lower() in ["viewer", "editor"]
