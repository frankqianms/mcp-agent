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
async def create_agent():
    with open(f'{os.getcwd()}/mcp_servers/mcp_servers_list.json') as file:
        mcp_servers_list = json.loads(file.read())
    async with MultiServerMCPClient(mcp_servers_list) as client:
        all_tools = client.get_tools()
        agent = create_react_agent(model, all_tools)
        try:
            yield agent
        finally:
            # Any cleanup code can go here
            print(f"Agent session completed with {len(all_tools)} tools")
            print(json.dumps(all_tools))
            
# Example of how to use this in the same module:
# async def main():
#     async with create_agent() as agent:
#         result = await agent.ainvoke({"messages": "hi"})
#         print(result)
