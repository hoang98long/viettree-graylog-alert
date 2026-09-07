from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db() -> None:
    from app.database import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    if not settings.database_url.startswith("sqlite"):
        return
    required = {
        "graylog_message_id": "VARCHAR(255)", "source": "VARCHAR(255) NOT NULL DEFAULT ''",
        "device_name": "VARCHAR(255)", "device_ip": "VARCHAR(64)", "device_type": "VARCHAR(100)",
        "telegram_sent_at": "DATETIME", "received_at": "DATETIME", "detection_reason": "TEXT", "matched_pattern": "VARCHAR(255)",
    }
    existing = {column["name"] for column in inspect(engine).get_columns("security_events")}
    with engine.begin() as connection:
        for name, definition in required.items():
            if name not in existing:
                connection.execute(text(f"ALTER TABLE security_events ADD COLUMN {name} {definition}"))
        connection.execute(text("UPDATE security_events SET received_at = created_at WHERE received_at IS NULL"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
