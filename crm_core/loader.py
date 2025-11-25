import os
import importlib
from typing import Optional
from .base import CRMAdapter

def load_crm_adapter() -> CRMAdapter:
    """
    Loads the active CRM adapter based on the ACTIVE_CRM environment variable.
    Defaults to 'zoho' if not specified.
    """
    active_crm = os.getenv("ACTIVE_CRM", "zoho").lower()
    
    # Map 'zoho' -> 'crm_zoho', 'hubspot' -> 'crm_hubspot'
    module_name = f"crm_{active_crm}.adapter"
    class_name = f"{active_crm.capitalize()}Adapter"
    
    # Special casing for names if needed, or enforce convention
    if active_crm == "zoho":
        class_name = "ZohoAdapter"
    elif active_crm == "hubspot":
        class_name = "HubSpotAdapter"
    elif active_crm == "salesforce":
        class_name = "SalesforceAdapter"

    try:
        module = importlib.import_module(module_name)
        adapter_class = getattr(module, class_name)
        adapter = adapter_class()
        adapter.initialize()
        return adapter
    except ImportError as e:
        raise RuntimeError(f"Could not load CRM adapter for '{active_crm}'. Ensure 'crm_{active_crm}' directory exists and contains 'adapter.py'. Error: {e}")
    except AttributeError as e:
        raise RuntimeError(f"Module '{module_name}' does not contain class '{class_name}'. Error: {e}")
