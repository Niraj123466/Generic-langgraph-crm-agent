import os
import httpx
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("HubSpot CRM")

HUBSPOT_ACCESS_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")
BASE_URL = "https://api.hubapi.com"

@mcp.tool()
async def search_contacts(query: str) -> str:
    """
    Search for contacts in HubSpot by email, name, or phone number.
    """
    if not HUBSPOT_ACCESS_TOKEN:
        return "Error: HUBSPOT_ACCESS_TOKEN not set."

    headers = {
        "Authorization": f"Bearer {HUBSPOT_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # HubSpot Search API
    url = f"{BASE_URL}/crm/v3/objects/contacts/search"
    payload = {
        "filterGroups": [
            {
                "filters": [
                    {
                        "propertyName": "email",
                        "operator": "EQ",
                        "value": query
                    }
                ]
            },
             {
                "filters": [
                    {
                        "propertyName": "firstname",
                        "operator": "EQ",
                        "value": query
                    }
                ]
            }
        ],
        "properties": ["email", "firstname", "lastname", "phone"],
        "limit": 5
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            results = data.get("results", [])
            if not results:
                return "No contacts found."
            
            formatted = []
            for contact in results:
                props = contact.get("properties", {})
                formatted.append(
                    f"ID: {contact['id']}, Name: {props.get('firstname')} {props.get('lastname')}, "
                    f"Email: {props.get('email')}, Phone: {props.get('phone')}"
                )
            return "\n".join(formatted)
            
        except httpx.HTTPStatusError as e:
            return f"HubSpot API Error: {e.response.text}"
        except Exception as e:
            return f"Error: {str(e)}"

@mcp.tool()
async def create_contact(email: str, firstname: str, lastname: str, phone: str = None) -> str:
    """
    Create a new contact in HubSpot.
    """
    if not HUBSPOT_ACCESS_TOKEN:
        return "Error: HUBSPOT_ACCESS_TOKEN not set."

    headers = {
        "Authorization": f"Bearer {HUBSPOT_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}/crm/v3/objects/contacts"
    properties = {
        "email": email,
        "firstname": firstname,
        "lastname": lastname
    }
    if phone:
        properties["phone"] = phone

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json={"properties": properties})
            response.raise_for_status()
            data = response.json()
            props = data.get("properties", {})
            return f"Successfully created contact: ID {data['id']}, {props.get('firstname')} {props.get('lastname')}"
            
        except httpx.HTTPStatusError as e:
            return f"HubSpot API Error: {e.response.text}"
        except Exception as e:
            return f"Error: {str(e)}"

if __name__ == "__main__":
    # Run the server
    mcp.run()
