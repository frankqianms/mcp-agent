import { ActivityTypes, ApplicationBuilder, MessageFactory } from '@microsoft/agents-hosting'
import { HumanMessage } from '@langchain/core/messages'
import { sysMessage, initializeMcpAgent } from './utils/index.js'
import { initializeAzureAgent } from './utils/initializeAzureAgent.js'
import { createAzureAgentTool } from './utils/azureAgentTool.js'

export const mcpAgent = new ApplicationBuilder().build()

let mcpClient;
let reactAgent;
let azureAgent;

try {
  azureAgent = await initializeAzureAgent();
  const azureTool = createAzureAgentTool(azureAgent);
  const initResult = await initializeMcpAgent([azureTool]);
  mcpClient = initResult.client;
  reactAgent = initResult.reactAgent;

  mcpAgent.activity(ActivityTypes.Message, async (context, state) => {
    try {
      const userText = context.activity.text!;
      const llmResponse = await reactAgent.invoke({
        messages: [sysMessage, new HumanMessage(userText)]
      }, {
        configurable: { thread_id: context.activity.conversation!.id }
      });
      const llmResponseContent = JSON.parse(llmResponse.messages[llmResponse.messages.length - 1].content as string);
      if (llmResponseContent.contentType === 'Text') {
        await context.sendActivity(llmResponseContent.content);
      } else if (llmResponseContent.contentType === 'AdaptiveCard') {
        const response = MessageFactory.attachment({
          contentType: 'application/vnd.microsoft.card.adaptive',
          content: llmResponseContent.content
        });
        await context.sendActivity(response);
      }
    } catch (error) {
      console.error("Error in activity handler:", error);
      await context.sendActivity("I'm sorry, I encountered an error processing your request.");
    }
  });
} catch (e) {
  console.error("Error during initialization:", e);
}
