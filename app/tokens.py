from flask import current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

def generate_token(email, purpose):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(email, salt=purpose)

def confirm_token(token, purpose, max_age):
    serializer =URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

    try:
        return serializer.loads(token, salt=purpose, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None