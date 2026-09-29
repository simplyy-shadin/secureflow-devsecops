import os
import secrets

os.environ.setdefault("JWT_SECRET_KEY", secrets.token_hex(32))
