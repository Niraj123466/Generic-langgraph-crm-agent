import os
from typing import Any, Dict, Optional
from crm_core.base import CRMAdapter
from .token_manager import ZohoTokenManager

class ZohoAdapter(CRMAdapter):
    """
    Adapter for Zoho CRM.
    """
    
    def __init__(self):
        self.client_id = os.getenv("ZOHO_CLIENT_ID")
        self.client_secret = os.getenv("ZOHO_CLIENT_SECRET")
        self.redirect_uri = os.getenv("ZOHO_REDIRECT_URI", "http://localhost:8080/oauth/callback")
        self.scope = os.getenv("ZOHO_SCOPE", "ZohoCRM.modules.ALL")
        self.accounts_server = os.getenv("ZOHO_ACCOUNTS_SERVER", "https://accounts.zoho.com")
        self.mcp_url = os.getenv("ZOHO_MCP_URL")

    def initialize(self) -> None:
        """
        Validate configuration.
        """
        if not self.mcp_url:
            # Fallback or error. For now, we'll assume it's set or use the default from old config
            self.mcp_url = "https://demo-zoho-mcp-60058881996.zohomcp.in/mcp/message?key=1c08e37e64c174cc5998440b50364806"

    def _get_auth_headers(self) -> Optional[Dict[str, str]]:
        """
        Get authentication headers with a valid access token.
        """
        if not self.client_id or not self.client_secret:
            return None

        try:
            token_manager = ZohoTokenManager(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=self.scope,
                accounts_server=self.accounts_server,
            )
            access_token = token_manager.get_valid_access_token()
            return {"Authorization": f"Bearer {access_token}"}
        except RuntimeError as e:
            print(f"Warning: Could not get access token: {e}")
            print("Continuing without Bearer token authentication...")
            return None

    def get_connection_config(self) -> Dict[str, Any]:
        auth_headers = self._get_auth_headers()
        
        config = {
            "transport": "streamable_http",
            "url": self.mcp_url,
        }
        
        if auth_headers:
            config["headers"] = auth_headers
            
        return config

    def get_server_name(self) -> str:
        return "zoho_crm"
