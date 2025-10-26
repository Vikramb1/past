import { Composio } from '@composio/core';
import { MCPClient } from "@mastra/mcp";
import { openai } from "@ai-sdk/openai";
import { Agent } from "@mastra/core/agent";

async function setupAndRun() {
  // Initialize Composio with your API key
  const composio = new Composio({
    apiKey: process.env.COMPOSIO_API_KEY || "ak_v3uGsSWnWBJccABnI_5c"
  });

  try {
    // Create MCP server with multiple toolkits
    const server = await composio.mcp.create("mcp-server-" + Date.now(), {  // Unique name for your MCP server
      toolkits: [
        {
          authConfigId: "ac_8YWxziF2cyD3", // Your Gmail auth config ID
          toolkit: "gmail"
        },
      ],
      allowedTools: ["GMAIL_FETCH_EMAILS", "GMAIL_SEND_EMAIL", "GOOGLECALENDAR_EVENTS_LIST"]
    });

    console.log(`Server created: ${server.id}`);

    // Generate server instance for user
    const instance = await composio.mcp.generate("0b368692-7942-4da4-8820-f152e2301ff3", server.id);

    console.log("MCP Server URL:", instance.url);

    // Now use the generated URL with MCP Client
    const client = new MCPClient({
      id: "docs-mcp-client",
      servers: {
        composio: { url: new URL(instance.url) },
      }
    });

    const agent = new Agent({
      name: "Assistant",
      description: "Helpful AI with MCP tools",
      instructions: "Use the MCP tools to answer.",
      model: openai("gpt-4-turbo"),
      tools: await client.getTools()
    });

    const res = await agent.generate("What meetings do I have tomorrow? Also check if I have any urgent emails");
    console.log("AI Response:", res.text);
  } catch (error) {
    console.error("Error:", error);
  }
}

setupAndRun();