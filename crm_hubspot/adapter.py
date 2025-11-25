import os
from typing import Any, Dict
from crm_core.base import CRMAdapter

class HubSpotAdapter(CRMAdapter):
    """
    Adapter for HubSpot CRM (Stub).
    """
    
    def initialize(self) -> None:
        # Load HubSpot specific env vars
        pass

    def get_connection_config(self) -> Dict[str, Any]:
        return {
            "transport": "sse",
            "url": os.getenv("HUBSPOT_MCP_URL", "http://localhost:8000/sse"),
        }

    def get_server_name(self) -> str:
        return "hubspot_crm"
