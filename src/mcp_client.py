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
async def create_agent(selected_tools=None, mcp_servers_list_path=None):
    with open(mcp_servers_list_path) as file:
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
            
# Function to get detailed information about all available tools
async def get_tool_details(mcp_servers_list_path=None):
    """
    Get detailed information about all available tools from MCP servers
    Returns a dictionary with server names as keys and lists of tool details as values
    """
    try:
        # Use provided path or fall back to default        servers_list_path = mcp_servers_list_path or f'{os.getcwd()}/mcp_servers/mcp_servers_list.json'
        with open(mcp_servers_list_path) as file:
            mcp_servers_list = json.loads(file.read())
        
        # Create a client to get the tools from each server
        async with MultiServerMCPClient(mcp_servers_list) as client:
            all_tools = client.get_tools()
            print(client.server_name_to_tools)
            
            # Directly use server_name_to_tools which already organizes tools by server
            tools_by_server = {}
            
            # Process each server and its tools
            for server_name, server_tools in client.server_name_to_tools.items():
                tools_by_server[server_name] = []
                
                # Process each tool in this server
                for tool in server_tools:
                    # Create the full name with server prefix
                    full_name = f"{server_name}.{tool.name}"
                    
                    tools_by_server[server_name].append({
                        "name": tool.name,
                        "full_name": full_name,
                        "description": tool.description
                    })
            
            return tools_by_server, all_tools
                
    except Exception as e:
        print(f"Error getting available tools: {e}")
        return {}, []
