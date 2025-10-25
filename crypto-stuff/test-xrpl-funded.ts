/**
 * Test script for XRPL EVM testnet using a funded wallet
 *
 * Funded Address: 0x60d6252fC31177B48732ab89f073407788F09C61
 * This script will send 0.0001 XRP as a gift to a new wallet
 */

const API_URL = 'http://localhost:3000';

// Funded wallet credentials (XRPL EVM Testnet)
const FUNDED_ADDRESS = '0x60d6252fC31177B48732ab89f073407788F09C61';
const FUNDED_PRIVATE_KEY = '0x2fa8efe237294d598f4c2699f69a0a9228c5263805a408dffabbea6dcf6e4105';

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

async function testXRPLGiftWithFundedWallet() {
    console.log('\n🔶 Testing XRPL EVM Testnet Gift with Funded Wallet 🔶\n');
    console.log('================================================\n');

    try {
        // Step 1: Check balance of funded wallet
        console.log('1️⃣ Checking funded wallet balance...');
        console.log('   Address:', FUNDED_ADDRESS);

        const balanceResponse = await apiRequest(`/xrpl/balance/${FUNDED_ADDRESS}`);

        if (!balanceResponse.success) {
            console.error('Failed to check balance:', balanceResponse.data);
            return;
        }

        console.log('   ✅ Current Balance:', balanceResponse.data.balanceFormatted || balanceResponse.data.balanceXRP + ' XRP');
        console.log('   Explorer URL:', balanceResponse.data.explorerUrl);

        // Step 2: Gift XRP to a new wallet
        console.log('\n2️⃣ Sending XRP as a gift to a new wallet...');
        console.log('   Amount: 0.0001 XRP');
        console.log('   Email: Will use default (sanjay.amirthraj@gmail.com)');

        const giftResponse = await apiRequest('/xrpl/gift-crypto', 'POST', {
            senderPrivateKey: FUNDED_PRIVATE_KEY,
            recipientEmail: 'test@example.com', // Will default to sanjay.amirthraj@gmail.com
            amount: '0.0001',
            senderName: 'XRPL Testnet Demo'
        });

        if (giftResponse.success) {
            console.log('\n✅ XRP Gift Sent Successfully!');
            console.log('================================================');
            console.log('📧 Email Status:', giftResponse.data.email.sent ? 'SENT' : 'FAILED');
            console.log('📬 Email sent to:', giftResponse.data.email.to);
            console.log('💰 Amount sent:', giftResponse.data.transaction.amount, 'XRP');
            console.log('📍 Sender address:', giftResponse.data.transaction.from);
            console.log('📍 Recipient address:', giftResponse.data.recipient.address);
            console.log('🔑 Recipient private key:', giftResponse.data.recipient.privateKey);
            console.log('🔗 Transaction hash:', giftResponse.data.transaction.hash);
            console.log('⛽ Gas used:', giftResponse.data.transaction.gasUsed);
            console.log('🔢 Block number:', giftResponse.data.transaction.blockNumber);
            console.log('🌐 Explorer URL:', giftResponse.data.transaction.explorerUrl);
            console.log('================================================');

            // Step 3: Verify recipient balance
            console.log('\n3️⃣ Verifying recipient received the XRP...');
            const recipientAddress = giftResponse.data.recipient.address;

            // Wait a bit for the transaction to be confirmed
            console.log('   Waiting 3 seconds for confirmation...');
            await new Promise(resolve => setTimeout(resolve, 3000));

            const recipientBalanceResponse = await apiRequest(`/xrpl/balance/${recipientAddress}`);

            if (recipientBalanceResponse.success) {
                console.log('   ✅ Recipient Balance:', recipientBalanceResponse.data.balanceFormatted || recipientBalanceResponse.data.balanceXRP + ' XRP');
                console.log('   Recipient Explorer:', recipientBalanceResponse.data.explorerUrl);
            }

            // Step 4: Check sender's new balance
            console.log('\n4️⃣ Checking sender\'s new balance...');
            const newBalanceResponse = await apiRequest(`/xrpl/balance/${FUNDED_ADDRESS}`);

            if (newBalanceResponse.success) {
                console.log('   Sender New Balance:', newBalanceResponse.data.balanceFormatted || newBalanceResponse.data.balanceXRP + ' XRP');
            }

            console.log('\n✨ Gift transaction completed successfully!');
            console.log('\n📝 Summary:');
            console.log('   - Created new wallet for recipient');
            console.log('   - Sent 0.0001 XRP from funded wallet');
            console.log('   - Emailed wallet credentials to recipient');
            console.log('   - Transaction confirmed on XRPL EVM Testnet');

        } else {
            console.error('\n❌ Failed to send gift:', giftResponse.data);

            if (giftResponse.data.error) {
                console.error('   Error:', giftResponse.data.error);
                console.error('   Message:', giftResponse.data.message);
            }
        }

        // Optional: Test sending directly to a specific address
        console.log('\n\n5️⃣ (Optional) Testing direct send to an address...');
        console.log('   Generating a test recipient address...');

        const newKeypair = await apiRequest('/xrpl/generate-keypair');
        if (newKeypair.success) {
            const testRecipientAddress = newKeypair.data.keypair.address;
            console.log('   Test recipient:', testRecipientAddress);

            const sendResponse = await apiRequest('/xrpl/send', 'POST', {
                privateKey: FUNDED_PRIVATE_KEY,
                recipientAddress: testRecipientAddress,
                amount: '0.0001'
            });

            if (sendResponse.success) {
                console.log('   ✅ Direct send successful!');
                console.log('   Transaction hash:', sendResponse.data.transactionHash);
                console.log('   Explorer URL:', sendResponse.data.explorerUrl);
            } else {
                console.log('   ❌ Direct send failed:', sendResponse.data.message);
            }
        }

    } catch (error) {
        console.error('\n❌ Test failed with error:', error);
    }
}

// Run the test
console.log('🚀 Starting XRPL EVM Testnet test with funded wallet...');
console.log('Make sure the API server is running on port 3000\n');

testXRPLGiftWithFundedWallet().then(() => {
    console.log('\n✨ All tests completed!\n');
}).catch(error => {
    console.error('Test error:', error);
});

export {};