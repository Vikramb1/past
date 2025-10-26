# Multi-Chain Cryptocurrency Support - Implementation Complete! 🎉

## Overview

The face recognition payment system now supports **both SUI and XRPL (XRP) cryptocurrencies** with voice-controlled payment selection!

## What's New

### Supported Chains
- ✅ **SUI** (Sui Network Testnet)
- ✅ **XRPL** (XRPL EVM Sidechain Testnet)

### Voice Commands

All of the following voice commands now work:

#### SUI Commands
- "send 0.0001 SUI"
- "send 0.5 SUI"
- "send 0.0001 of SUI"
- "send five SUI"

#### XRPL Commands
- "send 0.0001 XRPL"
- "send 0.0001 XRP"
- "send 0.0001 of XRPL"
- "send 0.0001 of XRP"
- "send point five XRP"

## Implementation Details

### Files Modified

#### 1. `config.py`
**Added:**
- `DEFAULT_PAYMENT_AMOUNT_XRPL = 0.0001`
- `XRPL_FUNDED_WALLET_PRIVATE_KEY` 
- `XRPL_FUNDED_WALLET_PUBLIC_KEY`

#### 2. `amount_parser.py`
**Updated:**
- `parse_amount()` now returns `(amount, currency, display_text)` tuple
- Added XRPL/XRP detection in regex patterns
- Updated Ollama prompts to extract both amount and currency
- Added `amount_to_wei()` method for XRPL conversion
- `validate_amount()` now handles both currencies

**Key Changes:**
```python
# OLD
def parse_amount(text: str) -> Optional[float]:
    return amount

# NEW  
def parse_amount(text: str) -> Tuple[Optional[float], str, str]:
    return amount, currency, display_text
```

#### 3. `crypto_payment.py`
**Updated:**
- `send_payment()` now routes to correct blockchain based on currency
- Added `_send_sui_payment()` method
- Added `_send_xrpl_payment()` method
- Both methods call appropriate endpoints (`/gift-crypto` or `/xrpl/gift-crypto`)

**Key Changes:**
```python
# NEW routing logic
def send_payment(self, amount: float = None, currency: str = 'SUI') -> Dict:
    if currency == 'XRPL':
        return self._send_xrpl_payment(amount)
    else:
        return self._send_sui_payment(amount)
```

#### 4. `transaction_logger.py`
**Updated:**
- CSV headers now include `currency` field
- `log_transaction()` accepts `currency` parameter
- `get_total_sent()` returns totals per currency: `{'SUI': X, 'XRPL': Y}`
- Backwards compatible with old transaction format

#### 5. `main.py`
**Updated:**
- Amount parsing extracts currency and display text
- Amount preview stores currency information
- Payment trigger passes currency to async handler
- Display shows correct currency label
- Transaction stats display both SUI and XRPL totals

### Server Endpoints

#### SUI
- **Endpoint:** `POST http://localhost:3001/gift-crypto`
- **Payload:**
```json
{
  "senderPrivateKey": "sui private key",
  "recipientEmail": "recipient@email.com",
  "amount": 100000,
  "senderName": "Face Recognition Payment System"
}
```

#### XRPL
- **Endpoint:** `POST http://localhost:3001/xrpl/gift-crypto`
- **Payload:**
```json
{
  "senderPrivateKey": "xrpl private key",
  "recipientEmail": "recipient@email.com",
  "amount": "0.0001",
  "senderName": "Face Recognition Payment System"
}
```

## Configuration

### Default Amounts
```python
DEFAULT_PAYMENT_AMOUNT_SUI = 0.0001   # SUI
DEFAULT_PAYMENT_AMOUNT_XRPL = 0.0001  # XRPL/XRP
```

### Wallet Keys
```python
# SUI
FUNDED_WALLET_PRIVATE_KEY = "suiprivkey1qrdkvfpf9..."

# XRPL
XRPL_FUNDED_WALLET_PRIVATE_KEY = "2fa8efe237294d..."
XRPL_FUNDED_WALLET_PUBLIC_KEY = "0x60d6252fC31177B..."
```

### Recipient
```python
RECIPIENT_EMAIL = "sanjay.amirthraj@gmail.com"  # Same for both chains
SENDER_NAME = "Face Recognition Payment System"
```

## How It Works

### Flow Diagram

```
1. User speaks: "send 0.0001 XRPL"
   ↓
2. Deepgram transcribes audio
   ↓
3. AmountParser detects:
   - amount: 0.0001
   - currency: 'XRPL'
   - display_text: 'XRPL'
   ↓
4. System validates amount
   ↓
5. Preview shown: "Sending: 0.0001 XRPL"
   ↓
6. User holds snap gesture for 2 seconds
   ↓
7. CryptoPaymentHandler routes to XRPL endpoint
   ↓
8. Server generates new XRPL wallet
   ↓
9. Sends XRPL to new wallet
   ↓
10. Emails recipient with wallet credentials
   ↓
11. Transaction logged with currency type
   ↓
12. Success message displayed
```

### Display Features

**Amount Preview (Top Right):**
- Shows parsed amount and currency
- Displays for 2 seconds before sending
- Format: `"Sending: 0.0001 XRPL"` or `"Sending: 0.5 SUI"`

**Transaction Status (Top Center):**
- Sending: `"Sending 0.0001 XRPL..."`
- Success: `"Sent 0.0001 XRPL!"`
- Failure: `"Payment failed: [error]"`

## Testing

### Test SUI Payment

1. Start the system:
```bash
cd /Users/vikra/past/face_recognition
python main.py
```

2. Say: **"send 0.0001 SUI"**

3. Hold snap gesture for 2+ seconds

