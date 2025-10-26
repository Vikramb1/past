const { Composio } = require('@composio/core');

async function sendDirectEmail() {
    try {
        // Initialize Composio
        const composio = new Composio({ apiKey: 'ak_v3uGsSWnWBJccABnI_5c' });
        const authConfig = "ac_8YWxziF2cyD3";

        console.log('Testing direct email execution...\n');

        // Get the tool info first
        const tools = await composio.tools.get(authConfig, { tools: ["GMAIL_SEND_EMAIL"] });
        console.log('Tool retrieved:', tools[0].function.name);
        console.log('Tool version:', tools[0].version || 'Not specified');
        console.log('Tool metadata:', tools[0].metadata || 'None');

        // Try different toolkit versions
        const versions = ['v2', 'v1', '1.0.0', 'latest'];

        // Try direct execution with composio.tools
        console.log('\nAttempting to send email directly...');

        for (const version of versions) {
            console.log(`\nTrying with version: ${version}`);
            try {
                const result = await composio.tools.execute(
                    'GMAIL_SEND_EMAIL',  // Use uppercase as shown in the tool
                    {
                        recipient_email: 'sanjay.amirthraj@gmail.com',
                        subject: 'Test from CalHacks',
                        body: 'Hi from CalHacks! This is a test email sent via the Composio workflow integration. The face recognition system is working!'
                    },
                    authConfig,
                    version
                );

                console.log(`\n✅ Email sent successfully with version ${version}!`);
                console.log('Result:', JSON.stringify(result, null, 2));
                return result;

            } catch (e) {
                console.log(`Version ${version} failed:`, e.message);
                continue;
            }
        }

        throw new Error('All versions failed');

    } catch (error) {
        console.error('\n❌ Error:', error.message);
        if (error.stack) {
            console.log('Stack trace:', error.stack);
        }
        throw error;
    }
}

// Run the test
sendDirectEmail()
    .then(() => {
        console.log('\n🎉 Test completed successfully! Check sanjay.amirthraj@gmail.com for the email.');
        process.exit(0);
    })
    .catch((err) => {
        console.log('\n❌ Test failed');
        process.exit(1);
    });