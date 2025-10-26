import { smsService } from './smsService';
import { Ed25519Keypair } from '@mysten/sui/keypairs/ed25519';

async function testSMSNotification() {
  try {
    console.log('📱 Testing SMS notification to sanjay.amirthraj@gmail.com\n');

    // Create a new wallet for the recipient
    const recipientKeypair = new Ed25519Keypair();
    const recipientPublicKey = recipientKeypair.getPublicKey().toSuiAddress();
    const recipientPrivateKey = recipientKeypair.getSecretKey();

    // Convert private key to hex string
    const privateKeyHex = Buffer.from(recipientPrivateKey).toString('hex');

    console.log('✨ Created wallet for recipient:');
    console.log('   Public Address:', recipientPublicKey);
    console.log('   Private Key (hex):', privateKeyHex);
    console.log('\n');

    // Send SMS notification with QR codes
    const success = await smsService.sendCryptoEmailNotification(
      'sanjay.amirthraj@gmail.com',
      'SUI',
      privateKeyHex,
      recipientPublicKey,
      '0.1' // Amount being sent
    );

    if (success) {
      console.log('✅ SMS notification sent successfully!');
      console.log('   Recipient will receive QR codes via iMessage');
      console.log('   Email: sanjay.amirthraj@gmail.com');
      console.log('\n📱 Wallet details sent:');
      console.log('   Private Key:', privateKeyHex);
      console.log('   Public Address:', recipientPublicKey);
    } else {
      console.log('❌ Failed to send SMS notification');
    }

  } catch (error) {
    console.error('❌ Error in test:', error);
  }
}

// Run the test
testSMSNotification().catch(console.error);