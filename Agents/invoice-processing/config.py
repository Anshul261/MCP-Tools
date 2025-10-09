"""
Configuration settings for invoice processing system
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""

    # Azure OpenAI settings
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-06-01")

    # Database settings
    DUCKDB_PATH = os.getenv("DUCKDB_PATH", "./invoices.db")

    # Human review settings
    HUMAN_REVIEW_ENABLED = os.getenv("HUMAN_REVIEW_ENABLED", "True").lower() == "true"
    AUTO_APPROVE_CONFIDENCE = float(os.getenv("AUTO_APPROVE_CONFIDENCE", "0.90"))

    # Processing settings
    DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "USD")

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = [
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_DEPLOYMENT_NAME",
        ]
        missing = [key for key in required if not getattr(cls, key)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    @classmethod
    def display(cls):
        """Display current configuration (hiding sensitive data)"""
        print("\n=== Configuration ===")
        print(f"Azure OpenAI Endpoint: {cls.AZURE_OPENAI_ENDPOINT}")
        print(f"Azure OpenAI Deployment: {cls.AZURE_OPENAI_DEPLOYMENT_NAME}")
        print(f"DuckDB Path: {cls.DUCKDB_PATH}")
        print(f"Human Review Enabled: {cls.HUMAN_REVIEW_ENABLED}")
        print(f"Auto-Approve Confidence Threshold: {cls.AUTO_APPROVE_CONFIDENCE}")
        print(f"Default Currency: {cls.DEFAULT_CURRENCY}")
        print("=" * 30 + "\n")


# Validate configuration on import
Config.validate()
