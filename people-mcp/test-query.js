#!/usr/bin/env node

import { spawn } from 'child_process';

// Start the MCP server
const serverProcess = spawn('node', ['index.js'], {
  cwd: process.cwd(),
  stdio: ['pipe', 'pipe', 'pipe']
});

let responseBuffer = '';

// Handle server output
serverProcess.stdout.on('data', (data) => {
  responseBuffer += data.toString();
  const lines = responseBuffer.split('\n');

  for (let i = 0; i < lines.length - 1; i++) {
    const line = lines[i].trim();
    if (line) {
      try {
        const response = JSON.parse(line);
        if (response.id === 3 && response.result) {
          console.log(response.result.content[0].text);
          serverProcess.kill();
          process.exit(0);
        }
      } catch (e) {
        // Continue
      }
    }
  }
  responseBuffer = lines[lines.length - 1];
});

serverProcess.stderr.on('data', (data) => {
  // Suppress stderr
});

// Send requests
async function searchNatera() {
  // Initialize
  const initRequest = {
    jsonrpc: "2.0",
    id: 1,
    method: "initialize",
    params: {
      protocolVersion: "0.1.0",
      capabilities: {},
      clientInfo: {
        name: "search-client",
        version: "1.0.0"
      }
    }
  };
  serverProcess.stdin.write(JSON.stringify(initRequest) + '\n');

  await new Promise(resolve => setTimeout(resolve, 500));

  // List tools (required by some implementations)
  const listRequest = {
    jsonrpc: "2.0",
    id: 2,
    method: "tools/list"
  };
  serverProcess.stdin.write(JSON.stringify(listRequest) + '\n');

  await new Promise(resolve => setTimeout(resolve, 500));

  // Search for Natera
  const searchRequest = {
    jsonrpc: "2.0",
    id: 3,
    method: "tools/call",
    params: {
      name: "search_people",
      arguments: {
        query: "works at natera"
      }
    }
  };
  serverProcess.stdin.write(JSON.stringify(searchRequest) + '\n');
}

setTimeout(searchNatera, 200);