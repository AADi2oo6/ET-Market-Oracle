from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "ET Market Oracle API"
    VERSION: str = "1.0.0"
    
    # Cloud Database URLs
    DATABASE_URL: str
    REDIS_URL: str
    
    # AI & Vector DB Keys
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str = "et-market-oracle"
    FASTROUTER_API_KEY: str

    # Load from the .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()