import os

from pydantic import (BaseSettings,
                      Field)


class Settings(BaseSettings):
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mongo_host: str = Field(default='localhost')
    mongo_port: int = Field(default='27017')
    mongo_db: str = Field(default='voice_helper')
    mongo_collection_commands = 'commands'


settings = Settings()