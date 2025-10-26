#!/usr/bin/env ts-node

/**
 * Test script for email-based crypto transfers
 *
 * This script demonstrates:
 * 1. Sending SUI to an email address (generates new wallet)
 * 2. Sending XRP to an email address (generates new wallet)
 * 3. SMS notifications sent to +15109773150
 *
 * Usage:
 * npx ts-node test-email-transfers.ts
 */

import axios from 'axios';

const API_BASE_URL = 'http://localhost:3001';

// Test configuration
const TEST_CONFIG = {
  // These are test private keys - DO NOT USE IN PRODUCTION
  suiPrivateKey: '0xYOUR_TEST_SUI_PRIVATE_KEY',
  xrpPrivateKey: '0xYOUR_TEST_XRP_PRIVATE_KEY',

  // Test recipient emails
  recipientEmail: 'test.recipient@example.com',

  // Test amounts (small amounts for testing)
  suiAmount: 1000000, // 0.001 SUI
  xrpAmount: '0.0001', // 0.0001 XRP

  // Sender name for email
  senderName: 'Test Sender'
};

// Helper function to make API calls
async function makeApiCall(endpoint: string, method: 'GET' | 'POST' = 'GET', data?: any) {
  try {
    const response = await axios({
      method,
      url: `${API_BASE_URL}${endpoint}`,
      data,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    return response.data;
  } catch (error: any) {
    console.error(`❌ API call failed: ${endpoint}`);
    console.error('Error:', error.response?.data || error.message);
    return null;
  }
}

// Test SUI transfer to email
async function testSuiEmailTransfer() {
  console.log('\n🔷 Testing SUI Transfer to Email Address');
  console.log('=========================================');
  console.log(`📧 Recipient Email: ${TEST_CONFIG.recipientEmail}`);
  console.log(`💰 Amount: ${TEST_CONFIG.suiAmount / 1_000_000_000} SUI`);

  // First, generate a test keypair if needed
  console.log('\nGenerating test SUI keypair...');
  const keypairResponse = await makeApiCall('/generate-keypair');

  if (keypairResponse) {
    console.log(`✅ Generated test address: ${keypairResponse.keypair.suiAddress}`);
    console.log(`   Private key: ${keypairResponse.keypair.privateKey}`);
    console.log(`   Current balance: ${keypairResponse.balance.balanceInSUI} SUI`);

    // Use the generated private key for testing
    const testPrivateKey = keypairResponse.keypair.privateKey;

    console.log('\nNOTE: You need to fund this address with test SUI from the faucet first!');
    console.log('Run: curl -X POST http://localhost:3001/faucet -H "Content-Type: application/json" -d \'{"address":"' + keypairResponse.keypair.suiAddress + '"}\'');

    console.log('\n📤 Sending SUI to email address...');
    const transferData = {
      privateKey: testPrivateKey,
      recipientEmail: TEST_CONFIG.recipientEmail,
      amount: TEST_CONFIG.suiAmount,
      senderName: TEST_CONFIG.senderName
    };

    const result = await makeApiCall('/send-sui', 'POST', transferData);

    if (result?.success) {
      console.log('✅ SUI Transfer Successful!');
      console.log(`   Transaction: ${result.transactionDigest}`);
      console.log(`   New wallet created: ${result.walletCredentials?.address}`);
      console.log(`   SMS notification: ${result.notifications?.sms ? '✅ Sent' : '❌ Failed'}`);
      console.log(`   Email notification: ${result.notifications?.email ? '✅ Sent' : '❌ Failed'}`);
      console.log(`   Explorer: ${result.explorerUrl}`);
    } else {
      console.log('❌ Transfer failed:', result?.message || 'Unknown error');
      if (result?.needsFaucet) {
        console.log('💡 You need to get test SUI from the faucet first!');
      }
    }
  }
}

// Test XRP transfer to email
async function testXrpEmailTransfer() {
  console.log('\n🔶 Testing XRP Transfer to Email Address');
  console.log('=========================================');
  console.log(`📧 Recipient Email: ${TEST_CONFIG.recipientEmail}`);
  console.log(`💰 Amount: ${TEST_CONFIG.xrpAmount} XRP`);

  // First, generate a test keypair if needed
  console.log('\nGenerating test XRP keypair...');
  const keypairResponse = await makeApiCall('/xrpl/generate-keypair');

  if (keypairResponse) {
    console.log(`✅ Generated test address: ${keypairResponse.keypair.address}`);
    console.log(`   Private key: ${keypairResponse.keypair.privateKey}`);
    console.log(`   Current balance: ${keypairResponse.balance.balanceXRP} XRP`);

    // Use the generated private key for testing
    const testPrivateKey = keypairResponse.keypair.privateKey;

    console.log('\nNOTE: You need to fund this address with test XRP first!');
    console.log('Visit the XRPL EVM testnet faucet to get test XRP.');

    console.log('\n📤 Sending XRP to email address...');
    const transferData = {
      privateKey: testPrivateKey,
      recipientEmail: TEST_CONFIG.recipientEmail,
      amount: TEST_CONFIG.xrpAmount,
      senderName: TEST_CONFIG.senderName
    };

    const result = await makeApiCall('/xrpl/send', 'POST', transferData);

    if (result?.success) {
      console.log('✅ XRP Transfer Successful!');
      console.log(`   Transaction: ${result.transactionHash}`);
      console.log(`   New wallet created: ${result.walletCredentials?.address}`);
      console.log(`   SMS notification: ${result.notifications?.sms ? '✅ Sent' : '❌ Failed'}`);
      console.log(`   Email notification: ${result.notifications?.email ? '✅ Sent' : '❌ Failed'}`);
      console.log(`   Explorer: ${result.explorerUrl}`);
    } else {
      console.log('❌ Transfer failed:', result?.message || 'Unknown error');
      if (result?.needsFaucet) {
        console.log('💡 You need to get test XRP from the faucet first!');
      }
    }
  }
}

// Test both regular address and email transfers
async function testBothTransferTypes() {
  console.log('\n🔄 Testing Address vs Email Transfer Comparison');
  console.log('================================================');

  // Generate a test keypair
  const keypairResponse = await makeApiCall('/generate-keypair');
  if (!keypairResponse) return;

  const testPrivateKey = keypairResponse.keypair.privateKey;
  const testRecipientAddress = '0x5d90e6a9c2d7ccaa1dc3a99a6e780ebcc199bb999b26134195a328cb5df151cb';

  console.log('\n1️⃣ Testing regular wallet address transfer...');
  const addressTransfer = await makeApiCall('/send-sui', 'POST', {
    privateKey: testPrivateKey,
    recipientAddress: testRecipientAddress,
    amount: 1000000
  });

  console.log(`   Regular transfer: ${addressTransfer?.success ? '✅ Would succeed (if funded)' : '❌ Failed'}`);
  console.log(`   Wallet generated: ${addressTransfer?.walletGenerated ? 'Yes' : 'No'}`);

  console.log('\n2️⃣ Testing email address transfer...');
  const emailTransfer = await makeApiCall('/send-sui', 'POST', {
    privateKey: testPrivateKey,
    recipientEmail: 'test@example.com',
    amount: 1000000
  });

  console.log(`   Email transfer: ${emailTransfer?.success ? '✅ Would succeed (if funded)' : '❌ Failed'}`);
  console.log(`   Wallet generated: ${emailTransfer?.walletGenerated ? 'Yes' : 'No'}`);
  console.log(`   SMS notification: ${emailTransfer?.notifications?.sms ? '✅ Would be sent' : '❌ Not sent'}`);
  console.log(`   Email notification: ${emailTransfer?.notifications?.email ? '✅ Would be sent' : '❌ Not sent'}`);
}

// Main test runner
async function runTests() {
  console.log('🚀 Email-Based Crypto Transfer Test Suite');
  console.log('==========================================');
  console.log('This test suite demonstrates email-based transfers for SUI and XRP.');
  console.log('When an email is provided, a new wallet is generated and credentials');
  console.log('are sent to the recipient via email, with SMS notification to +15109773150.');

  // Check if API is running
  const healthCheck = await makeApiCall('/');
  if (!healthCheck) {
    console.error('\n❌ API server is not running!');
    console.error('Please start the server first: npm run dev');
    process.exit(1);
  }

  console.log('\n✅ API server is running');

  // Run tests
  await testSuiEmailTransfer();
  await testXrpEmailTransfer();
  await testBothTransferTypes();

  console.log('\n✅ All tests completed!');
  console.log('\n📝 Summary:');
  console.log('- Email-based transfers generate new wallets for recipients');
  console.log('- SMS notifications are sent to +15109773150 for manual email delivery');
  console.log('- Both SUI and XRP support email-based transfers');
  console.log('- Regular wallet addresses still work as before');
}

// Run the tests
runTests().catch(error => {
  console.error('❌ Test suite failed:', error);
  process.exit(1);
});