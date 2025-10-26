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
    // Create MCP server with Gmail toolkit only
    const server = await composio.mcp.create("mcp-gmail-" + Date.now(), {  // Unique name for your MCP server
      toolkits: [
        {
          authConfigId: "ac_8YWxziF2cyD3", // Your Gmail auth config ID
          toolkit: "gmail"
        },
      ],
      allowedTools: ["GMAIL_FETCH_EMAILS", "GMAIL_SEND_EMAIL"]  // Removed Google Calendar
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

    console.log("Connecting to MCP server...");

    const tools = await client.getTools();
    console.log("Tools received:", tools);

    // Check if tools is an array or needs to be converted
    const toolsArray = Array.isArray(tools) ? tools : Object.values(tools);
    if (toolsArray && toolsArray.length > 0) {
      console.log("Available tools:", toolsArray.map((t: any) => t.name || t));
    }

    const agent = new Agent({
      name: "Assistant",
      description: "Helpful AI with MCP tools",
      instructions: "Use the MCP tools to answer. Be specific about what emails you find.",
      model: openai("gpt-4-turbo"),
      tools: tools  // Pass the original tools object/array as received
    });

    console.log("Generating AI response...");
    const res = await agent.generate("Check if I have any urgent or important emails. List the senders and subjects.");
    console.log("\n=== AI Response ===");
    console.log(res.text);
    console.log("==================\n");
  } catch (error) {
    console.error("Error:", error);
  }
}

setupAndRun();