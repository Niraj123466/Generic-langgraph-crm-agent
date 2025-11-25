"""
Entry point for the Zoho MCP LangGraph proof-of-concept.
"""

from __future__ import annotations

import asyncio

from agent_config import validate_config
from agent_core import run_conversation, setup_zoho_agent


async def main():
    validate_config()

    agent_app = await setup_zoho_agent()
    prompt = (
        "Create a new lead in Zoho CRM for Sarah Connor with email "
        "sarah.c@example.com and company T-800 Corp. "
        "Confirm once the lead is recorded."
    )
    await run_conversation(agent_app, prompt)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (ConnectionError, OSError, RuntimeError) as exc:
        print("Failed to reach the Zoho MCP server:", exc)


