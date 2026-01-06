"""
Unified Tools Configuration for AgentOS Integration
Consolidates all tool definitions for ManageEngine Helpdesk system
"""

import os
import requests
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from agno.tools.toolkit import Toolkit

# Load environment variables
load_dotenv()

# ManageEngine API Configuration
MANAGEENGINE_BASE_URL = os.getenv("MANAGEENGINE_BASE_URL")
MANAGEENGINE_API_KEY = os.getenv("MANAGEENGINE_API_KEY")

class ManageEngineTools(Toolkit):
    """Unified toolkit for ManageEngine operations"""
    
    def __init__(self):
        super().__init__(
            name="manage_engine_tools",
        )
        self.base_url = MANAGEENGINE_BASE_URL
        self.api_key = MANAGEENGINE_API_KEY
        self.headers = {
            "technician_key": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded"
        }
    
    def _make_api_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make API request to ManageEngine"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, data=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}
    
    # User Information Tools
    def get_users(self) -> Dict[str, Any]:
        """Get all users from ManageEngine"""
        return self._make_api_request("/users")
    
    def get_specific_user(self, user_id: str) -> Dict[str, Any]:
        """Get specific user details"""
        return self._make_api_request(f"/users/{user_id}")
    
    def get_user_requests_by_name(self, user_name: str) -> Dict[str, Any]:
        """Get all requests for a specific user by name"""
        return self._make_api_request(f"/requests?search_text={user_name}")
    
    # Creator Tools
    def get_ticket_fields(self) -> Dict[str, Any]:
        """Get all available ticket fields"""
        return self._make_api_request("/requests/fields")
    
    def get_groups(self) -> Dict[str, Any]:
        """Get all available groups"""
        return self._make_api_request("/requests/groups")
    
    def get_sites(self) -> Dict[str, Any]:
        """Get all available sites"""
        return self._make_api_request("/requests/sites")
    
    def get_impacts(self) -> Dict[str, Any]:
        """Get all impact levels"""
        return self._make_api_request("/requests/impacts")
    
    def get_urgencies(self) -> Dict[str, Any]:
        """Get all urgency levels"""
        return self._make_api_request("/requests/urgencies")
    
    def get_request_types(self) -> Dict[str, Any]:
        """Get all request types"""
        return self._make_api_request("/requests/types")
    
    def get_accounts(self) -> Dict[str, Any]:
        """Get all accounts"""
        return self._make_api_request("/requests/accounts")
    
    def get_statuses(self) -> Dict[str, Any]:
        """Get all statuses"""
        return self._make_api_request("/requests/statuses")
    
    def get_categories(self) -> Dict[str, Any]:
        """Get all categories"""
        return self._make_api_request("/requests/categories")
    
    def get_subcategories(self, category_id: str) -> Dict[str, Any]:
        """Get subcategories for a category"""
        return self._make_api_request(f"/requests/categories/{category_id}/subcategories")
    
    def get_items(self, subcategory_id: str) -> Dict[str, Any]:
        """Get items for a subcategory"""
        return self._make_api_request(f"/requests/subcategories/{subcategory_id}/items")
    
    def build_ticket_payload(self, **kwargs) -> Dict[str, Any]:
        """Build ticket payload from provided data"""
        return {
            "subject": kwargs.get("subject", ""),
            "description": kwargs.get("description", ""),
            "category": kwargs.get("category", ""),
            "subcategory": kwargs.get("subcategory", ""),
            "item": kwargs.get("item", ""),
            "impact": kwargs.get("impact", ""),
            "urgency": kwargs.get("urgency", ""),
            "group": kwargs.get("group", ""),
            "request_type": kwargs.get("request_type", ""),
            "account": kwargs.get("account", ""),
            "site": kwargs.get("site", ""),
        }
    
    def validate_ticket_data(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate ticket data before creation"""
        required_fields = ["subject", "description", "category", "subcategory", "item"]
        missing_fields = [field for field in required_fields if not ticket_data.get(field)]
        
        if missing_fields:
            return {"valid": False, "missing_fields": missing_fields}
        
        return {"valid": True, "missing_fields": []}
    
    def create_ticket(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new ticket"""
        validation_result = self.validate_ticket_data(input_data)
        if not validation_result["valid"]:
            return {"error": f"Missing required fields: {validation_result['missing_fields']}"}
        
        return self._make_api_request("/requests", method="POST", data=input_data)
    
    # Updater Tools
    def update_request(self, ticket_id: str, additional_description: str, user_id: str) -> Dict[str, Any]:
        """Update existing ticket with additional description"""
        update_data = {
            "description": additional_description,
            "request_id": ticket_id
        }
        return self._make_api_request(f"/requests/{ticket_id}", method="POST", data=update_data)
    
    # Viewer Tools
    def get_specific_request(self, ticket_id: str, user_id: str) -> Dict[str, Any]:
        """Get specific ticket details"""
        return self._make_api_request(f"/requests/{ticket_id}")
    
    def get_request_resolution(self, ticket_id: str, user_id: str) -> Dict[str, Any]:
        """Get resolution details for a closed ticket"""
        return self._make_api_request(f"/requests/{ticket_id}/resolutions")

# Initialize unified tools instance
manage_engine_tools = ManageEngineTools()

# Export individual tool functions for backward compatibility
def get_users():
    return manage_engine_tools.get_users()

def get_specific_user(user_id: str):
    return manage_engine_tools.get_specific_user(user_id)

def get_user_requests_by_name(user_name: str):
    return manage_engine_tools.get_user_requests_by_name(user_name)

def get_ticket_fields():
    return manage_engine_tools.get_ticket_fields()

def get_groups():
    return manage_engine_tools.get_groups()

def get_sites():
    return manage_engine_tools.get_sites()

def get_impacts():
    return manage_engine_tools.get_impacts()

def get_urgencies():
    return manage_engine_tools.get_urgencies()

def get_request_types():
    return manage_engine_tools.get_request_types()

def get_accounts():
    return manage_engine_tools.get_accounts()

def get_statuses():
    return manage_engine_tools.get_statuses()

def get_categories():
    return manage_engine_tools.get_categories()

def get_subcategories(category_id: str):
    return manage_engine_tools.get_subcategories(category_id)

def get_items(subcategory_id: str):
    return manage_engine_tools.get_items(subcategory_id)

def build_ticket_payload(**kwargs):
    return manage_engine_tools.build_ticket_payload(**kwargs)

def validate_ticket_data(ticket_data: Dict[str, Any]):
    return manage_engine_tools.validate_ticket_data(ticket_data)

def create_ticket(input_data: Dict[str, Any]):
    return manage_engine_tools.create_ticket(input_data)

def update_request(ticket_id: str, additional_description: str, user_id: str):
    return manage_engine_tools.update_request(ticket_id, additional_description, user_id)

def get_specific_request(ticket_id: str, user_id: str):
    return manage_engine_tools.get_specific_request(ticket_id, user_id)

def get_request_resolution(ticket_id: str, user_id: str):
    return manage_engine_tools.get_request_resolution(ticket_id, user_id)