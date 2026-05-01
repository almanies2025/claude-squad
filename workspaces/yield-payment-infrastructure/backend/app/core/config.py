from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    cors_origins: str = "http://localhost:3000"

    def get_cors_origins(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    model_config = {"env_prefix": "FLOATS_", "extra": "ignore"}


settings = Settings()
