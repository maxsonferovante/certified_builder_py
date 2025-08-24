import logging
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

class Config(BaseSettings):
    REGION: str
    BUCKET_NAME: str    
    QUEUE_URL: str


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"        


config = Config()


