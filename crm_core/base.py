from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class CRMAdapter(ABC):
    """
    Abstract base class for CRM adapters.
    Each CRM implementation (Zoho, HubSpot, Salesforce) must inherit from this class.
    """

    @abstractmethod
    def initialize(self) -> None:
        """
        Perform any necessary initialization (e.g., loading env vars, setting up auth).
        """
        pass

    @abstractmethod
    def get_connection_config(self) -> Dict[str, Any]:
        """
        Return the configuration dictionary required by MultiServerMCPClient.
        This typically includes 'url', 'transport', and 'headers'.
        """
        pass

    @abstractmethod
    def get_server_name(self) -> str:
        """
        Return the unique name for this CRM server (e.g., 'zoho_crm', 'hubspot_crm').
        """
        pass
