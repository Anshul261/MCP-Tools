# api/settings.py
from core.config import settings

# Export settings for use in the API
api_settings = settings.api
database_settings = settings.database
azure_openai_settings = settings.azure_openai
document_settings = settings.documents
external_api_settings = settings.external

# API-specific configurations
CORS_ORIGINS = api_settings.cors_origins
API_TITLE = api_settings.title
API_DESCRIPTION = api_settings.description
API_VERSION = api_settings.version
DEBUG_MODE = api_settings.debug
DOCS_ENABLED = api_settings.docs_enabled# api/settings.py
from core.config import settings

# Export settings for use in the API
api_settings = settings.api
database_settings = settings.database
azure_openai_settings = settings.azure_openai
document_settings = settings.documents
external_api_settings = settings.external

# API-specific configurations
CORS_ORIGINS = api_settings.cors_origins
API_TITLE = api_settings.title
API_DESCRIPTION = api_settings.description
API_VERSION = api_settings.version
DEBUG_MODE = api_settings.debug
DOCS_ENABLED = api_settings.docs_enabled