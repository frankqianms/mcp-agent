import { DynamicTool } from '@langchain/core/tools';

export function createAzureAgentTool(azureAgent: any) {
  return new DynamicTool({
    name: 'azure_repair_tool',
    description: 'Use this tool for repair-related or OpenAPI-based queries. It will call the Azure agent to handle the request.',
    func: async (input: string) => {
      return await azureAgent.runUserMessage(input);
    },
  });
}
