#!/bin/bash

# Quick script to send SUI from the funded wallet

echo "=========================================="
echo "Quick SUI Transfer Script"
echo "=========================================="
echo ""
echo "Sending 0.0001 SUI from funded wallet..."
echo ""

# Send 0.0001 SUI (100,000 MIST) from funded wallet to your wallet
curl -X POST http://localhost:3000/send-sui \
  -H "Content-Type: application/json" \
  -d '{
    "privateKey": "suiprivkey1qrdkvfpf9ksrsh8pwayg6n8vgk5n89087fy05u9uavvwsd6egv5ezxt843t",
    "recipientAddress": "0xbf8ba70997c705101fa3bbd478a6c87e884a34196408a08c40d90f0b5ae59511",
    "amount": 100000
  }' | python -m json.tool

echo ""
echo "=========================================="
echo "Transaction complete!"
echo "=========================================="