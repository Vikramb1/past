#!/bin/bash

echo "=========================================="
echo "   CRYPTO GIFTING TEST (Without Email)"
echo "=========================================="
echo ""
echo "Testing keypair generation and display..."
echo ""

# Generate a new keypair and display it
echo "Generating new wallet..."
RESPONSE=$(curl -s http://localhost:3000/test-email \
  -H "Content-Type: application/json" \
  -d '{"recipientEmail": "test@example.com", "senderName": "Crypto Gift"}')

# Extract the keypair information
ADDRESS=$(echo $RESPONSE | grep -o '"address":"[^"]*' | cut -d'"' -f4)
PUBLIC_KEY=$(echo $RESPONSE | grep -o '"publicKey":"[^"]*' | cut -d'"' -f4)
PRIVATE_KEY=$(echo $RESPONSE | grep -o '"privateKey":"[^"]*' | cut -d'"' -f4)

echo ""
echo "✅ NEW WALLET GENERATED SUCCESSFULLY!"
echo "======================================"
echo ""
echo "🏠 Wallet Address:"
echo "   $ADDRESS"
echo ""
echo "🔑 Private Key (KEEP SECRET!):"
echo "   $PRIVATE_KEY"
echo ""
echo "📊 Public Key:"
echo "   $PUBLIC_KEY"
echo ""
echo "🌐 View on Explorer:"
echo "   https://testnet.suivision.xyz/account/$ADDRESS"
echo ""
echo "======================================"
echo ""
echo "📋 INSTRUCTIONS FOR RECIPIENT:"
echo "1. Save the private key securely"
echo "2. Download a SUI wallet (Sui Wallet, Ethos, or Martian)"
echo "3. Import wallet using the private key"
echo "4. Your crypto will be available!"
echo ""
echo "⚠️  NEVER share your private key with anyone!"
echo ""