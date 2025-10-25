import * as dotenv from 'dotenv';
import * as path from 'path';

// Load environment variables from .env file
dotenv.config({ path: path.join(__dirname, '.env') });

const express = require('express');
import { Request, Response } from 'express';
import { SuiClient, getFullnodeUrl } from '@mysten/sui/client';
import { Transaction } from '@mysten/sui/transactions';
import { Ed25519Keypair } from '@mysten/sui/keypairs/ed25519';
import { fromB64, toB64 } from '@mysten/sui/utils';
import { getFaucetHost, requestSuiFromFaucetV1 } from '@mysten/sui/faucet';
import { sendCryptoGiftEmail, verifyEmailConfig } from './emailService';

// Configuration for testnet
const NETWORK = "testnet";
const DEFAULT_RECIPIENT_ADDRESS = "0x5d90e6a9c2d7ccaa1dc3a99a6e780ebcc199bb999b26134195a328cb5df151cb";
const AMOUNT_TO_SEND = 1000000; // 0.001 SUI (1 SUI = 1,000,000,000 MIST)

const suiClient = new SuiClient({ url: getFullnodeUrl(NETWORK) });

// Helper function to convert Uint8Array to a hex string for API response
function toHexString(bytes: Uint8Array): string {
    return Array.from(bytes).map(byte => byte.toString(16).padStart(2, '0')).join('');
}

// Function to check balance of an address
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

// Function to request SUI from testnet faucet
async function requestFromFaucet(address: string) {
    try {
        const faucetHost = getFaucetHost(NETWORK);
        const result = await requestSuiFromFaucetV1({
            host: faucetHost,
            recipient: address,
        });
        console.log("Faucet request successful:", result);
        return {
            success: true,
            message: "Successfully requested SUI from faucet",
            taskId: result.task,
            amount: "1 SUI"
        };
    } catch (error: any) {
        console.error("Faucet request failed:", error);
        return {
            success: false,
            error: error.message || "Failed to request from faucet",
            message: "Make sure you're on testnet and haven't exceeded rate limits"
        };
    }
}

// Function to verify transaction on chain
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
            sender: txDetails.transaction?.data?.sender,
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

