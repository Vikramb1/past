# People MCP Server

An MCP (Model Context Protocol) server for querying people information from Supabase databases using natural language queries.

## Features

- **Natural Language Search**: Search for people using natural language queries
- **Multi-field Search**: Find people by name, email, company, title, location, or phone number
- **Detailed Information**: Get comprehensive details about specific individuals
- **Image Search**: Find people associated with images
- **Bulk Listing**: List all people in the database

## Installation

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables in `.env`:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key
```

## Usage with Claude Desktop

Add this configuration to your Claude Desktop config file:

### macOS
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "people-mcp": {
      "command": "node",
      "args": ["/path/to/people-mcp/index.js"],
      "env": {
        "NODE_ENV": "production"
      }
    }
  }
}
```

### Windows
Add to `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "people-mcp": {
      "command": "node",
      "args": ["C:\\path\\to\\people-mcp\\index.js"],
      "env": {
        "NODE_ENV": "production"
      }
    }
  }
}
```

## Available Tools

### 1. search_people
Search for people using natural language queries.

**Examples:**
- "Find John Smith"
- "Who works at Tech Corp"
- "Person with email john@example.com"
- "People from San Francisco"
- "Software engineers"

### 2. get_person_details
Get detailed information about a specific person by their email address.

**Example:**
```
get_person_details(email: "john@example.com")
```

### 3. search_by_image
Find a person by their associated image in the database.

**Example:**
```
search_by_image(email: "john@example.com")
```

### 4. list_all_people
List all people in the database with basic information.

**Example:**
```
list_all_people(limit: 10)
```

## Database Schema

The server works with two Supabase tables:

### images_names Table
- `email` (text): Person's email address
- `image` (bytea): Image data in binary format

### nyne_results Table
- `email` (text): Person's email address
- `name` (text): Full name
- `phone` (text): Phone number
- `text` (text): Additional text data
- `company` (text): Company name
- `title` (text): Job title
- `location` (text): Geographic location
- `data` (json): Extended information including:
  - Display name
  - Bio
  - Gender
  - Alternative emails
  - Social profiles
  - Organizations
  - Additional phone numbers

## Natural Language Processing

The server intelligently parses natural language queries to extract:

- **Names**: Automatically identifies person names in queries
- **Emails**: Recognizes email patterns
- **Phone Numbers**: Detects various phone number formats
- **Companies**: Identifies company names with keywords like "works at"
- **Titles**: Finds job titles with keywords like "title", "position", "role"
- **Locations**: Extracts locations with keywords like "from", "in", "location"

## Testing

To test the server locally:

```bash
npm start
```

The server will run on stdio and output logs to stderr.

## Troubleshooting

1. **Connection Issues**: Ensure your Supabase URL and service key are correctly set in `.env`
2. **Permission Errors**: Make sure the service key has appropriate permissions for both tables
3. **Module Errors**: Ensure you're using Node.js v14+ with ES module support

## License

ISC