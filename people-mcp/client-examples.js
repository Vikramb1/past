#!/usr/bin/env node

/**
 * Client Examples for People MCP Server
 * Shows how to interact with the HTTP server running on port 4206
 */

// Using Node.js fetch (built-in from Node 18+)
const SERVER_URL = 'http://localhost:4206';

console.log('🔍 People MCP Client Examples\n');

// Example 1: Search for people
async function searchPeople(query) {
  console.log(`📎 Searching for: "${query}"`);

  const response = await fetch(`${SERVER_URL}/api/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ query })
  });

  const data = await response.json();

  if (data.success) {
    console.log(`✅ Found ${data.results.length} results:`);
    data.results.forEach(person => {
      console.log(`  - ${person.name} (${person.email}) - ${person.company}`);
    });
  } else {
    console.log(`❌ Error: ${data.error}`);
  }
  console.log('');
}

// Example 2: Get person details
async function getPersonDetails(email) {
  console.log(`👤 Getting details for: ${email}`);

  const response = await fetch(`${SERVER_URL}/api/person/${email}`);
  const data = await response.json();

  if (data.success) {
    const person = data.person;
    console.log('✅ Person Details:');
    console.log(`  Name: ${person.name}`);
    console.log(`  Email: ${person.email}`);
    console.log(`  Company: ${person.company}`);
    console.log(`  Title: ${person.title}`);
    console.log(`  Location: ${person.location}`);
    console.log(`  Phone: ${person.phone}`);
  } else {
    console.log(`❌ Error: ${data.error}`);
  }
  console.log('');
}

// Example 3: List all people
async function listAllPeople(limit = 5) {
  console.log(`📋 Listing up to ${limit} people`);

  const response = await fetch(`${SERVER_URL}/api/people?limit=${limit}`);
  const data = await response.json();

  if (data.success) {
    console.log(`✅ Found ${data.results.length} people:`);
    data.results.forEach((person, index) => {
      console.log(`  ${index + 1}. ${person.name} - ${person.company} (${person.email})`);
    });
  } else {
    console.log(`❌ Error: ${data.error}`);
  }
  console.log('');
}

// Example 4: Health check
async function checkHealth() {
  console.log('🏥 Checking server health');

  const response = await fetch(`${SERVER_URL}/health`);
  const data = await response.json();

  console.log(`✅ Server Status: ${data.status}`);
  console.log(`  Service: ${data.service} v${data.version}`);
  console.log(`  Port: ${data.port}`);
  console.log('');
}

// Example 5: Using MCP protocol via fetch with SSE
async function testMCPProtocol() {
  console.log('🔧 Testing MCP Protocol via SSE\n');
  console.log('To test MCP protocol:');
  console.log('1. Open the Online MCP Inspector');
  console.log('2. Select "SSE" transport');
  console.log(`3. Enter URL: ${SERVER_URL}/sse`);
  console.log('4. Click Connect');
  console.log('');
}

// Run examples
async function runExamples() {
  try {
    // Check if server is running
    await checkHealth();

    // Run search examples
    await searchPeople('natera');
    await searchPeople('vikram');
    await searchPeople('works at Arcadia Robotics');

    // Get specific person details
    await getPersonDetails('sanjayamirthraj@example.com');

    // List all people
    await listAllPeople(3);

    // Show MCP protocol info
    testMCPProtocol();

  } catch (error) {
    console.error('❌ Error connecting to server:', error.message);
    console.log('\nMake sure the server is running:');
    console.log('  npm run serve');
  }
}

// Python client example
function showPythonExample() {
  console.log('\n📝 Python Client Example:\n');
  console.log(`import requests

SERVER_URL = 'http://localhost:4206'

# Search for people
response = requests.post(f'{SERVER_URL}/api/search',
    json={'query': 'natera'})
data = response.json()
print(f"Found {len(data['results'])} results")

# Get person details
response = requests.get(f'{SERVER_URL}/api/person/sanjayamirthraj@example.com')
person = response.json()['person']
print(f"Name: {person['name']}, Company: {person['company']}")

# List all people
response = requests.get(f'{SERVER_URL}/api/people?limit=5')
people = response.json()['results']
for person in people:
    print(f"- {person['name']} ({person['email']})")
`);
}

// cURL examples
function showCurlExamples() {
  console.log('\n📝 cURL Examples:\n');
  console.log(`# Search for people
curl -X POST http://localhost:4206/api/search \\
  -H "Content-Type: application/json" \\
  -d '{"query": "natera"}'

# Get person details
curl http://localhost:4206/api/person/sanjayamirthraj@example.com

# List all people
curl http://localhost:4206/api/people?limit=5

# Health check
curl http://localhost:4206/health
`);
}

// Browser example
function showBrowserExample() {
  console.log('\n📝 Browser JavaScript Example:\n');
  console.log(`// In your browser console or web app:

// Search for people
fetch('http://localhost:4206/api/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: 'natera' })
})
.then(res => res.json())
.then(data => {
  console.log('Found:', data.results);
});

// Get person details
fetch('http://localhost:4206/api/person/sanjayamirthraj@example.com')
  .then(res => res.json())
  .then(data => console.log('Person:', data.person));
`);
}

// Main execution
console.log('=====================================\n');
runExamples().then(() => {
  showPythonExample();
  showCurlExamples();
  showBrowserExample();

  console.log('\n💡 To run the server:');
  console.log('   npm run serve');
  console.log('\n💡 To access from other machines:');
  console.log('   Replace "localhost" with your machine\'s IP address');
});