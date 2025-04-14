from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from botbuilder.core import TurnContext

from contextlib import asynccontextmanager
import json, os
from config import Config
import asyncio

model = AzureChatOpenAI(
    api_key=Config.AZURE_OPENAI_API_KEY,
    azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
    model=Config.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME,
    api_version="2025-01-01-preview"
)

@asynccontextmanager
async def create_agent(mcp_servers_file_path, turn_context: TurnContext):
    with open(mcp_servers_file_path) as file:
        mcp_servers_list = json.loads(file.read())
    async with MultiServerMCPClient(mcp_servers_list) as client:
        all_tools = client.get_tools()
        agent = create_react_agent(model, all_tools)
        tool_names = [tool.name+'.'+tool.description for tool in all_tools]
        await turn_context.send_activity(f"Agent successfully initialized with tools: {tool_names}")
        try:
            yield agent
        finally:
            # Any cleanup code can go here
            print(f"Agent session completed with {len(all_tools)} tools")
            print(json.dumps(all_tools))
