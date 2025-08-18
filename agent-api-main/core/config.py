import os
from pathlib import Path
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    
    user: str = Field(alias="DB_USER")
    password: str = Field(alias="DB_PASSWORD")
    host: str = Field(alias="DB_HOST")
    port: int = Field(default=5432, alias="DB_PORT")
    name: str = Field(alias="DB_NAME")
    url: Optional[str] = Field(default=None, alias="DB_URL")
    
    @field_validator("url", mode="before")
    @classmethod
    def build_db_url(cls, v, info):
        if v:
            return v
        
        values = info.data
        return f"postgresql://{values.get('user')}:{values.get('password')}@{values.get('host')}:{values.get('port')}/{values.get('name')}"
    
    class Config:
        env_prefix = "DB_"


class AzureOpenAISettings(BaseSettings):
    """Azure OpenAI configuration settings"""
    
    api_key: str = Field(alias="AZURE_OPENAI_API_KEY")
    endpoint: str = Field(alias="AZURE_OPENAI_ENDPOINT")
    deployment_name: str = Field(alias="AZURE_OPENAI_DEPLOYMENT_NAME")
    api_version: str = Field(default="2024-02-15-preview", alias="OPENAI_API_VERSION")
    
    class Config:
        env_prefix = "AZURE_OPENAI_"


class HuggingFaceSettings(BaseSettings):
    """HuggingFace configuration settings"""
    
    token: str = Field(alias="HUGGINGFACE_HUB_TOKEN")
    model_id: str = Field(default="BAAI/bge-small-en-v1.5")
    dimensions: int = Field(default=384)
    
    class Config:
        env_prefix = "HUGGINGFACE_"


class DocumentSettings(BaseSettings):
    """Document processing configuration settings"""
    
    source_dir: Path = Field(default=Path("documents"), alias="DOCUMENTS_DIR")
    converted_dir: Path = Field(default=Path("converted_docs"), alias="CONVERTED_DOCS_DIR")
    vector_table: str = Field(default="rag_documents", alias="PGVECTOR_TABLE")
    max_file_size: int = Field(default=50 * 1024 * 1024)  # 50MB
    allowed_extensions: list = Field(default=[".pdf", ".docx", ".pptx", ".txt"])
    
    @field_validator("source_dir", "converted_dir", mode="before")
    @classmethod
    def ensure_path(cls, v):
        return Path(v) if not isinstance(v, Path) else v
    
    class Config:
        env_prefix = "DOC_"


class APISettings(BaseSettings):
    """API configuration settings"""
    
    title: str = Field(default="Custom Agent API")
    description: str = Field(default="Document Search, Web Search, and Reasoning Team API")
    version: str = Field(default="1.0.0")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    debug: bool = Field(default=False)
    docs_enabled: bool = Field(default=True)
    cors_origins: list = Field(default=["*"])
    
    class Config:
        env_prefix = "API_"


class ExternalAPISettings(BaseSettings):
    """External API configuration settings"""
    
    brave_api_key: Optional[str] = Field(default=None, alias="BRAVE_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    
    class Config:
        env_prefix = "EXTERNAL_"


class Settings:
    """Main settings container"""
    
    def __init__(self):
        self.database = DatabaseSettings()
        self.azure_openai = AzureOpenAISettings()
        self.huggingface = HuggingFaceSettings()
        self.documents = DocumentSettings()
        self.api = APISettings()
        self.external = ExternalAPISettings()
        
        # Ensure document directories exist
        self.documents.source_dir.mkdir(parents=True, exist_ok=True)
        self.documents.converted_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_required_settings(self) -> list:
        """Validate that all required settings are present"""
        missing = []
        
        # Check database settings
        if not all([self.database.user, self.database.password, self.database.host, self.database.name]):
            missing.append("Database configuration incomplete")
        
        # Check Azure OpenAI settings
        if not all([self.azure_openai.api_key, self.azure_openai.endpoint, self.azure_openai.deployment_name]):
            missing.append("Azure OpenAI configuration incomplete")
        
        # Check HuggingFace settings
        if not self.huggingface.token:
            missing.append("HuggingFace token missing")
        
        return missing


# Global settings instance
settings = Settings()
