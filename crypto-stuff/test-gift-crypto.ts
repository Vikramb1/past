import axios from 'axios';

// Test script for the crypto gifting functionality
// This demonstrates how to send crypto as a gift to someone

const API_BASE_URL = 'http://localhost:3000';

// Configuration
// IMPORTANT: Replace this with a funded testnet private key
// You can get test SUI from the faucet first using the /faucet endpoint
const SENDER_PRIVATE_KEY = '0x...'; // Your funded wallet's private key

const RECIPIENT_EMAIL = 'sanjay.amirthraj@gmail.com'; // Will use default if not specified
const AMOUNT_TO_GIFT = 1000000; // 0.001 SUI in MIST
const SENDER_NAME = 'Your Friend'; // Optional, appears in the email

async function testGiftCrypto() {
    console.log('🎁 Testing Crypto Gift Feature...\n');

    try {
        // First, let's check if the API is running
        const healthCheck = await axios.get(API_BASE_URL);
        console.log('✅ API is running\n');

        // Optional: Check sender's balance first
        // Uncomment and add your sender address to check balance
        // const senderAddress = '0x...';
        // const balanceResponse = await axios.get(`${API_BASE_URL}/balance/${senderAddress}`);
        // console.log('Sender balance:', balanceResponse.data.balanceInSUI, 'SUI\n');

        // Send the crypto gift
        console.log(`📤 Sending ${AMOUNT_TO_GIFT / 1_000_000_000} SUI as a gift...`);
        console.log(`📧 Recipient email: ${RECIPIENT_EMAIL}`);
        console.log(`💰 Amount: ${AMOUNT_TO_GIFT / 1_000_000_000} SUI\n`);

        const giftResponse = await axios.post(`${API_BASE_URL}/gift-crypto`, {
            senderPrivateKey: SENDER_PRIVATE_KEY,
            recipientEmail: RECIPIENT_EMAIL,
            amount: AMOUNT_TO_GIFT,
            senderName: SENDER_NAME
        });

        if (giftResponse.data.success) {
            console.log('🎉 Gift sent successfully!\n');
            console.log('Transaction Details:');
            console.log('-------------------');
            console.log(`Transaction ID: ${giftResponse.data.transaction.digest}`);
            console.log(`From: ${giftResponse.data.transaction.from}`);
            console.log(`To: ${giftResponse.data.recipient.address}`);
            console.log(`Amount: ${giftResponse.data.transaction.amountInSUI} SUI`);
            console.log(`Explorer: ${giftResponse.data.transaction.explorerUrl}\n`);

            console.log('Recipient Wallet:');
            console.log('----------------');
            console.log(`Address: ${giftResponse.data.recipient.address}`);
            console.log(`Balance: ${giftResponse.data.recipient.balance.balanceInSUI} SUI\n`);

            console.log('Email Status:');
            console.log('------------');
            if (giftResponse.data.email.sent) {
                console.log(`✅ Email sent successfully to ${giftResponse.data.email.to}`);
                console.log('The recipient will receive their wallet credentials via email.');
            } else {
                console.log(`⚠️ Email failed: ${giftResponse.data.email.error}`);
                console.log('\nRecipient credentials (share manually):');
                console.log(`Address: ${giftResponse.data.recipient.address}`);
                console.log(`Private Key: ${giftResponse.data.recipient.privateKey}`);
            }
        } else {
            console.error('❌ Gift failed:', giftResponse.data.message);
            console.error('Error:', giftResponse.data.error);
        }
    } catch (error: any) {
        console.error('❌ Error during gift process:');

        if (error.response) {
            // API responded with an error
            console.error('Status:', error.response.status);
            console.error('Message:', error.response.data.message || error.response.data.error);
            console.error('Details:', error.response.data.details);

            // Special handling for insufficient balance
            if (error.response.data.needsFaucet) {
                console.log('\n💡 Tip: Your wallet needs funds. Use the faucet to get test SUI:');
                console.log(`curl -X POST ${API_BASE_URL}/faucet -H "Content-Type: application/json" -d '{"address": "YOUR_ADDRESS"}'`);
            }
        } else if (error.request) {
            // Request was made but no response
            console.error('No response from API. Is the server running?');
            console.log('\n💡 Start the server with: npm run dev');
        } else {
            // Something else happened
            console.error('Error:', error.message);
        }
    }
}

// Instructions for using this test
console.log('========================================');
console.log('   CRYPTO GIFT TEST INSTRUCTIONS');
console.log('========================================\n');
console.log('Before running this test:\n');
console.log('1. Set up email credentials:');
console.log('   - Copy .env.example to .env');
console.log('   - Add your Gmail credentials (use app-specific password)');
console.log('   - Or configure another SMTP service in emailService.ts\n');
console.log('2. Get a funded testnet wallet:');
console.log('   - Generate a keypair: GET /generate-keypair');
console.log('   - Request test SUI: POST /faucet');
console.log('   - Update SENDER_PRIVATE_KEY in this file\n');
console.log('3. Update recipient email (optional):');
console.log('   - Change RECIPIENT_EMAIL or leave default\n');
console.log('4. Start the API server:');
console.log('   npm run dev\n');
console.log('5. Run this test:');
console.log('   npx ts-node crypto-stuff/test-gift-crypto.ts\n');
console.log('========================================\n');

// Uncomment to run the test
// testGiftCrypto();

// Export for use in other scripts
export { testGiftCrypto };