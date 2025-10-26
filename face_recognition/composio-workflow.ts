import express from 'express';
import OpenAI from 'openai';
import { Composio } from '@composio/core';

// Initialize Express app
const app = express();
app.use(express.json());

// Initialize Composio client
const composio = new Composio('ak_v3uGsSWnWBJccABnI_5c');

// Initialize OpenAI client with hardcoded API key
const openai = new OpenAI({
    apiKey: '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'
});

// Your user ID
const userId = "0b368692-7942-4da4-8820-f152e2301ff3";

// Gmail auth config - this is the connected account
const authConfig = "ac_8YWxziF2cyD3";

// Health check endpoint
app.get('/', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'Composio Workflow Service',
        userId: userId,
        authConfig: authConfig
    });
});

// Check authorization status
app.get('/auth-status', async (req, res) => {
    try {
        // Try to get tools to verify connection
        const tools = await composio.tools.get(authConfig, { tools: ["GMAIL_SEND_EMAIL"] });

        res.json({
            success: true,
            authorized: tools && tools.length > 0,
            toolCount: tools ? tools.length : 0,
            authConfig: authConfig
        });
    } catch (error: any) {
        res.json({
            success: false,
            authorized: false,
            error: error.message,
            authConfig: authConfig
        });
    }
});

// Main workflow execution endpoint
app.post('/execute-workflow', async (req, res) => {
    try {
        const {
            command,
            personInfo,
            focusedPersonEmail
        } = req.body;

        console.log('\n🚀 Executing workflow...');
        console.log('   Command:', command);
        console.log('   Focused person email:', focusedPersonEmail || 'None');

        // Enhance command with context
        let enhancedCommand = command;

        // If command mentions "them/him/her" and we have an email, add context
        if (focusedPersonEmail) {
            const pronouns = ['them', 'him', 'her', 'this person', 'the person'];
            const commandLower = command.toLowerCase();

            for (const pronoun of pronouns) {
                if (commandLower.includes(pronoun)) {
                    enhancedCommand = `${command}. The person's email is ${focusedPersonEmail}`;
                    break;
                }
            }
        }

        // Add person name context if available
        if (personInfo && personInfo.full_name && personInfo.full_name !== 'Unknown') {
            enhancedCommand = `${enhancedCommand}. The person's name is ${personInfo.full_name}`;
        }

        console.log('🧠 Enhanced command:', enhancedCommand);

        // Get Gmail tools using auth config
        const tools = await composio.tools.get(authConfig, { tools: ["GMAIL_SEND_EMAIL"] });

        if (!tools || tools.length === 0) {
            throw new Error('Gmail not authorized. Please check your auth config: ' + authConfig);
        }

        // Use OpenAI to interpret and execute the command
        const response = await openai.chat.completions.create({
            model: "gpt-4o",
            messages: [
                {
                    role: "system",
                    content: "You are a helpful assistant that sends emails based on user commands. Be concise and professional. If the user mentions 'them' or similar pronouns and provides an email context, use that email."
                },
                {
                    role: "user",
                    content: enhancedCommand
                }
            ],
            tools: tools,
            tool_choice: "auto"
        });

        // Check if there are tool calls to execute
        if (response.choices[0].message.tool_calls) {
            console.log('📧 Executing tool calls...');

            // Execute all tool calls
            const results = [];
            for (const toolCall of response.choices[0].message.tool_calls) {
                console.log(`   Executing: ${toolCall.function.name}`);

                // Execute the tool call
                const executionResult = await composio.actions.execute(
                    toolCall.function.name,
                    JSON.parse(toolCall.function.arguments),
                    authConfig
                );

                results.push(executionResult);
            }

            console.log('✅ Workflow executed successfully!');
            console.log('   Results:', results);

            res.json({
                success: true,
                command: command,
                enhancedCommand: enhancedCommand,
                results: results,
                message: 'Email sent successfully'
            });
        } else {
            // No tool calls, just return the AI response
            const aiResponse = response.choices[0].message.content;
            console.log('ℹ️ No email action taken. AI response:', aiResponse);

            res.json({
                success: true,
                command: command,
                enhancedCommand: enhancedCommand,
                aiResponse: aiResponse,
                message: 'Command processed but no email action was taken'
            });
        }

    } catch (error: any) {
        console.error('❌ Workflow execution error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            command: req.body.command
        });
    }
});

// Parse email from person info
app.post('/extract-email', async (req, res) => {
    try {
        const { personInfo } = req.body;

        // Extract email from summary using regex
        const emailPattern = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;

        let extractedEmail = null;

        // Check summary field
        if (personInfo.summary) {
            const matches = personInfo.summary.match(emailPattern);
            if (matches && matches.length > 0) {
                extractedEmail = matches[0];
            }
        }

        // Check social media
        if (!extractedEmail && personInfo.social_media) {
            for (const [platform, data] of Object.entries(personInfo.social_media)) {
                if (platform.toLowerCase().includes('email')) {
                    extractedEmail = typeof data === 'string' ? data : (data as any).url;
                    break;
                }
            }
        }

        res.json({
            success: true,
            email: extractedEmail
        });

    } catch (error: any) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Start server
const PORT = process.env.PORT || 3002;

app.listen(PORT, () => {
    console.log(`\n🤖 Composio Workflow Service started on port ${PORT}`);
    console.log(`   Auth Config: ${authConfig}`);
    console.log(`   Composio API Key: ak_v3uGsSWnWBJccABnI_5c`);
    console.log(`   OpenAI API Key: sk-proj-XXX...T8A (configured)`);
    console.log(`   Endpoints:`);
    console.log(`   - GET  / (health check)`);
    console.log(`   - GET  /auth-status (check if authorized)`);
    console.log(`   - POST /execute-workflow (run workflow)`);
    console.log(`   - POST /extract-email (extract email from person info)`);
    console.log(`\n✅ Gmail connected via auth config: ${authConfig}`);
});