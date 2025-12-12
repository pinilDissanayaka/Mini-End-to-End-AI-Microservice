from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "AI Microservice"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8070
    
    
    llm_model_name: str = "gpt-3.5-turbo"
    llm_temperature: float = 0.7
    
    embedding_model_name: str = "text-embedding-ada-002"
    
    vector_store_path: str = "vector_store"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
        
        

settings = Settings()