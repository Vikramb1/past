import express, { Request, Response } from 'express';
import { SuiClient, getFullnodeUrl } from '@mysten/sui/client';
import { Transaction } from '@mysten/sui/transactions';
import { Ed25519Keypair } from '@mysten/sui/keypairs/ed25519';
import { fromB64, toB64 } from '@mysten/sui/utils';
import { getFaucetHost, requestSuiFromFaucetV1 } from '@mysten/sui/faucet';
import { sendCryptoGiftEmail, verifyEmailConfig } from './emailService';
import {
    generateXRPLKeypair,
    checkXRPLBalance,
    sendXRPL,
    requestXRPLFromFaucet,
    giftXRPL
} from './xrplService';
import { sendSuiEnhanced, sendXrpEnhanced, isEmail } from './enhancedTransfers';

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
const PORT = 3001;

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

// Send SUI using a private key (supports both wallet addresses and email addresses)
app.post('/send-sui', async (req: Request, res: Response) => {
    try {
        const { privateKey, recipientAddress, recipientEmail, amount, senderName } = req.body;

        if (!privateKey) {
            return res.status(400).json({
                error: 'Private key is required',
                message: 'Please provide a private key (hex or base64 format)'
            });
        }

        // Accept either recipientAddress or recipientEmail
        const recipient = recipientAddress || recipientEmail;
        if (!recipient) {
            return res.status(400).json({
                error: 'Recipient is required',
                message: 'Please provide either a recipient address or email'
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

        // Check if recipient is an email
        if (isEmail(recipient)) {
            console.log(`📧 Processing email-based SUI transfer to ${recipient}`);
            const sendResult = await sendSuiEnhanced(keypair, recipient, finalAmount, senderName);
            res.json(sendResult);
        } else {
            // Regular wallet address transfer
            const sendResult = await sendSui(keypair, recipient, finalAmount);
            res.json(sendResult);
        }
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

// XRPL EVM Sidechain Endpoints

// Generate a new XRPL EVM keypair
app.get('/xrpl/generate-keypair', async (req: Request, res: Response) => {
    try {
        const keypair = generateXRPLKeypair();
        const balance = await checkXRPLBalance(keypair.address);

        res.json({
            keypair: {
                address: keypair.address,
                privateKey: keypair.privateKey,
                publicKey: keypair.publicKey,
                mnemonic: keypair.mnemonic
            },
            balance: balance,
            network: 'XRPL EVM Testnet',
            chainId: 1449000,
            message: 'New XRPL EVM keypair generated. You may need to get test XRP from a faucet.',
            explorerUrl: `https://explorer.testnet.xrplevm.org/address/${keypair.address}`,
            rpcUrl: 'https://rpc.testnet.xrplevm.org'
        });
    } catch (error: any) {
        console.error('Error generating XRPL keypair:', error);
        res.status(500).json({ error: 'Failed to generate XRPL keypair', details: error.message });
    }
});

// Send XRP on XRPL EVM Sidechain (supports both wallet addresses and email addresses)
app.post('/xrpl/send', async (req: Request, res: Response) => {
    try {
        const { privateKey, recipientAddress, recipientEmail, amount, senderName } = req.body;

        if (!privateKey) {
            return res.status(400).json({
                error: 'Private key is required',
                message: 'Please provide a private key (hex format starting with 0x)'
            });
        }

        // Accept either recipientAddress or recipientEmail
        const recipient = recipientAddress || recipientEmail;
        if (!recipient) {
            return res.status(400).json({
                error: 'Recipient is required',
                message: 'Please provide either a recipient address or email'
            });
        }

        const finalAmount = amount || '0.0001'; // Default 0.0001 XRP

        // Check if recipient is an email
        if (isEmail(recipient)) {
            console.log(`📧 Processing email-based XRP transfer to ${recipient}`);
            const result = await sendXrpEnhanced(privateKey, recipient, finalAmount, senderName);
            res.json(result);
        } else {
            // Regular wallet address transfer
            const result = await sendXRPL(privateKey, recipient, finalAmount);
            res.json(result);
        }
    } catch (error: any) {
        console.error('Error sending XRP:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to send XRP',
            details: error.message
        });
    }
});

// Check XRPL EVM balance
app.get('/xrpl/balance/:address', async (req: Request, res: Response) => {
    try {
        const { address } = req.params;

        if (!address) {
            return res.status(400).json({ error: 'Address is required' });
        }

        const balance = await checkXRPLBalance(address);

        res.json({
            address: address,
            ...balance,
            network: 'XRPL EVM Testnet',
            chainId: 1449000,
            explorerUrl: `https://explorer.testnet.xrplevm.org/address/${address}`
        });
    } catch (error: any) {
        console.error('Error checking XRPL balance:', error);
        res.status(500).json({
            error: 'Failed to check balance',
            details: error.message
        });
    }
});

// Request XRP from faucet (if available)
app.post('/xrpl/faucet', async (req: Request, res: Response) => {
    try {
        const { address } = req.body;

        if (!address) {
            return res.status(400).json({
                error: 'Address is required',
                message: 'Please provide an XRPL EVM address to receive test XRP'
            });
        }

        const result = await requestXRPLFromFaucet(address);

        res.json({
            ...result,
            address: address,
            network: 'XRPL EVM Testnet',
            note: 'Faucet availability may vary. You can also try the official XRPL faucet.'
        });
    } catch (error: any) {
        console.error('Error requesting from XRPL faucet:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to request from faucet',
            details: error.message
        });
    }
});

// Gift XRP with email notification
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
                error: 'Sender private key is required',
                message: 'Please provide the private key to send from (hex format starting with 0x)'
            });
        }

        const emailToUse = recipientEmail || 'sanjay.amirthraj@gmail.com';
        const finalAmount = amount || '0.0001'; // Default 0.0001 XRP

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
                ? `The recipient has been emailed their wallet credentials at ${emailToUse}. They can now access their ${finalAmount} XRP!`
                : `Email failed to send. Please manually share the wallet credentials with the recipient.`
        });

    } catch (error: any) {
        console.error('Error in XRPL gift-crypto:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to complete XRPL crypto gift',
            details: error.message
        });
    }
});

