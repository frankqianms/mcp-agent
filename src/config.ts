const config = {
    clientId: process.env.clientSecret,
    clientSecret: process.env.clientSecret,
    azureOpenAIKey: process.env.AZURE_OPENAI_API_KEY,
    azureOpenAIEndpoint: process.env.AZURE_OPENAI_ENDPOINT,
    azureOpenAIDeploymentName: process.env.AZURE_OPENAI_DEPLOYMENT_NAME,
    azureOpenAIApiVersion: "2024-06-01",
    connectionString: process.env.AZURE_AGENT_CONNECTION_STRING
  };
  
export default config;