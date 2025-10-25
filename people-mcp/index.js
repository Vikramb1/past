#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ToolSchema
} from "@modelcontextprotocol/sdk/types.js";
import { createClient } from '@supabase/supabase-js';

// Hardcoded configuration
const SUPABASE_URL = 'https://afwpcbmhvjwrnolhrocz.supabase.co';
const SUPABASE_SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFmd3BjYm1odmp3cm5vbGhyb2N6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTM2NzYwOCwiZXhwIjoyMDc2OTQzNjA4fQ.32C1dNH0-aQFhpODSlw9UzAj721kjP_BIZfuS-2VMGE';

// Initialize Supabase client
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

// Create MCP server
const server = new Server(
  {
    name: "people-mcp",
    version: "1.0.0"
  },
  {
    capabilities: {
      tools: {}
    }
  }
);

// Helper function to parse natural language queries
function parseNaturalLanguageQuery(query) {
  const lowerQuery = query.toLowerCase();

  // Check if it's an image search request
  if (lowerQuery.includes('image') || lowerQuery.includes('photo') || lowerQuery.includes('picture')) {
    return { type: 'image', query: lowerQuery };
  }

  // Extract search terms for people
  const searchTerms = {
    name: null,
    email: null,
    company: null,
    title: null,
    location: null,
    phone: null
  };

  // Look for email patterns
  const emailMatch = query.match(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/);
  if (emailMatch) {
    searchTerms.email = emailMatch[0];
  }

  // Look for phone patterns
  const phoneMatch = query.match(/\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/);
  if (phoneMatch) {
    searchTerms.phone = phoneMatch[0];
  }

  // Look for company mentions
  if (lowerQuery.includes('works at') || lowerQuery.includes('from company')) {
    const companyMatch = lowerQuery.match(/(?:works at|from company|company)\s+([^,.\s]+(?:\s+[^,.\s]+)*)/);
    if (companyMatch) {
      searchTerms.company = companyMatch[1].trim();
    }
  }

  // Look for title mentions
  if (lowerQuery.includes('title') || lowerQuery.includes('position') || lowerQuery.includes('role')) {
    const titleMatch = lowerQuery.match(/(?:title|position|role)\s+(?:is\s+)?([^,.\s]+(?:\s+[^,.\s]+)*)/);
    if (titleMatch) {
      searchTerms.title = titleMatch[1].trim();
    }
  }

  // Look for location mentions
  if (lowerQuery.includes('from') || lowerQuery.includes('in') || lowerQuery.includes('location')) {
    const locationMatch = lowerQuery.match(/(?:from|in|location)\s+([^,.\s]+(?:\s+[^,.\s]+)*)/);
    if (locationMatch) {
      searchTerms.location = locationMatch[1].trim();
    }
  }

  // Look for name (if not other specific fields)
  if (!searchTerms.email && !searchTerms.phone && !searchTerms.company && !searchTerms.title && !searchTerms.location) {
    // Remove common words and extract potential name
    const nameWords = query
      .replace(/find|search|look for|who is|tell me about|person named|called/gi, '')
      .trim()
      .split(/\s+/)
      .filter(word => word.length > 2);

    if (nameWords.length > 0) {
      searchTerms.name = nameWords.join(' ');
    }
  }

  return { type: 'search', searchTerms };
}

// Helper function to format person data
function formatPersonData(record) {
  const result = {
    email: record.email,
    name: record.name,
    phone: record.phone,
    company: record.company,
    title: record.title,
    location: record.location
  };

  // Parse the JSON data field if it exists
  if (record.data) {
    try {
      const parsedData = typeof record.data === 'string' ? JSON.parse(record.data) : record.data;

      if (parsedData.data && parsedData.data.result) {
        const nyneData = parsedData.data.result;
        result.detailed = {
          displayName: nyneData.displayname,
          bio: nyneData.bio,
          gender: nyneData.gender,
          location: nyneData.location || result.location,
          phones: nyneData.fullphone || [],
          alternativeEmails: nyneData.altemails || [],
          socialProfiles: nyneData.social_profiles || {},
          organizations: nyneData.organizations || []
        };
      }
    } catch (e) {
      console.error('Error parsing data field:', e);
    }
  }

  return result;
}