4. Expected Output:
```
💭 Parsing: 'send 0.0001 SUI'
✅ Regex parsed: 0.0001 SUI
💰 Amount validated: 0.0001 SUI
💰 Payment triggered by 2.1s snap hold!
💸 Sending 0.0001 SUI
✅ SUI crypto gift successful!
   Transaction: [digest]
   New wallet: [address]
```

### Test XRPL Payment

1. Say: **"send 0.0001 XRPL"** or **"send 0.0001 XRP"**

2. Hold snap gesture for 2+ seconds

3. Expected Output:
```
💭 Parsing: 'send 0.0001 XRPL'
✅ Regex parsed: 0.0001 XRPL
💰 Amount validated: 0.0001 XRPL
💰 Payment triggered by 2.1s snap hold!
💸 Sending 0.0001 XRPL
✅ XRPL crypto gift successful!
   Transaction: [hash]
   New wallet: [address]
```

## Transaction Logging

Transactions are logged to:
- **CSV:** `logs/transactions.csv`
- **JSON:** `logs/transactions.json`

### CSV Format
```csv
timestamp,datetime,currency,amount,transaction_digest,recipient_address,recipient_email,sender_name,explorer_url,status
1729901234,2025-10-25T12:34:56,SUI,0.0001,Ab12Cd34...,0x5d90...,email@example.com,System,https://...,success
1729901456,2025-10-25T12:37:36,XRPL,0.0001,0xef56...,0x60d6...,email@example.com,System,https://...,success
```

### JSON Format
```json
[
  {
    "timestamp": 1729901234,
    "datetime": "2025-10-25T12:34:56",
    "currency": "SUI",
    "amount": 0.0001,
    "transaction_digest": "Ab12Cd34...",
    "recipient": {
      "address": "0x5d90...",
      "email": "email@example.com"
    },
    "sender_name": "System",
    "explorer_url": "https://...",
    "status": "success"
  },
  {
    "timestamp": 1729901456,
    "datetime": "2025-10-25T12:37:36",
    "currency": "XRPL",
    "amount": 0.0001,
    "transaction_digest": "0xef56...",
    ...
  }
]
```

### Statistics Display

When you exit the system (press 'q'), you'll see:

```
=== Transaction Statistics ===
Total SUI sent: 0.0005 SUI
Total XRPL sent: 0.0002 XRPL
Transaction log: logs/transactions.csv
```

## Currency Detection Logic

### Regex Patterns (Fastest)

**XRPL Patterns (checked first):**
```python
r'(?:send\s+)?(\d+\.?\d*)\s*(?:of\s+)?xrpl\b'  # "send 0.5 XRPL" or "send 0.5 of XRPL"
r'(?:send\s+)?(\d+\.?\d*)\s*(?:of\s+)?xrp\b'   # "send 0.5 XRP" or "send 0.5 of XRP"
```

**SUI Patterns:**
```python
r'(?:send\s+)?(\d+\.?\d*)\s*(?:of\s+)?sui\b'  # "send 0.5 SUI" or "send 0.5 of SUI"
```

### Ollama LLM (Fallback)

If regex doesn't match, Ollama (llama3.2) parses the text:

**Prompt:**
```
Extract the cryptocurrency amount and type from this text. 
Return the amount and currency type.

Examples:
- "send 0.5 SUI" -> 0.5 SUI
- "send five XRP" -> 5 XRP
- "transfer 0.0001 XRPL" -> 0.0001 XRPL
- "send one point five SUI" -> 1.5 SUI

Text: "[user speech]"

Response (amount and currency):
```

## Validation Rules

### Amount Validation (Both Currencies)
- ❌ **Negative amounts:** Rejected
- ❌ **Zero amounts:** Rejected
- ❌ **Too large (>1000):** Rejected for safety
- ❌ **Too small (<0.00001):** Rejected
- ✅ **Valid range:** 0.00001 to 1000

### Default Behavior
- If no amount detected → Use default (0.0001)
- If no currency detected → Default to SUI
- Preserve original spoken text for display ("XRP" vs "XRPL")

## Backwards Compatibility

✅ **Fully backward compatible**

- Old transaction logs still work
- `get_total_sent()` handles old format with nested `{mist, sui}` structure
- Defaults to SUI if no currency specified
- Old code calling without currency parameter still works

## Error Handling

### Server Not Ready
```python
{
  'success': False,
  'message': 'Server not ready',
  'error': 'Crypto server is still starting up'
}
```

### Invalid Amount
```python
{
  'success': False,
  'message': 'Amount too large: 2000 SUI (max: 1000)',
  'currency': 'SUI'
}
```

### Transaction Failed
```python
{
  'success': False,
  'currency': 'XRPL',
  'message': 'Insufficient balance',
  'error': 'Current balance: 0 XRP. Required: 0.5 XRP'
}
```

## Troubleshooting

### Problem: Parser only detects SUI
**Solution:** Make sure you say "XRPL" or "XRP" clearly

### Problem: Wrong currency detected
**Solution:** Check transcription at bottom of screen to verify Deepgram heard correctly

### Problem: Transaction fails for XRPL
**Solution:** Check that XRPL wallet has funds in the testnet

### Problem: Email not received
**Solution:** Check spam folder, verify `RECIPIENT_EMAIL` in config

## Summary

🎉 **Multi-chain support is complete!**

✅ Voice-controlled payments for both SUI and XRPL
✅ Automatic currency detection from speech
✅ Separate transaction logging per currency
✅ Display shows correct currency labels
✅ Backward compatible with existing code
✅ Comprehensive error handling

Just speak the currency you want to send, and the system handles the rest! 🚀

