import type { MessageTextContentOutput } from "@azure/ai-projects";
import { AIProjectsClient, isOutputOfType, ToolUtility } from "@azure/ai-projects";
import { delay } from "@azure/core-util";
import { DefaultAzureCredential } from "@azure/identity";
import * as fs from "fs";
import config from "../config.js";

const connectionString = config.connectionString;
const modelDeploymentName = "gpt-4o";
const filePath = "./src/openApi/repairOpenApi.json";

export async function initializeAzureAgent() {
  const client = AIProjectsClient.fromConnectionString(
    connectionString || "",
    new DefaultAzureCredential(),
  );
  const openApiSpec = JSON.parse(fs.readFileSync(filePath, "utf-8"));
  const openApiFunction = {
    name: "repairs",
    spec: openApiSpec,
    description: "Retrieve repairs information",
    auth: { type: "anonymous" },
    default_params: ["format"],
  };
  const openApiTool = ToolUtility.createOpenApiTool(openApiFunction);
  const agent = await client.agents.createAgent(modelDeploymentName, {
    name: "myAgent",
    instructions: "You are a helpful agent",
    tools: [openApiTool.definition],
  });
  return {
    async runUserMessage(userMessage: string) {
      const thread = await client.agents.createThread();
      await client.agents.createMessage(thread.id, {
        role: "user",
        content: userMessage,
      });
      let run = await client.agents.createRun(thread.id, agent.id);
      while (run.status === "queued" || run.status === "in_progress") {
        await delay(1000);
        run = await client.agents.getRun(thread.id, run.id);
      }
      if (run.status === "failed") {
        return `Run failed: ${run.lastError}`;
      }
      const messages = await client.agents.listMessages(thread.id);
      const assistantMessage = messages.data.find((msg) => msg.role === "assistant");
      if (assistantMessage) {
        const textContent = assistantMessage.content.find((content) =>
          isOutputOfType<MessageTextContentOutput>(content, "text"),
        ) as MessageTextContentOutput;
        if (textContent) {
          return textContent.text.value;
        }
      }
      return "No response from assistant.";
    },
    async cleanup() {
      await client.agents.deleteAgent(agent.id);
    }
  };
}
