from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI, AzureChatOpenAI

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
async def create_agent(selected_tools=None):
    with open(f'{os.getcwd()}/mcp_servers/mcp_servers_list.json') as file:
        mcp_servers_list = json.loads(file.read())
    async with MultiServerMCPClient(mcp_servers_list) as client:
        all_tools = client.get_tools()
        # If selected_tools is provided, filter tools to only include selected ones
        if selected_tools and isinstance(selected_tools, list) and len(selected_tools) > 0:
            filtered_tools = [tool for tool in all_tools if tool.name in selected_tools]
            agent_tools = filtered_tools if filtered_tools else all_tools
        else:
            agent_tools = all_tools
            
        agent = create_react_agent(model, agent_tools)
        try:
            yield agent
        finally:
            # Any cleanup code can go here
            print(f"Agent session completed with {len(agent_tools)} tools")
            print(json.dumps([tool.name for tool in agent_tools]))
            
# Example of how to use this in the same module:
# async def main():
#     async with create_agent() as agent:
#         result = await agent.ainvoke({"messages": "hi"})
#         print(result)
