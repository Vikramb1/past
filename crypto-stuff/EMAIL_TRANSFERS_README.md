# Email-Based Crypto Transfers

## Overview
The crypto transfer system now supports sending SUI and XRP to email addresses in addition to wallet addresses. When an email is provided as the recipient, the system automatically:

1. **Generates a new wallet** for the recipient
2. **Sends the crypto** to the newly generated wallet
3. **Sends SMS notification** to +15109773150 requesting email delivery
4. **Sends email** with wallet credentials to the recipient

## Features

### 🔷 SUI Email Transfers
- Endpoint: `POST /send-sui`
- Accepts either `recipientAddress` or `recipientEmail`
- Generates Ed25519 keypair for email recipients
- Sends wallet credentials via email and SMS notification

### 🔶 XRP Email Transfers
- Endpoint: `POST /xrpl/send`
- Accepts either `recipientAddress` or `recipientEmail`
- Generates Ethereum-compatible keypair for email recipients
- Sends wallet credentials via email and SMS notification

## API Usage

### Send SUI to Email Address
```bash
curl -X POST http://localhost:3001/send-sui \
  -H "Content-Type: application/json" \
  -d '{
    "privateKey": "0xYOUR_PRIVATE_KEY",
    "recipientEmail": "recipient@example.com",
    "amount": 1000000,
    "senderName": "John Doe"
  }'
```

### Send XRP to Email Address
```bash
curl -X POST http://localhost:3001/xrpl/send \
  -H "Content-Type: application/json" \
  -d '{
    "privateKey": "0xYOUR_PRIVATE_KEY",
    "recipientEmail": "recipient@example.com",
    "amount": "0.0001",
    "senderName": "John Doe"
  }'
```

### Response Format (Email Transfer)
```json
{
  "success": true,
  "transactionDigest": "TRANSACTION_HASH",
  "recipientEmail": "recipient@example.com",
  "walletGenerated": true,
  "walletCredentials": {
    "address": "0x...",
    "privateKey": "0x...",
    "publicKey": "0x..."
  },
  "notifications": {
    "sms": true,
    "email": true
  },
  "instructions": "SMS sent to +15109773150 to notify about sending wallet credentials to recipient@example.com"
}
```

## SMS Integration

### iMessage Handler
- Sends notifications to **+15109773150**
- Uses macOS iMessage via AppleScript
- Message format includes:
  - Crypto type (SUI/XRP)
  - Recipient email
  - Amount transferred
  - Generated wallet credentials

### SMS Message Format
```
Crypto Transfer Request:
Type: SUI
Recipient Email: recipient@example.com
Amount: 0.001 SUI

Please send an email to recipient@example.com with the following wallet credentials:

Private Key: 0x...
Public Key: 0x...

This wallet has been created for the SUI transfer.
```

## Email Service

### Email Contents
Recipients receive an email with:
- Welcome message
- Amount of crypto received
- Wallet credentials (address, private key, public key)
- Instructions on how to access their funds
- Security warnings about private key storage
- Links to blockchain explorers

### Email Configuration
- Service: Mailgun
- Default recipient: sanjay.amirthraj@gmail.com (if not specified)
- HTML and plain text formats supported

## File Structure

```
crypto-stuff/
├── suicrypto.ts          # Main API server with updated endpoints
├── enhancedTransfers.ts  # Email-based transfer logic
├── smsService.ts         # SMS/iMessage notification service
├── emailService.ts       # Email delivery service
├── xrplService.ts        # XRP transfer functions
└── test-email-transfers.ts # Test suite for email transfers
```

## Testing

Run the test suite:
```bash
npx ts-node test-email-transfers.ts
```

This will test:
1. SUI transfers to email addresses
2. XRP transfers to email addresses
3. SMS notification delivery
4. Email credential delivery

## Important Notes

### Security Considerations
- **Private keys** are sent via email - use only for testnet/demo purposes
- Production systems should use more secure credential delivery methods
- SMS notifications go to a fixed number for manual email processing

### Network Requirements
- SUI Testnet: https://fullnode.testnet.sui.io
- XRPL EVM Testnet: https://rpc.testnet.xrplevm.org
- Requires macOS for iMessage integration

### Error Handling
- If email delivery fails, credentials are returned in API response
- SMS failures don't block the transfer
- Wallet generation failures prevent the transfer

## Migration from Address-Only Transfers

The system is **backward compatible**:
- Existing code using `recipientAddress` continues to work
- New code can use either `recipientAddress` or `recipientEmail`
- Both parameters cannot be used simultaneously

### Example Migration
```javascript
// Old way (still works)
await sendSui({
  privateKey: "0x...",
  recipientAddress: "0x...",
  amount: 1000000
});

// New way (with email)
await sendSui({
  privateKey: "0x...",
  recipientEmail: "recipient@example.com",
  amount: 1000000,
  senderName: "Sender Name"
});
```

## Troubleshooting

### SMS Not Sending
- Ensure macOS Messages app is configured
- Check that +15109773150 is a valid iMessage contact
- Verify AppleScript permissions are enabled

### Email Not Sending
- Check EMAIL_USER and EMAIL_PASSWORD environment variables
- Verify Mailgun API credentials
- Check recipient email validity

### Transfer Failures
- Ensure sufficient balance in sender wallet
- Verify network connectivity to blockchain nodes
- Check private key format (hex/base64/bech32)

## Future Enhancements

Potential improvements:
- [ ] Add Twilio SMS integration for non-macOS systems
- [ ] Implement secure key management service
- [ ] Add multi-signature wallet support
- [ ] Create web interface for email-based transfers
- [ ] Add QR code generation for wallet credentials
- [ ] Implement email verification before transfer