// Register handlers for listing tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "search_people",
        description: "Search for people using natural language queries. You can search by name, email, company, title, location, or phone number.",
        inputSchema: {
          type: "object",
          properties: {
            query: {
              type: "string",
              description: "Natural language query to search for people (e.g., 'find John Smith', 'who works at Tech Corp', 'person with email john@example.com')"
            }
          },
          required: ["query"]
        }
      },
      {
        name: "get_person_details",
        description: "Get detailed information about a specific person by their email address",
        inputSchema: {
          type: "object",
          properties: {
            email: {
              type: "string",
              description: "Email address of the person to get details for"
            }
          },
          required: ["email"]
        }
      },
      {
        name: "search_by_image",
        description: "Find a person by their image (searches the images_names table)",
        inputSchema: {
          type: "object",
          properties: {
            email: {
              type: "string",
              description: "Email to find associated image for"
            }
          },
          required: ["email"]
        }
      },
      {
        name: "list_all_people",
        description: "List all people in the database with basic information",
        inputSchema: {
          type: "object",
          properties: {
            limit: {
              type: "number",
              description: "Maximum number of results to return (default: 10)",
              default: 10
            }
          }
        }
      }
    ]
  };
});

// Register handler for calling tools
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "search_people": {
        const { query } = args;
        const parsed = parseNaturalLanguageQuery(query);

        if (parsed.type === 'image') {
          // Redirect to image search
          const { data, error } = await supabase
            .from('images_names')
            .select('email')
            .limit(10);

          if (error) throw error;

          return {
            content: [{
              type: "text",
              text: `Found ${data.length} people with images. Use search_by_image with specific email to get image data.`
            }]
          };
        }

        // Build query based on search terms
        let supabaseQuery = supabase.from('nyne_results').select('*');
        const { searchTerms } = parsed;

        // Apply filters based on search terms
        if (searchTerms.email) {
          supabaseQuery = supabaseQuery.ilike('email', `%${searchTerms.email}%`);
        }
        if (searchTerms.name) {
          supabaseQuery = supabaseQuery.ilike('name', `%${searchTerms.name}%`);
        }
        if (searchTerms.company) {
          supabaseQuery = supabaseQuery.ilike('company', `%${searchTerms.company}%`);
        }
        if (searchTerms.title) {
          supabaseQuery = supabaseQuery.ilike('title', `%${searchTerms.title}%`);
        }
        if (searchTerms.location) {
          supabaseQuery = supabaseQuery.ilike('location', `%${searchTerms.location}%`);
        }
        if (searchTerms.phone) {
          supabaseQuery = supabaseQuery.ilike('phone', `%${searchTerms.phone}%`);
        }

        const { data, error } = await supabaseQuery.limit(10);

        if (error) throw error;

        if (data.length === 0) {
          return {
            content: [{
              type: "text",
              text: "No people found matching your search criteria."
            }]
          };
        }

        const results = data.map(formatPersonData);

        return {
          content: [{
            type: "text",
            text: `Found ${results.length} people:\n\n${results.map((p, i) =>
              `${i + 1}. **${p.name || 'Unknown'}**\n` +
              `   Email: ${p.email}\n` +
              `   Company: ${p.company || 'N/A'}\n` +
              `   Title: ${p.title || 'N/A'}\n` +
              `   Location: ${p.location || 'N/A'}\n` +
              `   Phone: ${p.phone || 'N/A'}`
            ).join('\n\n')}`
          }]
        };
      }

      case "get_person_details": {
        const { email } = args;

        const { data, error } = await supabase
          .from('nyne_results')
          .select('*')
          .eq('email', email)
          .single();

        if (error) {
          if (error.code === 'PGRST116') {
            return {
              content: [{
                type: "text",
                text: `No person found with email: ${email}`
              }]
            };
          }
          throw error;
        }

        const person = formatPersonData(data);

        let detailsText = `**Person Details**\n\n`;
        detailsText += `**Basic Information:**\n`;
        detailsText += `- Name: ${person.name || 'Unknown'}\n`;
        detailsText += `- Email: ${person.email}\n`;
        detailsText += `- Phone: ${person.phone || 'N/A'}\n`;
        detailsText += `- Company: ${person.company || 'N/A'}\n`;
        detailsText += `- Title: ${person.title || 'N/A'}\n`;
        detailsText += `- Location: ${person.location || 'N/A'}\n`;

        if (person.detailed) {
          const d = person.detailed;
          detailsText += `\n**Extended Information:**\n`;
          if (d.displayName) detailsText += `- Display Name: ${d.displayName}\n`;
          if (d.bio) detailsText += `- Bio: ${d.bio}\n`;
          if (d.gender) detailsText += `- Gender: ${d.gender}\n`;

          if (d.phones && d.phones.length > 0) {
            detailsText += `\n**Phone Numbers:**\n`;
            d.phones.forEach(p => {
              detailsText += `- ${p.fullphone}\n`;
            });
          }

          if (d.alternativeEmails && d.alternativeEmails.length > 0) {
            detailsText += `\n**Alternative Emails:**\n`;
            d.alternativeEmails.forEach(e => {
              detailsText += `- ${e}\n`;
            });
          }

          if (d.socialProfiles && Object.keys(d.socialProfiles).length > 0) {
            detailsText += `\n**Social Profiles:**\n`;
            for (const [platform, profile] of Object.entries(d.socialProfiles)) {
              if (profile.url) {
                detailsText += `- ${platform}: ${profile.url}\n`;
              }
            }
          }

          if (d.organizations && d.organizations.length > 0) {
            detailsText += `\n**Organizations:**\n`;
            d.organizations.forEach(org => {
              detailsText += `- ${org.name}${org.title ? ` (${org.title})` : ''}\n`;
            });
          }
        }

        return {
          content: [{
            type: "text",
            text: detailsText
          }]
        };
      }

      case "search_by_image": {
        const { email } = args;

        const { data, error } = await supabase
          .from('images_names')
          .select('email, image')
          .eq('email', email)
          .single();

        if (error) {
          if (error.code === 'PGRST116') {
            return {
              content: [{
                type: "text",
                text: `No image found for email: ${email}`
              }]
            };
          }
          throw error;
        }

        // Check if we also have person data
        const { data: personData } = await supabase
          .from('nyne_results')
          .select('*')
          .eq('email', email)
          .single();

        let responseText = `**Image Found for ${email}**\n\n`;
        responseText += `Image data available (stored as bytea).\n`;

        if (personData) {
          const person = formatPersonData(personData);
          responseText += `\n**Associated Person Data:**\n`;
          responseText += `- Name: ${person.name || 'Unknown'}\n`;
          responseText += `- Company: ${person.company || 'N/A'}\n`;
          responseText += `- Title: ${person.title || 'N/A'}\n`;
          responseText += `- Location: ${person.location || 'N/A'}\n`;
        } else {
          responseText += `\nNo additional person data found in nyne_results table.`;
        }

        return {
          content: [{
            type: "text",
            text: responseText
          }]
        };
      }

      case "list_all_people": {
        const { limit = 10 } = args;

        const { data, error } = await supabase
          .from('nyne_results')
          .select('*')
          .limit(limit);

        if (error) throw error;

        if (data.length === 0) {
          return {
            content: [{
              type: "text",
              text: "No people found in the database."
            }]
          };
        }

        const results = data.map(formatPersonData);

        return {
          content: [{
            type: "text",
            text: `Listing ${results.length} people:\n\n${results.map((p, i) =>
              `${i + 1}. **${p.name || 'Unknown'}**\n` +
              `   Email: ${p.email}\n` +
              `   Company: ${p.company || 'N/A'}\n` +
              `   Title: ${p.title || 'N/A'}\n` +
              `   Location: ${p.location || 'N/A'}`
            ).join('\n\n')}`
          }]
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    console.error('Error executing tool:', error);
    return {
      content: [{
        type: "text",
        text: `Error: ${error.message}`
      }],
      isError: true
    };
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("People MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});