#!/usr/bin/env node

import { spawn } from 'child_process';
import { Readable, Writable } from 'stream';

console.log("🔧 Testing MCP Server Protocol\n");

// Start the MCP server
const serverProcess = spawn('node', ['index.js'], {
  cwd: process.cwd(),
  stdio: ['pipe', 'pipe', 'pipe']
});

let responseBuffer = '';

// Handle server output
serverProcess.stdout.on('data', (data) => {
  responseBuffer += data.toString();

  // Try to parse complete JSON messages
  const lines = responseBuffer.split('\n');
  for (let i = 0; i < lines.length - 1; i++) {
    const line = lines[i].trim();
    if (line) {
      try {
        const response = JSON.parse(line);
        console.log("📥 Server Response:", JSON.stringify(response, null, 2));
      } catch (e) {
        // Not valid JSON yet, continue buffering
      }
    }
  }
  responseBuffer = lines[lines.length - 1];
});

serverProcess.stderr.on('data', (data) => {
  const message = data.toString().trim();
  if (message) {
    console.log("ℹ️  Server:", message);
  }
});

// Send test requests
async function runTests() {
  console.log("📤 Sending initialize request...\n");

  // Initialize request
  const initRequest = {
    jsonrpc: "2.0",
    id: 1,
    method: "initialize",
    params: {
      protocolVersion: "0.1.0",
      capabilities: {},
      clientInfo: {
        name: "test-client",
        version: "1.0.0"
      }
    }
  };

  serverProcess.stdin.write(JSON.stringify(initRequest) + '\n');

  // Wait a bit for response
  await new Promise(resolve => setTimeout(resolve, 1000));

  console.log("\n📤 Sending list tools request...\n");

  // List tools request
  const listToolsRequest = {
    jsonrpc: "2.0",
    id: 2,
    method: "tools/list"
  };

  serverProcess.stdin.write(JSON.stringify(listToolsRequest) + '\n');

  // Wait for response
  await new Promise(resolve => setTimeout(resolve, 1000));

  console.log("\n📤 Sending tool call request (search_people)...\n");

  // Call tool request
  const callToolRequest = {
    jsonrpc: "2.0",
    id: 3,
    method: "tools/call",
    params: {
      name: "search_people",
      arguments: {
        query: "vikram"
      }
    }
  };

  serverProcess.stdin.write(JSON.stringify(callToolRequest) + '\n');

  // Wait for response
  await new Promise(resolve => setTimeout(resolve, 2000));

  console.log("\n✅ Test completed!");

  // Clean up
  serverProcess.kill();
  process.exit(0);
}

// Run tests after a brief startup delay
setTimeout(runTests, 500);

// Handle errors
serverProcess.on('error', (error) => {
  console.error("❌ Server error:", error);
  process.exit(1);
});