// Function to send SUI using a keypair
async function sendSui(keypair: Ed25519Keypair, recipientAddress: string = DEFAULT_RECIPIENT_ADDRESS, amount: number = AMOUNT_TO_SEND) {
    try {
        const senderAddress = keypair.toSuiAddress();

        console.log(`Preparing to send SUI from ${senderAddress} to ${recipientAddress}`);

        // Check sender's balance first
        const balance = await checkBalance(senderAddress);
        if (!balance || parseInt(balance.totalBalance) < amount) {
            const currentBalance = balance ? balance.balanceInSUI : '0';
            return {
                success: false,
                error: "Insufficient balance",
                message: `Current balance: ${currentBalance} SUI. Required: ${(amount / 1_000_000_000).toFixed(6)} SUI (plus gas fees)`,
                senderAddress: senderAddress,
                needsFaucet: true,
                faucetMessage: "Use the /faucet endpoint to request test SUI tokens"
            };
        }

        // Check if there are any gas coins available
        if (balance.coinObjectCount === 0) {
            return {
                success: false,
                error: "No valid gas coins found for the transaction",
                message: "Your wallet has no SUI coins. Request test SUI from the faucet first.",
                senderAddress: senderAddress,
                needsFaucet: true,
                faucetMessage: "Use the /faucet endpoint to request test SUI tokens"
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

        console.log("Transaction result:", result);
        console.log("Transaction digest:", result.digest);

        // Verify the transaction was successful
        const verification = await verifyTransaction(result.digest);

        return {
            success: true,
            transactionDigest: result.digest,
            senderAddress: senderAddress,
            recipientAddress: recipientAddress,
            amount: amount,
            amountInSUI: (amount / 1_000_000_000).toFixed(6),
            message: "SUI sent and verified successfully",
            verified: verification.success,
            gasUsed: verification.gasUsed,
            explorerUrl: `https://testnet.suivision.xyz/txblock/${result.digest}`
        };
    } catch (error: any) {
        console.error("Error sending SUI:", error);

        // Handle specific error for no gas coins
        if (error.message?.includes("No valid gas coins") || error.message?.includes("gas coins")) {
            return {
                success: false,
                error: "No valid gas coins found for the transaction",
                message: "Your wallet has no SUI coins. Request test SUI from the faucet first.",
                needsFaucet: true,
                faucetMessage: "Use the /faucet endpoint to request test SUI tokens"
            };
        }

        return {
            success: false,
            error: error.message || 'Unknown error',
            message: "Failed to send SUI"
        };
    }
}

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());

// Generate a new Sui keypair
app.get('/generate-keypair', async (req: Request, res: Response) => {
    try {
        // Generate a new random keypair
        const keypair = new Ed25519Keypair();

        const privateKeyBytes = keypair.getSecretKey();
        const publicKeyBytes = keypair.getPublicKey().toRawBytes();
        const suiAddress = keypair.getPublicKey().toSuiAddress();

        const privateKeyB64 = toB64(new Uint8Array(Buffer.from(privateKeyBytes.replace('0x', ''), 'hex')));
        const publicKeyHex = toHexString(publicKeyBytes);

        // Check balance of the new address
        const balance = await checkBalance(suiAddress);

        res.json({
            keypair: {
                suiAddress: suiAddress,
                publicKey: publicKeyHex,
                privateKey: privateKeyBytes,
                privateKeyBase64: privateKeyB64,
            },
            balance: balance || { totalBalance: '0', balanceInSUI: '0' },
            network: NETWORK,
            message: "New keypair generated. Use /faucet endpoint to get test SUI tokens.",
            explorerUrl: `https://testnet.suivision.xyz/account/${suiAddress}`
        });
    } catch (error: any) {
        console.error('Error generating keypair:', error);
        res.status(500).json({ error: 'Failed to generate keypair', details: error.message });
    }
});

// Send SUI using a private key
app.post('/send-sui', async (req: Request, res: Response) => {
    try {
        const { privateKey, recipientAddress, amount } = req.body;

        if (!privateKey) {
            return res.status(400).json({
                error: 'Private key is required',
                message: 'Please provide a private key (hex or base64 format)'
            });
        }

        if (!recipientAddress) {
            return res.status(400).json({
                error: 'Recipient address is required'
            });
        }

        // Try to create keypair from the provided private key
        let keypair: Ed25519Keypair;

        try {
            if (privateKey.startsWith('0x')) {
                // Hex format
                const secretKeyBytes = Buffer.from(privateKey.replace('0x', ''), 'hex');
                keypair = Ed25519Keypair.fromSecretKey(secretKeyBytes);
            } else if (privateKey.startsWith('suiprivkey')) {
                // Bech32 format (new SUI format)
                keypair = Ed25519Keypair.fromSecretKey(privateKey);
            } else {
                // Try base64
                const secretKeyBytes = fromB64(privateKey);
                keypair = Ed25519Keypair.fromSecretKey(secretKeyBytes);
            }
        } catch (keyError) {
            return res.status(400).json({
                error: 'Invalid private key format',
                message: 'Private key must be in hex (0x...), base64, or bech32 (suiprivkey...) format'
            });
        }

        const finalAmount = amount || AMOUNT_TO_SEND;
        const sendResult = await sendSui(keypair, recipientAddress, finalAmount);

        res.json(sendResult);
    } catch (error: any) {
        console.error('Error sending SUI:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to send SUI',
            details: error.message
        });
    }
});

// Check balance of an address
app.get('/balance/:address', async (req: Request, res: Response) => {
    try {
        const { address } = req.params;

        if (!address) {
            return res.status(400).json({ error: 'Address is required' });
        }

        const balance = await checkBalance(address);

        if (!balance) {
            return res.status(500).json({ error: 'Failed to fetch balance' });
        }

        res.json({
            address: address,
            ...balance,
            network: NETWORK,
            explorerUrl: `https://testnet.suivision.xyz/account/${address}`
        });
    } catch (error: any) {
        console.error('Error checking balance:', error);
        res.status(500).json({
            error: 'Failed to check balance',
            details: error.message
        });
    }
});

// Request SUI from testnet faucet
app.post('/faucet', async (req: Request, res: Response) => {
    try {
        const { address } = req.body;

        if (!address) {
            return res.status(400).json({
                error: 'Address is required',
                message: 'Please provide a SUI address to receive test tokens'
            });
        }

        const result = await requestFromFaucet(address);

        if (result.success) {
            // Wait a bit for the faucet transaction to be processed
            setTimeout(async () => {
                const balance = await checkBalance(address);
                console.log('Balance after faucet request:', balance);
            }, 5000);
        }

        res.json({
            ...result,
            address: address,
            network: NETWORK,
            message: result.success
                ? "Test SUI requested successfully. Balance will be updated in a few seconds."
                : result.message
        });
    } catch (error: any) {
        console.error('Error requesting from faucet:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to request from faucet',
            details: error.message,
            message: 'Faucet may be rate limited. Try again later.'
        });
    }
});

// Verify a transaction
app.get('/verify/:digest', async (req: Request, res: Response) => {
    try {
        const { digest } = req.params;

        if (!digest) {
            return res.status(400).json({ error: 'Transaction digest is required' });
        }

        const verification = await verifyTransaction(digest);

        res.json({
            ...verification,
            explorerUrl: `https://testnet.suivision.xyz/txblock/${digest}`
        });
    } catch (error: any) {
        console.error('Error verifying transaction:', error);
        res.status(500).json({
            error: 'Failed to verify transaction',
            details: error.message
        });
    }
});

