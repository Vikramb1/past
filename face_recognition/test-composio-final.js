const { Composio } = require('@composio/core');

async function finalTest() {
    try {
        // Initialize Composio
        const composio = new Composio({ apiKey: 'ak_v3uGsSWnWBJccABnI_5c' });
        const authConfig = "ac_8YWxziF2cyD3";

        console.log('=== FINAL TEST: Sending Email via Composio ===\n');

        // Get tools and examine structure
        const tools = await composio.tools.get(authConfig, { tools: ["GMAIL_SEND_EMAIL"] });
        console.log('Tool retrieved successfully');

        // Log all properties of the tool to find toolkit info
        console.log('\nTool properties:');
        const tool = tools[0];
        for (const key in tool) {
            if (typeof tool[key] !== 'function' && key !== 'function') {
                console.log(`  ${key}:`, JSON.stringify(tool[key]).substring(0, 100));
            }
        }

        // Try using executeComposioTool directly
        console.log('\n📧 Attempting to send email...\n');

        try {
            // First, let's get the raw tool info
            const rawTool = await composio.tools.getRawComposioToolBySlug('GMAIL_SEND_EMAIL');
            console.log('Raw tool app:', rawTool?.app);
            console.log('Raw tool version:', rawTool?.version);

            // Try with app name as toolkit version
            const result = await composio.tools.executeComposioTool(
                'GMAIL_SEND_EMAIL',
                {
                    recipient_email: 'sanjay.amirthraj@gmail.com',
                    subject: 'Test from CalHacks - Final',
                    body: 'Hi from CalHacks! 🎉\n\nThis email confirms that the Composio workflow integration is working successfully!\n\nBest regards,\nYour Face Recognition System'
                },
                authConfig,
                rawTool?.app || 'gmail'
            );

            console.log('✅ SUCCESS! Email sent!');
            console.log('\nResult:', JSON.stringify(result, null, 2));
            return result;

        } catch (e1) {
            console.log('Direct execute failed:', e1.message);

            // Try alternate approach with toolkits
            try {
                console.log('\nTrying alternate approach with toolkits...');

                // Get toolkit info
                const toolkit = await composio.toolkits.get('gmail');
                console.log('Toolkit retrieved:', toolkit?.name);
                console.log('Toolkit version:', toolkit?.version || 'Not specified');

                // Try with toolkit info
                const result = await composio.tools.executeComposioTool(
                    'GMAIL_SEND_EMAIL',
                    {
                        recipient_email: 'sanjay.amirthraj@gmail.com',
                        subject: 'Test from CalHacks - Final',
                        body: 'Hi from CalHacks! This email was sent via Composio workflow integration.'
                    },
                    authConfig,
                    toolkit?.version || toolkit?.name || 'gmail'
                );

                console.log('✅ SUCCESS with alternate method!');
                console.log('\nResult:', JSON.stringify(result, null, 2));
                return result;

            } catch (e2) {
                console.log('Alternate method failed:', e2.message);
                throw e2;
            }
        }

    } catch (error) {
        console.error('\n❌ Final test failed:', error.message);
        throw error;
    }
}

// Run the test
console.log('Starting Composio email test...\n');
finalTest()
    .then(() => {
        console.log('\n🎉 EMAIL SENT SUCCESSFULLY!');
        console.log('Check sanjay.amirthraj@gmail.com for the test email.');
        process.exit(0);
    })
    .catch((err) => {
        console.log('\n❌ Test failed. The Composio integration may need additional configuration.');
        console.log('\n📝 Summary:');
        console.log('- Gmail tools are accessible via auth config: ac_8YWxziF2cyD3');
        console.log('- The SDK requires a toolkit version for direct execution');
        console.log('- The OpenAI integration approach may be more suitable for production use');
        process.exit(1);
    });