"""
LangGraph agent core for the Zoho MCP proof-of-concept.
"""

from __future__ import annotations

from typing import Any, Dict

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

from agent_config import GOOGLE_API_KEY, ZOHO_MCP_URL


async def setup_zoho_agent():
    """
    Build and return a LangGraph agent wired to Zoho MCP tools.

    The MCP client is configured for a single HTTP server that exposes Zoho CRM
    helpers (create lead, search contacts, etc.). `load_mcp_tools` introspects
    that endpoint so LangGraph can call whichever Zoho tool is relevant at
    runtime.
    """
    server_name = "zoho_crm"
    client = MultiServerMCPClient(
        connections={
            server_name: {
                "transport": "streamable_http",
                "url": ZOHO_MCP_URL,
            }
        }
    )

    # Open a short-lived session to enumerate tools and capture schemas.
    async with client.session(server_name) as session:
        tools = await load_mcp_tools(
            session,
            connection=client.connections[server_name],
            server_name=server_name,
        )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=GOOGLE_API_KEY,
        temperature=0,
    )

    agent_app = create_react_agent(llm, tools)
    return agent_app


async def run_conversation(agent_app, prompt: str) -> Dict[str, Any]:
    """
    Stream the agent's reasoning trace and return the final response payload.
    """
    print(">>> Prompt:", prompt)
    print("\n--- Agent Thoughts ---")

    inputs = {"messages": [("user", prompt)]}
    final_response: Dict[str, Any] | None = None

    async for event in agent_app.astream_events(inputs, version="v1"):
        event_type = event["event"]
        data = event.get("data", {})

        if event_type == "on_tool_start":
            print(f"[tool start] {event.get('name')} -> {data.get('input')}")
        elif event_type == "on_tool_end":
            print(f"[tool result] {event.get('name')} -> {data.get('output')}")
        elif event_type == "on_chat_model_stream":
            chunk = data.get("chunk")
            if chunk:
                text = "".join(
                    part.text for part in chunk.content if hasattr(part, "text")
                )
                if text:
                    print(text, end="", flush=True)
        elif event_type == "on_chain_end":
            final_response = data.get("output")

    print("\n--- Conversation Complete ---")
    if final_response:
        messages = final_response.get("messages") or []
        if messages:
            print(messages[-1].content)
        else:
            print(final_response)
    else:
        print("No final response received.")

    return final_response or {}

