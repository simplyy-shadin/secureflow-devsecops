from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.database import create_database_engine


def test_sqlite_engine_executes_query() -> None:
    engine = create_database_engine("sqlite+pysqlite:///:memory:")

    try:
        with Session(engine) as session:
            result = session.execute(text("SELECT 1")).scalar_one()

        assert result == 1
    finally:
        engine.dispose()
