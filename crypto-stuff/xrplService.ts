import { ethers } from 'ethers';
import { sendCryptoGiftEmail } from './emailService';

// XRPL EVM Sidechain Configuration (Testnet)
const XRPL_EVM_RPC_URL = 'https://rpc.testnet.xrplevm.org';
const CHAIN_ID = 1449000; // 0x161c28 - XRPL EVM Testnet Chain ID
const EXPLORER_BASE_URL = 'https://explorer.testnet.xrplevm.org';
const DEFAULT_AMOUNT = '0.0001'; // 0.0001 XRP

// Create provider for XRPL EVM Sidechain
const provider = new ethers.JsonRpcProvider(XRPL_EVM_RPC_URL, {
    name: 'XRPL EVM Testnet',
    chainId: CHAIN_ID
});

// Interface for XRPL gift email parameters
interface XRPLGiftEmailParams {
    recipientEmail: string;
    publicKey: string;
    privateKey: string;
    address: string;
    amountSent: string;
    transactionHash: string;
    explorerUrl: string;
    senderName?: string;
}

// Generate new XRPL EVM keypair
export function generateXRPLKeypair() {
    try {
        // Generate random wallet
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

// Check balance of an XRPL EVM address
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

// Send XRP on the EVM sidechain
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
            const currentBalance = ethers.formatEther(balance);
            return {
                success: false,
                error: 'Insufficient balance',
                message: `Current balance: ${currentBalance} XRP. Required: ${amountInXRP} XRP (plus gas fees)`,
                senderAddress,
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

        if (!gasPrice) {
            throw new Error('Could not get gas price');
        }

        // Create and send transaction
        const tx = await wallet.sendTransaction({
            to: recipientAddress,
            value: amountWei,
            gasLimit: gasEstimate,
            gasPrice: gasPrice
        });

        console.log('Transaction sent:', tx.hash);

        // Wait for confirmation
        const receipt = await tx.wait();

        if (!receipt) {
            throw new Error('Transaction receipt not found');
        }

        return {
            success: true,
            transactionHash: tx.hash,
            senderAddress,
            recipientAddress,
            amount: amountInXRP,
            gasUsed: receipt.gasUsed.toString(),
            effectiveGasPrice: receipt.gasPrice?.toString(),
            blockNumber: receipt.blockNumber,
            explorerUrl: `${EXPLORER_BASE_URL}/tx/${tx.hash}`,
            message: 'XRP sent successfully on XRPL EVM Sidechain'
        };
    } catch (error: any) {
        console.error('Error sending XRPL:', error);
        return {
            success: false,
            error: error.message || 'Unknown error',
            message: 'Failed to send XRP on XRPL EVM Sidechain'
        };
    }
}

// Request XRP from faucet (if available)
export async function requestXRPLFromFaucet(address: string) {
    // Note: The XRPL EVM Sidechain devnet faucet might have different endpoints
    // This is a placeholder - you'll need to check the official docs for the actual faucet API
    try {
        // Example faucet request (update with actual faucet endpoint when available)
        const faucetUrl = `https://faucet-evm-sidechain.xrpl.org/accounts/${address}`;

        const response = await fetch(faucetUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`Faucet request failed: ${response.statusText}`);
        }

        const result = await response.json();

        return {
            success: true,
            message: 'Successfully requested XRP from faucet',
            address,
            result
        };
    } catch (error: any) {
        console.error('Faucet request failed:', error);
        return {
            success: false,
            error: error.message || 'Failed to request from faucet',
            message: 'Faucet may be unavailable or rate limited'
        };
    }
}

// Send XRPL crypto gift email using the same service as SUI
export async function sendXRPLGiftEmail(params: XRPLGiftEmailParams) {
    // Use the existing email service from emailService.ts
    // This ensures emails are sent from the same Mailgun account as SUI
    return await sendCryptoGiftEmail({
        recipientEmail: params.recipientEmail,
        publicKey: params.publicKey,
        privateKey: params.privateKey,
        suiAddress: params.address, // Using address field for compatibility
        amountSent: params.amountSent + ' XRP (XRPL EVM Sidechain)',
        transactionDigest: params.transactionHash,
        explorerUrl: params.explorerUrl,
        senderName: params.senderName
    });
}

// Gift XRP with email notification
export async function giftXRPL(
    senderPrivateKey: string,
    recipientEmail: string,
    amountInXRP: string = DEFAULT_AMOUNT,
    senderName?: string
) {
    try {
        // Generate new keypair for recipient
        console.log('Generating new XRPL EVM keypair for recipient...');
        const recipientKeypair = generateXRPLKeypair();

        console.log(`Generated new address for recipient: ${recipientKeypair.address}`);

        // Send XRP to the new address
        console.log(`Sending ${amountInXRP} XRP to recipient...`);
        const sendResult = await sendXRPL(senderPrivateKey, recipientKeypair.address, amountInXRP);

        if (!sendResult.success) {
            return {
                success: false,
                error: sendResult.error,
                message: sendResult.message,
                needsFaucet: sendResult.needsFaucet
            };
        }

        // Send email with wallet credentials
        const emailParams: XRPLGiftEmailParams = {
            recipientEmail: recipientEmail || 'sanjay.amirthraj@gmail.com',
            publicKey: recipientKeypair.publicKey,
            privateKey: recipientKeypair.privateKey,
            address: recipientKeypair.address,
            amountSent: amountInXRP,
            transactionHash: sendResult.transactionHash!,
            explorerUrl: sendResult.explorerUrl!,
            senderName
        };

        console.log(`Sending email to ${emailParams.recipientEmail}...`);
        const emailResult = await sendXRPLGiftEmail(emailParams);

        // Check recipient's balance
        const recipientBalance = await checkXRPLBalance(recipientKeypair.address);

        return {
            success: true,
            message: `Successfully sent ${amountInXRP} XRP as a gift!`,
            transaction: {
                hash: sendResult.transactionHash,
                from: sendResult.senderAddress,
                to: recipientKeypair.address,
                amount: amountInXRP,
                explorerUrl: sendResult.explorerUrl,
                gasUsed: sendResult.gasUsed,
                blockNumber: sendResult.blockNumber
            },
            recipient: {
                address: recipientKeypair.address,
                privateKey: recipientKeypair.privateKey,
                publicKey: recipientKeypair.publicKey,
                mnemonic: recipientKeypair.mnemonic,
                balance: recipientBalance
            },
            email: {
                sent: emailResult.success,
                to: emailParams.recipientEmail,
                message: emailResult.message,
                error: emailResult.error
            }
        };
    } catch (error: any) {
        console.error('Error in giftXRPL:', error);
        return {
            success: false,
            error: error.message || 'Unknown error',
            message: 'Failed to complete XRPL gift'
        };
    }
}