from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings"""

    PROJECT_NAME: str = "Faster APP"
    VERSION: str = "0.0.7"
    DEBUG: bool = True