// Test email endpoint - generates keypair and sends test email without transaction
app.post('/test-email', async (req: Request, res: Response) => {
    try {
        const { recipientEmail, senderName } = req.body;

        // Use default email if none provided
        const emailToUse = recipientEmail || 'sanjay.amirthraj@gmail.com';

        // Generate new keypair for testing
        console.log('Generating test keypair...');
        const testKeypair = new Ed25519Keypair();

        const privateKeyBytes = testKeypair.getSecretKey();
        const publicKeyBytes = testKeypair.getPublicKey().toRawBytes();
        const suiAddress = testKeypair.getPublicKey().toSuiAddress();

        const privateKeyB64 = toB64(new Uint8Array(Buffer.from(privateKeyBytes.replace('0x', ''), 'hex')));
        const publicKeyHex = toHexString(publicKeyBytes);

        console.log(`Generated test address: ${suiAddress}`);

        // Prepare email parameters with test transaction details
        const emailParams = {
            recipientEmail: emailToUse,
            publicKey: publicKeyHex,
            privateKey: privateKeyBytes,
            suiAddress: suiAddress,
            amountSent: "0.001000",
            transactionDigest: "TEST_TRANSACTION_" + Date.now(),
            explorerUrl: `https://testnet.suivision.xyz/account/${suiAddress}`,
            senderName: senderName || "Test Sender"
        };

        // Send test email
        console.log(`Sending test email to ${emailToUse}...`);
        const emailResult = await sendCryptoGiftEmail(emailParams);

        res.json({
            success: true,
            message: 'Test email functionality',
            keypair: {
                address: suiAddress,
                publicKey: publicKeyHex,
                privateKey: privateKeyBytes,
                privateKeyBase64: privateKeyB64
            },
            email: {
                sent: emailResult.success,
                to: emailToUse,
                message: emailResult.message,
                error: emailResult.error
            },
            note: 'This is a TEST - no actual crypto was sent'
        });

    } catch (error: any) {
        console.error('Error in test-email:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to test email',
            details: error.message
        });
    }
});

// Gift crypto endpoint - generates new keypair for recipient and sends them the keys via email
app.post('/gift-crypto', async (req: Request, res: Response) => {
    try {
        const {
            senderPrivateKey,
            recipientEmail,
            amount,
            senderName
        } = req.body;

        // Use default email if none provided
        const emailToUse = recipientEmail || 'sanjay.amirthraj@gmail.com';

        // Validate sender's private key
        if (!senderPrivateKey) {
            return res.status(400).json({
                error: 'Sender private key is required',
                message: 'Please provide the private key to send from'
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
                error: 'Invalid sender private key format',
                message: 'Private key must be in hex (0x...), base64, or bech32 (suiprivkey...) format'
            });
        }

        // Generate new keypair for recipient
        console.log('Generating new keypair for recipient...');
        const recipientKeypair = new Ed25519Keypair();

        const recipientPrivateKeyBytes = recipientKeypair.getSecretKey();
        const recipientPublicKeyBytes = recipientKeypair.getPublicKey().toRawBytes();
        const recipientSuiAddress = recipientKeypair.getPublicKey().toSuiAddress();

        const recipientPrivateKeyB64 = toB64(new Uint8Array(Buffer.from(recipientPrivateKeyBytes.replace('0x', ''), 'hex')));
        const recipientPublicKeyHex = toHexString(recipientPublicKeyBytes);

        console.log(`Generated new address for recipient: ${recipientSuiAddress}`);

        // Send SUI to the new address
        const finalAmount = amount || AMOUNT_TO_SEND;
        console.log(`Sending ${(finalAmount / 1_000_000_000).toFixed(6)} SUI to recipient...`);

        const sendResult = await sendSui(senderKeypair, recipientSuiAddress, finalAmount);

        if (!sendResult.success) {
            return res.status(500).json({
                success: false,
                error: 'Failed to send SUI to recipient',
                details: sendResult.error,
                message: sendResult.message
            });
        }

        // Prepare email parameters
        const emailParams = {
            recipientEmail: emailToUse,
            publicKey: recipientPublicKeyHex,
            privateKey: recipientPrivateKeyBytes,
            suiAddress: recipientSuiAddress,
            amountSent: (finalAmount / 1_000_000_000).toFixed(6),
            transactionDigest: sendResult.transactionDigest || '',
            explorerUrl: sendResult.explorerUrl || `https://testnet.suivision.xyz/txblock/${sendResult.transactionDigest}`,
            senderName: senderName || undefined
        };

        // Send email with the keypair information
        console.log(`Sending email to ${emailToUse}...`);
        const emailResult = await sendCryptoGiftEmail(emailParams);

        // Check final balance of the new address
        const recipientBalance = await checkBalance(recipientSuiAddress);

        // Return comprehensive response
        res.json({
            success: true,
            message: `Successfully sent ${(finalAmount / 1_000_000_000).toFixed(6)} SUI as a gift!`,
            transaction: {
                digest: sendResult.transactionDigest,
                from: sendResult.senderAddress,
                to: recipientSuiAddress,
                amount: finalAmount,
                amountInSUI: (finalAmount / 1_000_000_000).toFixed(6),
                explorerUrl: sendResult.explorerUrl,
                verified: sendResult.verified,
                gasUsed: sendResult.gasUsed
            },
            recipient: {
                address: recipientSuiAddress,
                publicKey: recipientPublicKeyHex,
                privateKey: recipientPrivateKeyBytes,
                privateKeyBase64: recipientPrivateKeyB64,
                balance: recipientBalance || { totalBalance: '0', balanceInSUI: '0' }
            },
            email: {
                sent: emailResult.success,
                to: emailToUse,
                message: emailResult.message,
                error: emailResult.error
            },
            network: NETWORK,
            instructions: emailResult.success
                ? `The recipient has been emailed their wallet credentials at ${emailToUse}. They can now access their ${(finalAmount / 1_000_000_000).toFixed(6)} SUI!`
                : `Email failed to send. Please manually share these credentials with the recipient:\nAddress: ${recipientSuiAddress}\nPrivate Key: ${recipientPrivateKeyBytes}`
        });

    } catch (error: any) {
        console.error('Error in gift-crypto:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to complete crypto gift',
            details: error.message
        });
    }
});

