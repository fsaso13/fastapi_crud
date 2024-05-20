from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_host:    str
    db_port:    str
    db_pwd:     str
    db_name:    str
    db_user:    str
    secret_key: str    
    algorithm:  str
    token_exp:  str

    class Config:
        env_file = ".env"

settings = Settings()