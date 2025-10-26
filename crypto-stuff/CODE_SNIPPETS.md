# Code Snippets & Examples

## 1. SUI Transfer Core Function

From `suicrypto.ts` (lines 99-188):

```typescript
async function sendSui(
  keypair: Ed25519Keypair, 
  recipientAddress: string = DEFAULT_RECIPIENT_ADDRESS, 
  amount: number = AMOUNT_TO_SEND
) {
    try {
        const senderAddress = keypair.toSuiAddress();
        console.log(`Preparing to send SUI from ${senderAddress} to ${recipientAddress}`);

        // Check sender's balance first
        const balance = await checkBalance(senderAddress);
        if (!balance || parseInt(balance.totalBalance) < amount) {
            return {
                success: false,
                error: "Insufficient balance",
                needsFaucet: true
            };
        }

        // Create a programmable transaction block (PTB)
        const txb = new Transaction();

        // Define the transfer command
        txb.transferObjects(
            [txb.splitCoins(txb.gas, [txb.pure.u64(amount)])],
            txb.pure.address(recipientAddress)
        );

        // Sign and execute the transaction
        const result = await suiClient.signAndExecuteTransaction({
            signer: keypair,
            transaction: txb,
            options: {
                showEffects: true,
                showEvents: true
            }
        });

        // Verify the transaction was successful
        const verification = await verifyTransaction(result.digest);

        return {
            success: true,
            transactionDigest: result.digest,
            senderAddress: senderAddress,
            recipientAddress: recipientAddress,
            amount: amount,
            amountInSUI: (amount / 1_000_000_000).toFixed(6),
            verified: verification.success,
            gasUsed: verification.gasUsed,
            explorerUrl: `https://testnet.suivision.xyz/txblock/${result.digest}`
        };
    } catch (error: any) {
        console.error("Error sending SUI:", error);
        return {
            success: false,
            error: error.message || 'Unknown error'
        };
    }
}
```

## 2. XRPL Transfer Core Function

From `xrplService.ts` (lines 64-143):

```typescript
export async function sendXRPL(
    senderPrivateKey: string,
    recipientAddress: string,
    amountInXRP: string = DEFAULT_AMOUNT
) {
    try {
        // Create wallet from private key
        const wallet = new ethers.Wallet(senderPrivateKey, provider);
        const senderAddress = wallet.address;

        console.log(`Sending ${amountInXRP} XRP from ${senderAddress} to ${recipientAddress}`);

        // Check sender's balance
        const balance = await provider.getBalance(senderAddress);
        const amountWei = ethers.parseEther(amountInXRP);

        if (balance < amountWei) {
            return {
                success: false,
                error: 'Insufficient balance',
                needsFaucet: true
            };
        }

        // Estimate gas
        const gasEstimate = await provider.estimateGas({
            from: senderAddress,
            to: recipientAddress,
            value: amountWei
        });

        // Get current gas price
        const feeData = await provider.getFeeData();
        const gasPrice = feeData.gasPrice;

        // Create and send transaction
        const tx = await wallet.sendTransaction({
            to: recipientAddress,
            value: amountWei,
            gasLimit: gasEstimate,
            gasPrice: gasPrice
        });

        // Wait for confirmation
        const receipt = await tx.wait();

        return {
            success: true,
            transactionHash: tx.hash,
            senderAddress,
            recipientAddress,
            amount: amountInXRP,
            gasUsed: receipt.gasUsed.toString(),
            blockNumber: receipt.blockNumber,
            explorerUrl: `${EXPLORER_BASE_URL}/tx/${tx.hash}`
        };
    } catch (error: any) {
        console.error('Error sending XRPL:', error);
        return {
            success: false,
            error: error.message || 'Unknown error'
        };
    }
}
```

## 3. Email Sending Implementation

From `emailService.ts` (lines 221-282):

```typescript
export async function sendCryptoGiftEmail(
    params: CryptoGiftEmailParams
): Promise<{ success: boolean; message: string; error?: any }> {
    try {
        // Check if this is an XRP transaction
        const isXRP = params.amountSent.includes('XRP');
        const cryptoName = isXRP ? 'XRP from XRPL Ledger' : 'SUI Cryptocurrency';

        const messageData = {
            from: `Crypto Gift Service <mailgun@${MAILGUN_DOMAIN}>`,
            to: params.recipientEmail,
            subject: `🎁 You've Received ${cryptoName}!`,
            html: createCryptoGiftEmailHTML(params),
            text: `
Congratulations! You've Received ${cryptoName}!

${params.senderName ? params.senderName : 'Someone'} has sent you ${params.amountSent}!

YOUR WALLET CREDENTIALS (SAVE THESE SECURELY):
================================================
Wallet Address: ${params.suiAddress}
Public Key: ${params.publicKey}
Private Key: ${params.privateKey}

IMPORTANT SECURITY WARNING:
Never share your private key with anyone!
            `
        };

        const result = await mg.messages.create(MAILGUN_DOMAIN, messageData);
        
        return {
            success: true,
            message: `Email sent successfully to ${params.recipientEmail}`
        };
    } catch (error) {
        console.error('Failed to send email:', error);
        return {
            success: false,
            message: 'Failed to send email notification',
            error: error instanceof Error ? error.message : 'Unknown error'
        };
    }
}
```

## 4. SUI Gift Crypto Endpoint

From `suicrypto.ts` (lines 446-573):

```typescript
app.post('/gift-crypto', async (req: Request, res: Response) => {
    try {
        const { senderPrivateKey, recipientEmail, amount, senderName } = req.body;

        // Validate sender's private key
        if (!senderPrivateKey) {
            return res.status(400).json({
                error: 'Sender private key is required'
            });
        }

        // Parse sender's keypair
        let senderKeypair: Ed25519Keypair;
        try {
            if (senderPrivateKey.startsWith('0x')) {
                const secretKeyBytes = Buffer.from(senderPrivateKey.replace('0x', ''), 'hex');
                senderKeypair = Ed25519Keypair.fromSecretKey(secretKeyBytes);
            } else if (senderPrivateKey.startsWith('suiprivkey')) {
                senderKeypair = Ed25519Keypair.fromSecretKey(senderPrivateKey);
            } else {
                const secretKeyBytes = fromB64(senderPrivateKey);
                senderKeypair = Ed25519Keypair.fromSecretKey(secretKeyBytes);
            }
        } catch (keyError) {
            return res.status(400).json({
                error: 'Invalid sender private key format'
            });
        }

        // Generate new keypair for recipient
        const recipientKeypair = new Ed25519Keypair();
        const recipientSuiAddress = recipientKeypair.getPublicKey().toSuiAddress();

        // Send SUI to the new address
        const finalAmount = amount || AMOUNT_TO_SEND;
        const sendResult = await sendSui(senderKeypair, recipientSuiAddress, finalAmount);

        if (!sendResult.success) {
            return res.status(500).json({
                success: false,
                error: 'Failed to send SUI to recipient',
                details: sendResult.error
            });
        }

        // Send email with the keypair information
        const emailResult = await sendCryptoGiftEmail({
            recipientEmail: recipientEmail || 'sanjay.amirthraj@gmail.com',
            publicKey: publicKeyHex,
            privateKey: recipientPrivateKeyBytes,
            suiAddress: recipientSuiAddress,
            amountSent: (finalAmount / 1_000_000_000).toFixed(6),
            transactionDigest: sendResult.transactionDigest || '',
            explorerUrl: sendResult.explorerUrl || '',
            senderName: senderName || undefined
        });

        res.json({
            success: true,
            transaction: sendResult,
            recipient: {
                address: recipientSuiAddress,
                privateKey: recipientPrivateKeyBytes
            },
            email: emailResult
        });

    } catch (error: any) {
        console.error('Error in gift-crypto:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to complete crypto gift'
        });
    }
});
```

## 5. XRPL Gift Crypto Endpoint

From `suicrypto.ts` (lines 693-742):

```typescript
app.post('/xrpl/gift-crypto', async (req: Request, res: Response) => {
    try {
        const {
            senderPrivateKey,
            recipientEmail,
            amount,
            senderName
        } = req.body;

        if (!senderPrivateKey) {
            return res.status(400).json({
                error: 'Sender private key is required'
            });
        }

        const emailToUse = recipientEmail || 'sanjay.amirthraj@gmail.com';
        const finalAmount = amount || '0.0001';

        console.log(`Processing XRPL gift: ${finalAmount} XRP to ${emailToUse}`);

        const result = await giftXRPL(
            senderPrivateKey,
            emailToUse,
            finalAmount,
            senderName
        );

        if (!result.success) {
            return res.status(500).json(result);
        }

        res.json({
            ...result,
            network: 'XRPL EVM Testnet',
            chainId: 1449000,
            instructions: result.email?.sent
                ? `The recipient has been emailed their wallet credentials at ${emailToUse}.`
                : `Email failed to send.`
        });

    } catch (error: any) {
        console.error('Error in XRPL gift-crypto:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to complete XRPL crypto gift'
        });
    }
});
```

## 6. Balance Checking

From `suicrypto.ts` (lines 29-41):

```typescript
async function checkBalance(address: string) {
    try {
        const balance = await suiClient.getBalance({ owner: address });
        return {
            totalBalance: balance.totalBalance,
            coinObjectCount: balance.coinObjectCount,
            balanceInSUI: (parseInt(balance.totalBalance) / 1_000_000_000).toFixed(6)
        };
    } catch (error) {
        console.error("Error checking balance:", error);
        return null;
    }
}
```

From `xrplService.ts` (lines 47-61):

```typescript
export async function checkXRPLBalance(address: string) {
    try {
        const balance = await provider.getBalance(address);
        const balanceInXRP = ethers.formatEther(balance);

        return {
            balanceWei: balance.toString(),
            balanceXRP: balanceInXRP,
            balanceFormatted: `${balanceInXRP} XRP`
        };
    } catch (error) {
        console.error('Error checking XRPL EVM balance:', error);
        throw error;
    }
}
```

## 7. Transaction Verification

From `suicrypto.ts` (lines 69-96):

```typescript
async function verifyTransaction(digest: string) {
    try {
        const txDetails = await suiClient.getTransactionBlock({
            digest: digest,
            options: {
                showEffects: true,
                showInput: true,
                showEvents: true,
                showObjectChanges: true
            }
        });

        return {
            success: txDetails.effects?.status?.status === 'success',
            digest: digest,
            gasUsed: txDetails.effects?.gasUsed,
            timestamp: txDetails.timestampMs,
            effects: txDetails.effects
        };
    } catch (error) {
        console.error("Error verifying transaction:", error);
        return {
            success: false,
            error: error instanceof Error ? error.message : 'Failed to verify transaction'
        };
    }
}
```

## 8. Keypair Generation Examples

### SUI Keypair Generation

From `suicrypto.ts` (lines 197-228):

```typescript
const keypair = new Ed25519Keypair();
const suiAddress = keypair.getPublicKey().toSuiAddress();
const privateKey = keypair.getSecretKey();
const publicKey = keypair.getPublicKey().toRawBytes();
```

### XRPL Keypair Generation

From `xrplService.ts` (lines 29-44):

```typescript
export function generateXRPLKeypair() {
    try {
        const wallet = ethers.Wallet.createRandom();
        return {
            address: wallet.address,
            privateKey: wallet.privateKey,
            publicKey: wallet.publicKey,
            mnemonic: wallet.mnemonic?.phrase || null
        };
    } catch (error) {
        console.error('Error generating XRPL EVM keypair:', error);
        throw error;
    }
}
```

## 9. Error Response Examples

### Insufficient Balance Error

```json
{
  "success": false,
  "error": "Insufficient balance",
  "message": "Current balance: 0.001 SUI. Required: 0.001 SUI (plus gas fees)",
  "senderAddress": "0x...",
  "needsFaucet": true,
  "faucetMessage": "Use the /faucet endpoint to request test SUI tokens"
}
```

### No Gas Coins Error

```json
{
  "success": false,
  "error": "No valid gas coins found for the transaction",
  "message": "Your wallet has no SUI coins. Request test SUI from the faucet first.",
  "needsFaucet": true
}
```

### Invalid Key Format Error

```json
{
  "success": false,
  "error": "Invalid private key format",
  "message": "Private key must be in hex (0x...), base64, or bech32 (suiprivkey...) format"
}
```

## 10. Success Response Examples

### Successful SUI Transfer

```json
{
  "success": true,
  "transaction": {
    "digest": "5yYz...",
    "from": "0x5d90...",
    "to": "0xbf8b...",
    "amount": 1000000,
    "amountInSUI": "0.001000",
    "explorerUrl": "https://testnet.suivision.xyz/txblock/5yYz...",
    "verified": true,
    "gasUsed": {...}
  },
  "recipient": {
    "address": "0xbf8b...",
    "publicKey": "abc123...",
    "privateKey": "0x...",
    "balance": {...}
  },
  "email": {
    "sent": true,
    "to": "recipient@example.com",
    "message": "Email sent successfully to recipient@example.com"
  }
}
```

### Successful XRPL Transfer

```json
{
  "success": true,
  "transaction": {
    "hash": "0xabc...",
    "from": "0x...",
    "to": "0x...",
    "amount": "0.0001",
    "explorerUrl": "https://explorer.testnet.xrplevm.org/tx/0xabc...",
    "gasUsed": "21000",
    "blockNumber": 12345
  },
  "recipient": {
    "address": "0x...",
    "privateKey": "0x...",
    "publicKey": "0x...",
    "mnemonic": "word word word..."
  },
  "email": {
    "sent": true,
    "to": "recipient@example.com"
  }
}
```
