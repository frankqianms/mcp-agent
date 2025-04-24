import { createReactAgent } from '@langchain/langgraph/prebuilt'
import { MultiServerMCPClient } from '@langchain/mcp-adapters'
import { agentModel } from './agentModel.js';
import { loadMcpServers } from './loadMcpServers.js';

/**
 * Initialize the MCP client and agent
 * @returns Object containing the MCP client and React agent
 */
export async function initializeMcpAgent(extraTools: any[] = []): Promise<{
  client: MultiServerMCPClient;
  reactAgent: any;
}> {
  try {
    const mcpServers = await loadMcpServers();
    const client = new MultiServerMCPClient({
      throwOnLoadError: true,
      prefixToolNameWithServerName: true,
      additionalToolNamePrefix: "mcp",
      mcpServers,
    });
    const tools = await client.getTools();
    if (extraTools.length > 0) {
      tools.push(...extraTools);
    }
    console.log(`Tools loaded\n`)
    for (const tool of tools) {
      console.log(`name: ${tool.name}\ndescription: ${tool.description}\n`);
    }

    // Create the agent with the tools and LLM model
    const reactAgent = createReactAgent({
      llm: agentModel,
      tools: tools,
    });

    console.log("Agent initialized successfully with tools from MCP servers and Azure AI Foundry Agent");

    return { client, reactAgent };
  } catch (e) {
    console.error("Failed to initialize MCP agent:", e);
    throw e;
  }
}
