# Zoho MCP LangGraph Agent (POC)

This proof of concept wires a LangGraph ReAct agent to a Zoho Model Context Protocol (MCP) server so the agent can call Zoho CRM tools (create leads, search contacts, etc.) when appropriate.

## Prerequisites

- Python 3.11+
- Active Zoho MCP server deployment with Zoho CRM tools enabled
- Google Generative AI API key (Gemini 2.5 Flash)

## Environment Variables

Create a `.env` file in the project root or export the variables in your shell:

```
ZOHO_MCP_URL=<copy from Zoho MCP console>
GOOGLE_API_KEY=<your Gemeni API key>
```

- `ZOHO_MCP_URL`: in the Zoho MCP Console, open your server, go to **Connect → HTTP**, and copy the streaming URL.
- `GOOGLE_API_KEY`: generate from Google AI Studio and ensure the Gemini 2.5 Flash model is enabled for the project.

> The sample URL in `agent_config.py` is a placeholder. Replace it with your own endpoint.

## Installation

```bash
cd /Users/nirajvaijinathmore/Desktop/dev/langgraph-zoho-mcp/zoho_mcp_agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the POC

```bash
python main.py
```

The script:

1. Loads env vars through `agent_config.py`.
2. Connects to the Zoho MCP server via `MultiServerMCPClient`.
3. Discovers all Zoho CRM tools using `load_mcp_tools`.
4. Spins up a LangGraph ReAct agent backed by Gemini 2.5 Flash (via `ChatGoogleGenerativeAI`).
5. Sends an actionable Zoho CRM prompt and streams the reasoning + final answer.

Ensure your Zoho MCP server is running; otherwise, the script will exit with a connection error.