// Add a root endpoint with API documentation
app.get('/', (req: Request, res: Response) => {
    res.json({
        name: "Multi-Chain Crypto API",
        networks: {
            sui: "SUI Testnet",
            xrpl: "XRPL EVM Sidechain Devnet"
        },
        endpoints: {
            sui: {
                "GET /generate-keypair": "Generate a new SUI keypair",
                "POST /send-sui": "Send SUI tokens",
                "POST /gift-crypto": "Gift SUI with email notification",
                "GET /balance/:address": "Check SUI balance",
                "POST /faucet": "Request test SUI from faucet",
                "GET /verify/:digest": "Verify SUI transaction"
            },
            xrpl: {
                "GET /xrpl/generate-keypair": "Generate a new XRPL EVM keypair",
                "POST /xrpl/send": "Send XRP on EVM sidechain",
                "POST /xrpl/gift-crypto": "Gift XRP with email notification",
                "GET /xrpl/balance/:address": "Check XRP balance",
                "POST /xrpl/faucet": "Request test XRP from faucet"
            }
        },
        examples: {
            sui: {
                sendSui: {
                    method: "POST",
                    endpoint: "/send-sui",
                    body: {
                        privateKey: "0x... or base64 or suiprivkey...",
                        recipientAddress: "0x... (or use recipientEmail instead)",
                        recipientEmail: "recipient@email.com (optional - use instead of address)",
                        amount: 1000000,
                        senderName: "Your Name (optional)"
                    }
                },
                giftCrypto: {
                    method: "POST",
                    endpoint: "/gift-crypto",
                    body: {
                        senderPrivateKey: "0x... or base64 or suiprivkey...",
                        recipientEmail: "recipient@email.com",
                        amount: 1000000,
                        senderName: "Your Name (optional)"
                    }
                }
            },
            xrpl: {
                sendXRP: {
                    method: "POST",
                    endpoint: "/xrpl/send",
                    body: {
                        privateKey: "0x...",
                        recipientAddress: "0x... (or use recipientEmail instead)",
                        recipientEmail: "recipient@email.com (optional - use instead of address)",
                        amount: "0.0001",
                        senderName: "Your Name (optional)"
                    }
                },
                giftXRP: {
                    method: "POST",
                    endpoint: "/xrpl/gift-crypto",
                    body: {
                        senderPrivateKey: "0x...",
                        recipientEmail: "recipient@email.com",
                        amount: "0.0001",
                        senderName: "Your Name (optional)"
                    }
                }
            }
        },
        notes: {
            sui: "1 SUI = 1,000,000,000 MIST. Default transfer: 0.001 SUI",
            xrpl: "XRPL EVM Sidechain uses XRP. Default transfer: 0.0001 XRP",
            email: "Emails default to sanjay.amirthraj@gmail.com if not provided"
        }
    });
});

// Start the server
app.listen(PORT, () => {
    console.log(`\n✨ Multi-Chain Crypto API Server Started ✨`);
    console.log(`============================================`);
    console.log(`Port: ${PORT}`);
    console.log(`\n🔷 SUI Testnet Endpoints:`);
    console.log(`  GET  http://localhost:${PORT}/                    - API documentation`);
    console.log(`  GET  http://localhost:${PORT}/generate-keypair    - Generate SUI keypair`);
    console.log(`  POST http://localhost:${PORT}/send-sui            - Send SUI tokens`);
    console.log(`  POST http://localhost:${PORT}/gift-crypto         - Gift SUI with email`);
    console.log(`  GET  http://localhost:${PORT}/balance/:address    - Check SUI balance`);
    console.log(`  POST http://localhost:${PORT}/faucet              - Request test SUI`);
    console.log(`  GET  http://localhost:${PORT}/verify/:digest      - Verify SUI transaction`);
    console.log(`\n🔶 XRPL EVM Sidechain Endpoints:`);
    console.log(`  GET  http://localhost:${PORT}/xrpl/generate-keypair - Generate XRPL EVM keypair`);
    console.log(`  POST http://localhost:${PORT}/xrpl/send            - Send XRP`);
    console.log(`  POST http://localhost:${PORT}/xrpl/gift-crypto     - Gift XRP with email`);
    console.log(`  GET  http://localhost:${PORT}/xrpl/balance/:address - Check XRP balance`);
    console.log(`  POST http://localhost:${PORT}/xrpl/faucet          - Request test XRP`);
    console.log(`============================================\n`);

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

// Export sendSui for use in other modules
export { sendSui };