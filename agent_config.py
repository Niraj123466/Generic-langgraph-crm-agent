"""
Configuration loader for the Zoho MCP LangGraph proof-of-concept.
"""

from __future__ import annotations

import os
from dotenv import load_dotenv

# Load `.env` values as early as possible so every module sees them.
load_dotenv()

# Zoho MCP endpoints can require extra authentication (Bearer headers,
# signed tokens, etc.). For this POC we assume the URL is reachable as-is
# or that Zoho handles auth internally once the URL is provided.
ZOHO_MCP_URL: str = os.getenv(
    "ZOHO_MCP_URL",
    "https://demo-zoho-mcp-60058881996.zohomcp.in/mcp/message?key=1c08e37e64c174cc5998440b50364806",
)

# Google Generative AI key used by `langchain-google-genai`.
GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY")


def validate_config() -> None:
    """
    Basic validation to make common misconfigurations fail fast.
    """
    missing = []
    if not ZOHO_MCP_URL:
        missing.append("ZOHO_MCP_URL")
    if not GOOGLE_API_KEY:
        missing.append("GOOGLE_API_KEY")

    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(
            f"Missing required environment variables: {joined}. "
            "Ensure they are set in your shell or .env file."
        )

