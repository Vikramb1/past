/**
 * Test script for XRPL EVM Sidechain gift crypto functionality
 *
 * This script demonstrates:
 * 1. Generating a new XRPL EVM keypair
 * 2. Checking balance
 * 3. Sending XRP as a gift with email notification
 */

const API_URL = 'http://localhost:3000';

// Helper function to make API requests
async function apiRequest(endpoint: string, method: string = 'GET', body?: any) {
    const options: RequestInit = {
        method,
        headers: {
            'Content-Type': 'application/json',
        }
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${API_URL}${endpoint}`, options);
        const data = await response.json();
        return { success: response.ok, data };
    } catch (error) {
        console.error(`Error calling ${endpoint}:`, error);
        return { success: false, error };
    }
}

async function testXRPLGiftFlow() {
    console.log('\n🔶 Testing XRPL EVM Sidechain Gift Crypto Flow 🔶\n');
    console.log('============================================\n');

    try {
        // Step 1: Generate a new keypair for the sender (for testing)
        console.log('1️⃣ Generating sender keypair...');
        const senderKeypair = await apiRequest('/xrpl/generate-keypair');

        if (!senderKeypair.success) {
            console.error('Failed to generate sender keypair:', senderKeypair.data);
            return;
        }

        console.log('✅ Sender keypair generated:');
        console.log('   Address:', senderKeypair.data.keypair.address);
        console.log('   Private Key:', senderKeypair.data.keypair.privateKey);
        console.log('   Current Balance:', senderKeypair.data.balance.balanceFormatted);
        console.log('   Explorer URL:', senderKeypair.data.explorerUrl);

        // Step 2: Check if sender has balance
        console.log('\n2️⃣ Checking sender balance...');
        const balanceResponse = await apiRequest(`/xrpl/balance/${senderKeypair.data.keypair.address}`);

        console.log('   Balance:', balanceResponse.data.balanceFormatted || '0 XRP');

        if (parseFloat(balanceResponse.data.balanceXRP || '0') < 0.0001) {
            console.log('\n⚠️  Sender has insufficient balance for testing.');
            console.log('   You need to fund this address with test XRP first.');
            console.log('   Address to fund:', senderKeypair.data.keypair.address);
            console.log('\n   Options to get test XRP:');
            console.log('   1. Use the XRPL EVM faucet (if available)');
            console.log('   2. Visit: https://bridge.devnet.xrpl.org/');
            console.log('   3. Or use another funded wallet as sender\n');

            // Try to request from faucet
            console.log('3️⃣ Attempting to request XRP from faucet...');
            const faucetResponse = await apiRequest('/xrpl/faucet', 'POST', {
                address: senderKeypair.data.keypair.address
            });

            if (faucetResponse.success) {
                console.log('✅ Faucet request submitted:', faucetResponse.data.message);
            } else {
                console.log('❌ Faucet request failed:', faucetResponse.data.message);
                console.log('\n📝 Example: Gift XRP using a funded wallet:');
                console.log(`
curl -X POST http://localhost:3000/xrpl/gift-crypto \\
  -H "Content-Type: application/json" \\
  -d '{
    "senderPrivateKey": "YOUR_FUNDED_PRIVATE_KEY",
    "recipientEmail": "friend@email.com",
    "amount": "0.0001",
    "senderName": "Your Name"
  }'
                `);
                return;
            }
        }

        // Step 3: Gift XRP to a recipient
        console.log('\n4️⃣ Sending XRP as a gift...');
        const giftResponse = await apiRequest('/xrpl/gift-crypto', 'POST', {
            senderPrivateKey: senderKeypair.data.keypair.privateKey,
            recipientEmail: 'test@example.com', // Will default to sanjay.amirthraj@gmail.com
            amount: '0.0001',
            senderName: 'XRPL Test Script'
        });

        if (giftResponse.success) {
            console.log('\n✅ XRP Gift Sent Successfully!');
            console.log('============================================');
            console.log('📧 Email sent to:', giftResponse.data.email.to);
            console.log('💰 Amount sent:', giftResponse.data.transaction.amount, 'XRP');
            console.log('📍 Recipient address:', giftResponse.data.recipient.address);
            console.log('🔑 Recipient private key:', giftResponse.data.recipient.privateKey);
            console.log('🔗 Transaction hash:', giftResponse.data.transaction.hash);
            console.log('🌐 Explorer URL:', giftResponse.data.transaction.explorerUrl);
            console.log('============================================\n');
        } else {
            console.error('\n❌ Failed to send gift:', giftResponse.data);

            if (giftResponse.data.needsFaucet) {
                console.log('\n💡 The sender wallet needs funding.');
                console.log('   Please fund this address:', senderKeypair.data.keypair.address);
            }
        }

    } catch (error) {
        console.error('\n❌ Test failed with error:', error);
    }
}

// Run the test
console.log('🚀 Starting XRPL EVM Sidechain API test...');
console.log('Make sure the API server is running on port 3000\n');

testXRPLGiftFlow().then(() => {
    console.log('\n✨ Test completed!\n');
}).catch(error => {
    console.error('Test error:', error);
});

export {};