// Add a root endpoint with API documentation
app.get('/', (req: Request, res: Response) => {
    res.json({
        name: "SUI Testnet API",
        network: NETWORK,
        endpoints: {
            "GET /": "API documentation",
            "GET /generate-keypair": "Generate a new SUI keypair",
            "POST /send-sui": "Send SUI tokens (requires privateKey, recipientAddress, and optional amount in request body)",
            "POST /gift-crypto": "Gift crypto to someone by generating a new wallet and emailing them the keys",
            "GET /balance/:address": "Check balance of a SUI address",
            "POST /faucet": "Request test SUI from faucet (requires address in request body)",
            "GET /verify/:digest": "Verify a transaction by its digest"
        },
        examples: {
            sendSui: {
                method: "POST",
                endpoint: "/send-sui",
                body: {
                    privateKey: "0x... or base64 or suiprivkey...",
                    recipientAddress: "0x...",
                    amount: 1000000
                }
            },
            giftCrypto: {
                method: "POST",
                endpoint: "/gift-crypto",
                body: {
                    senderPrivateKey: "0x... or base64 or suiprivkey...",
                    recipientEmail: "recipient@email.com (defaults to sanjay.amirthraj@gmail.com if not provided)",
                    amount: 1000000,
                    senderName: "Your Name (optional)"
                }
            },
            faucet: {
                method: "POST",
                endpoint: "/faucet",
                body: {
                    address: "0x..."
                }
            }
        },
        note: "1 SUI = 1,000,000,000 MIST. Default transfer amount is 0.001 SUI (1,000,000 MIST)"
    });
});

// Start the server
app.listen(PORT, () => {
    console.log(`\n✨ SUI Testnet API Server Started ✨`);
    console.log(`================================`);
    console.log(`Network: ${NETWORK}`);
    console.log(`Port: ${PORT}`);
    console.log(`\nAvailable endpoints:`);
    console.log(`  GET  http://localhost:${PORT}/                    - API documentation`);
    console.log(`  GET  http://localhost:${PORT}/generate-keypair    - Generate new keypair`);
    console.log(`  POST http://localhost:${PORT}/send-sui            - Send SUI tokens`);
    console.log(`  POST http://localhost:${PORT}/gift-crypto         - Gift crypto with email notification`);
    console.log(`  GET  http://localhost:${PORT}/balance/:address    - Check balance`);
    console.log(`  POST http://localhost:${PORT}/faucet              - Request test SUI`);
    console.log(`  GET  http://localhost:${PORT}/verify/:digest      - Verify transaction`);
    console.log(`================================\n`);

    // Check email configuration on startup
    verifyEmailConfig().then(isValid => {
        if (!isValid) {
            console.log('⚠️  Email configuration not set. Please configure EMAIL_USER and EMAIL_PASSWORD environment variables.');
            console.log('   For Gmail: Use an app-specific password, not your regular password.');
        } else {
            console.log('✅ Email service configured and ready.');
        }
    });
});