from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ASA Config Monitor"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    graylog_url: str = "http://192.168.10.10:9000"
    graylog_username: str = ""
    graylog_password: str = ""
    graylog_verify_ssl: bool = False
    graylog_search_endpoint: str = "/api/search/universal/relative"
    graylog_search_query: str = "source:192.168.1.1"
    asa_ip: str = "192.168.1.1"
    poll_interval_seconds: int = 5
    initial_lookback_seconds: int = 60
    poll_overlap_seconds: int = 2
    database_url: str = "sqlite:///./data/asa_monitor.db"
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    enable_telegram: bool = True
    mock_graylog: bool = False
    cors_origins: str = "http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    return Settings()
