// filepath: c:\Users\frankqian\TeamsApps\mcp-agent\src\myAgent.ts
import { ActivityTypes, ApplicationBuilder, MessageFactory } from '@microsoft/agents-hosting'
import { HumanMessage } from '@langchain/core/messages'
import { sysMessage, initializeMcpAgent } from './utils/index.js'

export const mcpAgent = new ApplicationBuilder().build()

// Initialize agent
let mcpClient;
let reactAgent;

// Initialize and setup the agent
try {
  // Use the utility function to initialize the agent
  const initResult = await initializeMcpAgent();
  mcpClient = initResult.client;
  reactAgent = initResult.reactAgent;
  
  // Register the activity handler
  mcpAgent.activity(ActivityTypes.Message, async (context, state) => {
    try {
      const llmResponse = await reactAgent.invoke({
        messages: [
          sysMessage,
          new HumanMessage(context.activity.text!)
        ]
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
