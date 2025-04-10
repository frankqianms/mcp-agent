from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from langchain_openai import ChatOpenAI, AzureChatOpenAI
model = AzureChatOpenAI(
    api_key="Aoi1Gep6NOE97Tw6nMAiWECjUg7f8osbZKaXHAhePAzdHMxgOYkJJQQJ99BCACYeBjFXJ3w3AAABACOGj8P9",
    azure_endpoint="https://openai-genaigateway-franktest.openai.azure.com/",
    model="gpt-4o",
    api_version="2025-01-01-preview"
)

import asyncio

# async def main():

client = MultiServerMCPClient(
    {
        "math": {
            "command": "python",
            # Make sure to update to the full absolute path to your math_server.py file
            "args": ["C:\\Users\\frankqian\\TeamsApps\\mcp-agent\\src\\mcp_servers\\math_server.py"],
            "transport": "stdio",
        },
        # "weather": {
        #     # make sure you start your weather server on port 8000
        #     "url": "http://localhost:8000/sse",
        #     "transport": "sse",
        # }
    }
)

all_tools = client.get_tools()
agent = create_react_agent(model, client.get_tools())