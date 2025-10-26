const { Composio } = require('@composio/core');
const OpenAI = require('openai');

async function testComposio() {
    try {
        // Initialize Composio
        const composio = new Composio({ apiKey: 'ak_v3uGsSWnWBJccABnI_5c' });

        // Initialize OpenAI
        const openai = new OpenAI.OpenAI({
            apiKey: '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'
        });

        const authConfig = "ac_8YWxziF2cyD3";

        console.log('Testing Composio SDK...');
        console.log('Composio client:', composio);
        console.log('Available methods:', Object.keys(composio));

        // Try to get tools
        try {
            const tools = await composio.tools.get(authConfig, { tools: ["GMAIL_SEND_EMAIL"] });
            console.log('Tools retrieved:', tools ? tools.length : 0);
        } catch (e) {
            console.log('Error getting tools:', e.message);
        }

        // Try to execute action using tools.execute
        try {
            console.log('\nSending test email to sanjay.amirthraj@gmail.com...');
            const result = await composio.tools.execute(
                'GMAIL_SEND_EMAIL',  // Use the exact action name
                {
                    to: 'sanjay.amirthraj@gmail.com',
                    subject: 'Test from CalHacks',
                    body: 'Hi from CalHacks! This is a test email sent via the Composio workflow integration. The face recognition system with workflow automation is working!'
                },
                authConfig,
                'latest'  // Toolkit version
            );
            console.log('✅ Email sent successfully!');
            console.log('Result:', result);
        } catch (e) {
            console.log('❌ Error sending email:', e.message);
            if (e.response) {
                console.log('Response status:', e.response.status);
                console.log('Response data:', e.response.data);
            }
        }

    } catch (error) {
        console.error('Error:', error);
    }
}

testComposio();