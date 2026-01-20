"""Test ManageEngine API endpoints: find correct user lookup endpoint."""
import os
import json
import requests
import urllib3
from dotenv import load_dotenv

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = os.getenv("MANAGEENGINE_API_BASE")
API_KEY = os.getenv("MANAGEENGINE_API_KEY")
HEADERS = {"authtoken": API_KEY, "Content-Type": "application/x-www-form-urlencoded"}

ENDPOINTS_TO_TRY = ["/requesters", "/users", "/requester", "/user", "/technicians"]

def test_endpoint(endpoint, name="administrator"):
    url = f"{BASE_URL}{endpoint}"
    input_data = {"list_info": {"search_fields": {"name": name}, "row_count": 5}}
    params = {"input_data": json.dumps(input_data)}
    try:
        resp = requests.get(url, headers=HEADERS, params=params, verify=False)
        data = resp.json()
        print(f"\n[{endpoint}] Status: {resp.status_code}")
        print(f"  Response: {json.dumps(data, indent=2)[:500]}")
    except Exception as e:
        print(f"\n[{endpoint}] Error: {e}")
    return resp

def test_create_ticket(requester_name, requester_id):
    url = f"{BASE_URL}/requests"
    input_data = {
        "request": {
            "subject": "Test Ticket - Wifi Issues",
            "description": "Wifi not working intermittently",
            "requester": {"name": requester_name, "id": requester_id},
            "request_type": {"name": "Incident"},
            "impact": {"name": "High"},
            "urgency": {"name": "High"},
            "category": {"name": "Network & Security"},
            "subcategory": {"name": "General"},
            "item": {"name": "Others"},
            "group": {"name": "Network Administration"},
        }
    }
    print(f"\n[CREATE TICKET] Payload: {json.dumps(input_data, indent=2)}")
    data = {"input_data": json.dumps(input_data)}
    resp = requests.post(url, headers=HEADERS, data=data, verify=False)
    print(f"[CREATE TICKET] Status: {resp.status_code}")
    print(f"[CREATE TICKET] Response: {json.dumps(resp.json(), indent=2)}")
    return resp.json()

def test_user_lookup(name):
    url = f"{BASE_URL}/users"
    input_data = {"list_info": {"search_fields": {"name": name}, "row_count": 5}}
    params = {"input_data": json.dumps(input_data)}
    resp = requests.get(url, headers=HEADERS, params=params, verify=False)
    data = resp.json()
    users = data.get("users", [])
    if users:
        print(f"\n[LOOKUP: {name}] Found {len(users)} user(s):")
        for u in users:
            print(f"  ID: {u.get('id')}, Name: {u.get('name')}, Email: {u.get('email_id')}")
        return users[0].get("id"), users[0].get("name")
    print(f"\n[LOOKUP: {name}] No users found")
    return None, None

def get_list(endpoint):
    url = f"{BASE_URL}/{endpoint}"
    resp = requests.get(url, headers=HEADERS, verify=False)
    data = resp.json()
    print(f"\n[{endpoint}] Status: {resp.status_code}")
    items = data.get(endpoint, data.get("list", []))
    if isinstance(items, list):
        for item in items[:10]:
            print(f"  - {item.get('name', item)}")
    else:
        print(f"  Response: {str(data)[:500]}")

def get_categories_with_ids():
    url = f"{BASE_URL}/categories"
    resp = requests.get(url, headers=HEADERS, verify=False)
    data = resp.json()
    categories = data.get("categories", [])
    print("\n[CATEGORIES]")
    for c in categories:
        print(f"  ID: {c.get('id')}, Name: {c.get('name')}")
    return categories

def get_subcategories(category_id):
    url = f"{BASE_URL}/categories/{category_id}/subcategories"
    resp = requests.get(url, headers=HEADERS, verify=False)
    data = resp.json()
    subcats = data.get("subcategories", [])
    print(f"\n[SUBCATEGORIES for category {category_id}]")
    for s in subcats:
        print(f"  ID: {s.get('id')}, Name: {s.get('name')}")
    return subcats

def test_create_ticket_v2():
    url = f"{BASE_URL}/requests"
    input_data = {
        "request": {
            "subject": "Test Ticket - Wifi Issues",
            "description": "Wifi not working intermittently",
            "requester": {"name": "Howard Stern", "id": "9"},
            "request_type": {"name": "Incident"},
            "impact": {"name": "High"},
            "urgency": {"name": "High"},
            "category": {"name": "Network & Security"},
            "subcategory": {"name": "Wireless/AP"},
            "item": {"name": "Frequent WIFI disconnection"},
            "group": {"name": "Network Administration"},
        }
    }
    print(f"\n[CREATE TICKET] Payload:")
    print(json.dumps(input_data, indent=2))
    data = {"input_data": json.dumps(input_data)}
    resp = requests.post(url, headers=HEADERS, data=data, verify=False)
    print(f"Status: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2)}")

def get_items_for_subcategory(subcategory_id):
    url = f"{BASE_URL}/subcategories/{subcategory_id}/items"
    resp = requests.get(url, headers=HEADERS, verify=False)
    data = resp.json()
    print(f"\n[ITEMS for subcategory {subcategory_id}] Status: {resp.status_code}")
    items = data.get("items", [])
    for i in items:
        print(f"  ID: {i.get('id')}, Name: {i.get('name')}")
    if not items:
        print(f"  Response: {data}")
    return items

if __name__ == "__main__":
    print(f"BASE_URL: {BASE_URL}")
    test_create_ticket_v2()
