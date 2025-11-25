import os
from typing import Any, Dict
from crm_core.base import CRMAdapter

class SalesforceAdapter(CRMAdapter):
    """
    Adapter for Salesforce CRM (Stub).
    """
    
    def initialize(self) -> None:
        # Load Salesforce specific env vars
        pass

    def get_connection_config(self) -> Dict[str, Any]:
        return {
            "transport": "streamable_http",
            "url": os.getenv("SALESFORCE_MCP_URL", "http://localhost:8001/mcp"),
        }

    def get_server_name(self) -> str:
        return "salesforce_crm"
