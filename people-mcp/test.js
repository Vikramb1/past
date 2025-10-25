#!/usr/bin/env node

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { spawn } from "child_process";

async function testMCPServer() {
  console.log("Testing People MCP Server...\n");

  // Spawn the MCP server
  const serverProcess = spawn("node", ["index.js"], {
    cwd: process.cwd(),
    stdio: ["pipe", "pipe", "inherit"]
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
      console.log(`  - ${tool.name}: ${tool.description}`);
    });
    console.log("");

    // Test search_people tool
    console.log("🔍 Testing search_people tool...");
    const searchResult = await client.callTool("search_people", {
      query: "find people from San Francisco"
    });
    console.log("Result:", searchResult.content[0].text);
    console.log("");

    // Test list_all_people tool
    console.log("📂 Testing list_all_people tool...");
    const listResult = await client.callTool("list_all_people", {
      limit: 5
    });
    console.log("Result:", listResult.content[0].text);
    console.log("");

    console.log("✅ All tests completed successfully!");

  } catch (error) {
    console.error("❌ Error during testing:", error);
  } finally {
    // Close connection
    await client.close();
    serverProcess.kill();
    process.exit(0);
  }
}

// Run the test
testMCPServer().catch(console.error);