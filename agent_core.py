from __future__ import annotations

from typing import Any, Dict

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from agent_config import GOOGLE_API_KEY


def create_agent(tools: list) -> Any:
    """
    Create the LangGraph ReAct agent with the given tools.
    """
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


async def refine_prompt(user_input: str) -> str:
    """
    Uses the LLM to convert raw user input into a clear, actionable prompt for the ReAct agent.
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=GOOGLE_API_KEY,
        temperature=0,
    )
    
    system_prompt = (
        "You are an expert at translating user requests into clear, actionable instructions "
        "for an AI agent that manages Zoho CRM. The agent has tools to search, create, and update "
        "leads, contacts, and deals.\n\n"
        "Convert the user's input into a precise, step-by-step prompt for the agent. "
        "If the user input is already clear, just repeat it. "
        "Do not add any preamble or explanation, just return the refined prompt.\n\n"
        f"User Input: {user_input}"
    )
    
    response = await llm.ainvoke(system_prompt)
    return response.content
