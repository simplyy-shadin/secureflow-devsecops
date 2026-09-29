from sqlalchemy import inspect

from app.db.models import User


def test_user_model_does_not_define_plaintext_password_column() -> None:
    columns = {column.name for column in inspect(User).columns}

    assert {"id", "email", "password_hash", "created_at"} <= columns
    assert "password" not in columns
