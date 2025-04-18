import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

/**
 * Loads the MCP servers configuration from JSON file and processes paths
 * to ensure they are absolute
 * @returns The processed MCP servers configuration
 */
export async function loadMcpServers(): Promise<Record<string, any>> {
  try {
    // Load the MCP servers configuration from JSON
    const baseDir = path.dirname(fileURLToPath(import.meta.url));
    const configPath = path.join(baseDir, '..', 'mcpServers', 'mcpServersList.json');
    const configFile = fs.readFileSync(configPath, 'utf8');
    const configJson = configFile.replace(/^\s*\/\/.*$/gm, '');
    const serverConfigs = JSON.parse(configJson);
    
    // Process the server configurations to make paths absolute
    const mcpServers = {};
    for (const [serverName, config] of Object.entries(serverConfigs)) {
      mcpServers[serverName] = { ...(config as object) };
      
      // Make paths absolute if they are relative
      if (mcpServers[serverName].args) {
        mcpServers[serverName].args = mcpServers[serverName].args.map(arg => {
          // If the arg looks like a file path and doesn't have an absolute path
          if (typeof arg === 'string' && 
              (arg.endsWith('.js') || arg.endsWith('.py')) && 
              !path.isAbsolute(arg)) {
            // Note: going up two levels from utils/serverConfig to reach root, then into mcp_servers
            return path.join(path.dirname(path.dirname(baseDir)), 'src', 'mcpServers', arg);
          }
          return arg;
        });
      }
    }
    
    console.log("Loaded MCP server configurations:", JSON.stringify(mcpServers, null, 2));
    return mcpServers;
  } catch (e) {
    console.error("Failed to load MCP server configurations:", e);
    throw e;
  }
}
