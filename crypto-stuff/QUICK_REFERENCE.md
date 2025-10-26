# Crypto-Stuff Quick Reference Guide

## File Structure
```
crypto-stuff/
├── suicrypto.ts              # Main Express server + SUI operations
├── xrplService.ts            # XRPL EVM service & functions  
├── emailService.ts           # Mailgun email functionality
├── test-gift-crypto.ts       # SUI gift test script
├── test-xrpl-gift.ts         # XRPL gift test script
├── send-from-funded.ts       # SUI transfer example
├── test-xrpl-funded.ts       # XRPL transfer example
├── package.json              # Dependencies
├── tsconfig.json             # TypeScript config
├── GMAIL_SETUP.md            # Email configuration guide
└── IMPLEMENTATION_ANALYSIS.md # Detailed analysis (NEW)
```

## Key Functions at a Glance

### SUI Functions
- `sendSui(keypair, recipientAddress, amount)` - Core transfer function
- `checkBalance(address)` - Check wallet balance
- `requestFromFaucet(address)` - Request test SUI
- `verifyTransaction(digest)` - Verify on-chain
- `sendCryptoGiftEmail(params)` - Send email with credentials

### XRPL Functions
- `generateXRPLKeypair()` - Create new keypair
- `sendXRPL(privateKey, recipientAddress, amount)` - Transfer XRP
- `checkXRPLBalance(address)` - Check balance
- `giftXRPL(privateKey, email, amount, senderName)` - Gift with email
- `sendXRPLGiftEmail(params)` - Send XRPL email

## Email Configuration
- **Service**: Mailgun (sandbox domain)
- **API Key**: Hardcoded in emailService.ts (SECURITY ISSUE)
- **From**: monkeyman20204@gmail.com
- **Features**: HTML + plain text, auto-detect SUI vs XRP, security warnings

## Transaction Flow (SUI)
```
POST /gift-crypto
  ├─ Validate sender private key
  ├─ Generate recipient keypair
  ├─ Call sendSui() to transfer
  ├─ Call sendCryptoGiftEmail()
  └─ Return transaction + email status
```

## Transaction Flow (XRPL)
```
POST /xrpl/gift-crypto
  ├─ Generate recipient keypair
  ├─ Call sendXRPL() to transfer
  ├─ Call sendXRPLGiftEmail()
  └─ Return transaction + email status
```

## Common Issues & Solutions

### "No valid gas coins"
- Need to request SUI from faucet first
- POST /faucet with your address

### Email not sending
- Check Mailgun credentials are valid
- Check recipient email format
- Email sends ASYNC (won't block transaction)

### Insufficient balance
- Use /balance/:address to check
- Request more from faucet if needed

### Private key format issues
- Supports: 0x..., base64, suiprivkey... (SUI)
- XRPL only: 0x... format

## Network Details

### SUI Testnet
- Explorer: https://testnet.suivision.xyz
- 1 SUI = 1,000,000,000 MIST
- Default send: 1,000,000 MIST (0.001 SUI)

### XRPL EVM Testnet
- RPC: https://rpc.testnet.xrplevm.org
- Chain ID: 1449000
- Explorer: https://explorer.testnet.xrplevm.org
- Default send: 0.0001 XRP

## API Port
- Default: 3001
- Can be changed in suicrypto.ts line 191

## Missing Features
- ❌ SMS messaging (not implemented)
- ❌ Authentication/API keys
- ❌ Rate limiting
- ❌ Database storage
- ❌ Webhook notifications

## Security Gaps
- Hardcoded Mailgun API key
- Private keys in email (necessary trade-off)
- No input validation
- No CORS protection

## Next Steps for Enhancement
1. Move credentials to environment variables
2. Add SMS capability via Twilio
3. Implement payment verification
4. Add rate limiting
5. Add database storage for transaction history
