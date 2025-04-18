import { createReactAgent } from '@langchain/langgraph/prebuilt'
import { MultiServerMCPClient } from '@langchain/mcp-adapters'
import { agentModel } from './agentModel.js';
import { loadMcpServers } from './loadMcpServers.js';

/**
 * Initialize the MCP client and agent
 * @returns Object containing the MCP client and React agent
 */
export async function initializeMcpAgent(): Promise<{
  client: MultiServerMCPClient;
  reactAgent: any;
}> {  
  try {
    // Load the MCP servers configuration from the separate module
    const mcpServers = await loadMcpServers();
    
    // Create client and connect to server
    const client = new MultiServerMCPClient({
      throwOnLoadError: true,
      prefixToolNameWithServerName: true,
      additionalToolNamePrefix: "mcp",
      // Server configuration loaded from JSON
      mcpServers,
    });  
    
    // Get available tools from the MCP client
    const tools = await client.getTools();
    console.log(`Tools loaded\n`)
    for (const tool of tools) {
      console.log(`name: ${tool.name}\ndescription: ${tool.description}\n`);
    }

    // Create the agent with the tools and LLM model
    const reactAgent = createReactAgent({
      llm: agentModel,
      tools: tools,
    });

    console.log("MCP agent initialized successfully with tools");

    return { client, reactAgent };
  } catch (e) {
    console.error("Failed to initialize MCP agent:", e);
    throw e;
  }
}
