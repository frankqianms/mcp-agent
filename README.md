# Overview of the Teams MCP Agent template

It showcases how to build an AI agent in Teams capable of chatting with users using MCP servers to enable tools.

## Get started with the template

> **Prerequisites**
>
> To run the template in your local dev machine, you will need:
>
> - [Node.js](https://nodejs.org/en) latest version or higher than v18.0.
> - [Teams Toolkit Visual Studio Code Extension](https://aka.ms/teams-toolkit) latest version or [Teams Toolkit CLI](https://aka.ms/teams-toolkit-cli).
> - An account with [Azure OpenAI](https://aka.ms/oai/access).
> - A [Microsoft 365 account for development](https://docs.microsoft.com/microsoftteams/platform/toolkit/accounts).

### Configurations
1. In file [env/.env.local.user](./env/.env.local.user), fill in your Azure OpenAI key `SECRET_AZURE_OPENAI_API_KEY`, deployment name `AZURE_OPENAI_MODEL_DEPLOYMENT_NAME` and endpoint `AZURE_OPENAI_ENDPOINT`.
1. In file [./src/mcpServers/mcpServersList.json](./src/mcpServers/mcpServersList.json), configure your MCP servers properly.
1. You can reference this [doc](https://loop.cloud.microsoft/p/eyJ1IjoiaHR0cHM6Ly9taWNyb3NvZnQuc2hhcmVwb2ludC5jb20vc2l0ZXMvMWUwM2YyOWEtMDk1Ni00Zjc2LTlkM2EtNTU5ZTIzNWFkZDE5P25hdj1jejBsTWtaemFYUmxjeVV5UmpGbE1ETm1NamxoTFRBNU5UWXROR1kzTmkwNVpETmhMVFUxT1dVeU16VmhaR1F4T1Naa1BXSWxNakZGTlRsNE1qWnpSbG93UTB3Mk4ybEliRko1UnpCM1dFZHVSa1JaZFU1NFNtdHRRMVZVWnkxSGRITk1RVTA0WmtRNGFESjJVM0p3U0d4V1QybEhRVFEzSm1ZOU1ERTBURkZRUkZaRE1rdEhTazVDUjBOSVJVWkhXVlEwU3pKUVZrODJURVpCVmlaalBTVXlSaVpoUFV4dmIzQkJjSEFtY0QwbE5EQm1iSFZwWkhnbE1rWnNiMjl3TFhCaFoyVXRZMjl1ZEdGcGJtVnlKbmc5SlRkQ0pUSXlkeVV5TWlVelFTVXlNbFF3VWxSVlNIaDBZVmRPZVdJelRuWmFibEYxWXpKb2FHTnRWbmRpTW14MVpFTTFhbUl5TVRoWmFVWkdUbFJzTkUxcVducFNiRzkzVVRCM01rNHliRWxpUmtvMVVucENNMWRGWkhWU2ExSmFaRlUxTkZOdGRIUlJNVlpWV25reFNHUklUazFSVlRBMFdtdFJOR0ZFU2pKVk0wcDNVMGQ0VjFReWJFaFJWRkV6WmtSQmVFNUZlRkpWUlZKWFUwVmtVVk5FU1hsVk1FMTVWbFJrVTFKNlRYbFJiR2hVVjBWa1dsSkZlR0ZVTUUwbE0wUWxNaklsTWtNbE1qSnBKVEl5SlROQkpUSXlaakEwWWpFeVpUTXRaRFkyT0MwME56QmtMVGhtWkdNdE1UZGlZakEzTURNNFlqRTFKVEl5SlRkRSJ9?ct=1744868463887&&LOF=1) to configure your API Center MCP server. If you can not do that, delete the relative part in [./src/mcpServers/mcpServersList.json](./src/mcpServers/mcpServersList.json).
```
    "apic-api": {
        "command": "npx",
        "args": ["-y", "azure-api-center-mcp-server@latest"],
        "env": {
            "CLIENT_ID": "",
            "TENANT_ID": "",
            "RUNTIME_URL": ""
        }
    }
```
1. Fill in your Azure AI Foundry project connection string in [env/.env.local.user](./env/.env.local.user) or [env/.env.testtool.user](./env/.env.testtool.user). It can be found in your [Azure AI Foundry project overview page](https://ai.azure.com/).
1. In [openApi/repairOpenApi.json](./src/openApi/repairOpenApi.json), input your repair OpenApi json content.

### Conversation with bot
1. Select the Teams Toolkit icon on the left in the VS Code toolbar.
1. In the Account section, sign in with your [Microsoft 365 account](https://docs.microsoft.com/microsoftteams/platform/toolkit/accounts) if you haven't already.
1. Press F5 to start debugging which launches your app in Teams using a web browser. Select `Debug in Teams (Edge)` or `Debug in Teams (Chrome)`.
1. When Teams launches in the browser, select the Add button in the dialog to install your app to Teams.
1. You will receive a welcome message from the bot, or send any message to get a response.

**Congratulations**! You are running an application that can now interact with users in Teams: When you are communicating with the agent, tool calling information will show if any tools are called.

> For local debugging using Teams Toolkit CLI, you need to do some extra steps described in [Set up your Teams Toolkit CLI for local debugging](https://aka.ms/teamsfx-cli-debugging).

![ai agent](./src/conversation.png)

## Known issue
- If you use `Debug in Test Tool` to local debug, you might get an error `InternalServiceError: connect ECONNREFUSED 127.0.0.1:3978` in Test Tool console log or error message `Error: Cannot connect to your app,
please make sure your app is running or restart your app` in log panel of Test Tool web page. You can wait for Python launch console ready and then refresh the front end web page.
- When you use `Launch Remote in Teams` to remote debug after deployment, you might loose interaction with your bot. This is because the remote service needs to restart. Please wait for several minutes to retry it.