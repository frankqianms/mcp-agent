import { AzureChatOpenAI } from '@langchain/openai'
import config from "../config.js";

// LLM model configuration
export const agentModel = new AzureChatOpenAI({
  azureOpenAIApiKey: config.azureOpenAIKey,
  azureOpenAIApiInstanceName: config.azureOpenAIEndpoint,
  azureOpenAIApiDeploymentName: config.azureOpenAIDeploymentName,
  azureOpenAIApiVersion: config.azureOpenAIApiVersion,
  temperature: 0
})
