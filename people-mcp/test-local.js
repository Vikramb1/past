#!/usr/bin/env node

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { spawn } from "child_process";
import readline from "readline";

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

async function testMCPServer() {
  console.log("🚀 Starting People MCP Server Test...\n");

  // Spawn the MCP server
  const serverProcess = spawn("node", ["index.js"], {
    cwd: process.cwd(),
    stdio: ["pipe", "pipe", "inherit"],
    env: { ...process.env }
  });

  const transport = new StdioClientTransport({
    stdin: serverProcess.stdout,
    stdout: serverProcess.stdin
  });

  const client = new Client({
    name: "test-client",
    version: "1.0.0"
  }, {
    capabilities: {}
  });

  try {
    // Connect to server
    await client.connect(transport);
    console.log("✅ Connected to MCP server\n");

    // List available tools
    const tools = await client.listTools();
    console.log("📋 Available tools:");
    tools.tools.forEach(tool => {
      console.log(`  • ${tool.name}`);
    });
    console.log("");

    // Test scenarios
    console.log("Running test scenarios...\n");

    // Test 1: Search for people
    console.log("Test 1: Searching for people");
    console.log("Query: 'find people from California'");
    try {
      const result = await client.callTool("search_people", {
        query: "find people from California"
      });
      console.log("Result:", result.content[0].text.substring(0, 200) + "...\n");
    } catch (error) {
      console.log("Error:", error.message, "\n");
    }

    // Test 2: List all people
    console.log("Test 2: Listing all people (limit 3)");
    try {
      const result = await client.callTool("list_all_people", {
        limit: 3
      });
      console.log("Result:", result.content[0].text.substring(0, 200) + "...\n");
    } catch (error) {
      console.log("Error:", error.message, "\n");
    }

    // Test 3: Get person details (will likely fail if email doesn't exist)
    console.log("Test 3: Get person details");
    console.log("Query: email 'test@example.com'");
    try {
      const result = await client.callTool("get_person_details", {
        email: "test@example.com"
      });
      console.log("Result:", result.content[0].text.substring(0, 200) + "...\n");
    } catch (error) {
      console.log("Error:", error.message, "\n");
    }

    // Interactive mode
    console.log("\n📝 Interactive Mode - Try your own queries!");
    console.log("Available commands:");
    console.log("  search <query> - Search for people (e.g., 'search John Smith')");
    console.log("  details <email> - Get person details (e.g., 'details john@example.com')");
    console.log("  list <number> - List people (e.g., 'list 5')");
    console.log("  image <email> - Search by image (e.g., 'image john@example.com')");
    console.log("  exit - Quit the test\n");

    const askQuestion = () => {
      rl.question("> ", async (answer) => {
        if (answer.toLowerCase() === 'exit') {
          console.log("\n👋 Goodbye!");
          await client.close();
          serverProcess.kill();
          process.exit(0);
        }

        const parts = answer.split(' ');
        const command = parts[0].toLowerCase();
        const args = parts.slice(1).join(' ');

        try {
          let result;
          switch (command) {
            case 'search':
              result = await client.callTool("search_people", { query: args });
              break;
            case 'details':
              result = await client.callTool("get_person_details", { email: args });
              break;
            case 'list':
              result = await client.callTool("list_all_people", { limit: parseInt(args) || 10 });
              break;
            case 'image':
              result = await client.callTool("search_by_image", { email: args });
              break;
            default:
              console.log("Unknown command. Try 'search', 'details', 'list', 'image', or 'exit'");
              askQuestion();
              return;
          }

          console.log("\nResult:");
          console.log(result.content[0].text);
          console.log("");
        } catch (error) {
          console.log("Error:", error.message, "\n");
        }

        askQuestion();
      });
    };

    askQuestion();

  } catch (error) {
    console.error("❌ Error during testing:", error);
    serverProcess.kill();
    process.exit(1);
  }
}

// Run the test
console.log("People MCP Server - Local Test Client");
console.log("=====================================\n");
testMCPServer().catch(console.error);