import { Ed25519Keypair } from '@mysten/sui/keypairs/ed25519';
import { fromB64, toB64 } from '@mysten/sui/utils';
import { smsService } from './smsService';
import { sendCryptoGiftEmail } from './emailService';
import { generateXRPLKeypair } from './xrplService';

// Utility to check if a string is an email
export function isEmail(input: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(input);
}

// Utility to convert Uint8Array to hex string
export function toHexString(bytes: Uint8Array): string {
  return Array.from(bytes).map(byte => byte.toString(16).padStart(2, '0')).join('');
}

// Enhanced transfer handler for SUI
export async function handleSuiTransfer(
  senderKeypair: Ed25519Keypair,
  recipientInput: string,
  amount: number,
  senderName?: string
): Promise<any> {
  // Check if recipient is an email
  if (isEmail(recipientInput)) {
    console.log(`📧 Detected email address: ${recipientInput}`);

    // Generate new keypair for recipient
    const recipientKeypair = new Ed25519Keypair();
    const recipientAddress = recipientKeypair.getPublicKey().toSuiAddress();
    const recipientPrivateKey = recipientKeypair.getSecretKey();
    const recipientPublicKey = toHexString(recipientKeypair.getPublicKey().toRawBytes());

    console.log(`🔑 Generated new SUI wallet for ${recipientInput}:`);
    console.log(`   Address: ${recipientAddress}`);

    // Send SMS notification
    const smsSuccess = await smsService.sendCryptoEmailNotification(
      recipientInput,
      'SUI',
      recipientPrivateKey,
      recipientPublicKey,
      (amount / 1_000_000_000).toFixed(6)
    );

    if (smsSuccess) {
      console.log(`✅ SMS notification sent to +15109773150 for email delivery`);
    } else {
      console.log(`⚠️ Failed to send SMS notification`);
    }

    // Email is optional backup - don't let it fail the transfer
    let emailResult = { success: false, message: 'Email skipped - SMS is primary', error: 'SMS is primary method' };
    try {
      const emailParams = {
        recipientEmail: recipientInput,
        publicKey: recipientPublicKey,
        privateKey: recipientPrivateKey,
        suiAddress: recipientAddress,
        amountSent: (amount / 1_000_000_000).toFixed(6),
        transactionDigest: '',
        explorerUrl: `https://testnet.suivision.xyz/account/${recipientAddress}`,
        senderName: senderName || 'Anonymous'
      };

      console.log(`📨 Attempting backup email to ${recipientInput} (optional)...`);
      const tempResult = await sendCryptoGiftEmail(emailParams);
      emailResult = {
        success: tempResult.success,
        message: tempResult.message,
        error: tempResult.error || 'No error details'
      };
      if (emailResult.success) {
        console.log(`✅ Backup email sent successfully`);
      } else {
        console.log(`ℹ️ Backup email failed (not critical): ${emailResult.error}`);
      }
    } catch (error) {
      console.log(`ℹ️ Email service unavailable (using SMS only)`);
    }

    // Now proceed with the actual transfer to the new address
    return {
      recipientAddress,
      recipientEmail: recipientInput,
      walletGenerated: true,
      privateKey: recipientPrivateKey,
      publicKey: recipientPublicKey,
      smsNotification: smsSuccess,
      emailSent: emailResult.success,
      emailError: emailResult.error
    };
  } else {
    // Regular wallet address transfer
    console.log(`💳 Using wallet address: ${recipientInput}`);
    return {
      recipientAddress: recipientInput,
      walletGenerated: false
    };
  }
}

// Enhanced transfer handler for XRP
export async function handleXrpTransfer(
  senderPrivateKey: string,
  recipientInput: string,
  amount: string,
  senderName?: string
): Promise<any> {
  // Check if recipient is an email
  if (isEmail(recipientInput)) {
    console.log(`📧 Detected email address: ${recipientInput}`);

    // Generate new keypair for recipient
    const recipientKeypair = generateXRPLKeypair();

    console.log(`🔑 Generated new XRPL wallet for ${recipientInput}:`);
    console.log(`   Address: ${recipientKeypair.address}`);

    // Send SMS notification
    const smsSuccess = await smsService.sendCryptoEmailNotification(
      recipientInput,
      'XRP',
      recipientKeypair.privateKey,
      recipientKeypair.publicKey,
      amount
    );

    if (smsSuccess) {
      console.log(`✅ SMS notification sent to +15109773150 for email delivery`);
    } else {
      console.log(`⚠️ Failed to send SMS notification`);
    }

    // Email is optional backup - don't let it fail the transfer
    let emailResult = { success: false, message: 'Email skipped - SMS is primary', error: 'SMS is primary method' };
    try {
      // Import email service for XRP from xrplService
      const { sendXRPLGiftEmail } = await import('./xrplService');

      const emailParams = {
        recipientEmail: recipientInput,
        publicKey: recipientKeypair.publicKey,
        privateKey: recipientKeypair.privateKey,
        address: recipientKeypair.address,
        amountSent: amount,
        transactionHash: '',
        explorerUrl: `https://explorer.testnet.xrplevm.org/address/${recipientKeypair.address}`,
        senderName: senderName || 'Anonymous'
      };

      console.log(`📨 Attempting backup email to ${recipientInput} (optional)...`);
      const tempResult = await sendXRPLGiftEmail(emailParams);
      emailResult = {
        success: tempResult.success,
        message: tempResult.message,
        error: tempResult.error || 'No error details'
      };
      if (emailResult.success) {
        console.log(`✅ Backup email sent successfully`);
      } else {
        console.log(`ℹ️ Backup email failed (not critical): ${emailResult.error}`);
      }
    } catch (error) {
      console.log(`ℹ️ Email service unavailable (using SMS only)`);
    }

    return {
      recipientAddress: recipientKeypair.address,
      recipientEmail: recipientInput,
      walletGenerated: true,
      privateKey: recipientKeypair.privateKey,
      publicKey: recipientKeypair.publicKey,
      mnemonic: recipientKeypair.mnemonic,
      smsNotification: smsSuccess,
      emailSent: emailResult.success,
      emailError: emailResult.error
    };
  } else {
    // Regular wallet address transfer
    console.log(`💳 Using wallet address: ${recipientInput}`);
    return {
      recipientAddress: recipientInput,
      walletGenerated: false
    };
  }
}

// Import required dependencies for SUI transfer
import { SuiClient, getFullnodeUrl } from '@mysten/sui/client';
import { Transaction } from '@mysten/sui/transactions';

const NETWORK = "testnet";
const suiClient = new SuiClient({ url: getFullnodeUrl(NETWORK) });

// Function to send SUI (duplicated here to avoid circular dependency)
async function performSuiTransfer(keypair: Ed25519Keypair, recipientAddress: string, amount: number) {
  try {
    const senderAddress = keypair.toSuiAddress();

    // Check sender's balance first
    const balance = await suiClient.getBalance({ owner: senderAddress });
    const totalBalance = parseInt(balance.totalBalance);

    if (totalBalance < amount) {
      return {
        success: false,
        error: "Insufficient balance",
        message: `Current balance: ${(totalBalance / 1_000_000_000).toFixed(6)} SUI. Required: ${(amount / 1_000_000_000).toFixed(6)} SUI (plus gas fees)`,
        senderAddress: senderAddress,
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

    return {
      success: true,
      transactionDigest: result.digest,
      senderAddress: senderAddress,
      recipientAddress: recipientAddress,
      amount: amount,
      amountInSUI: (amount / 1_000_000_000).toFixed(6),
      message: "SUI sent successfully",
      explorerUrl: `https://testnet.suivision.xyz/txblock/${result.digest}`
    };
  } catch (error: any) {
    console.error("Error sending SUI:", error);
    return {
      success: false,
      error: error.message || 'Unknown error',
      message: "Failed to send SUI"
    };
  }
}

// Wrapper for sendSui that handles email addresses
export async function sendSuiEnhanced(
  keypair: Ed25519Keypair,
  recipientInput: string,
  amount: number,
  senderName?: string
): Promise<any> {
  const transferInfo = await handleSuiTransfer(keypair, recipientInput, amount, senderName);

  // Use the actual recipient address (either provided or generated)
  const result = await performSuiTransfer(keypair, transferInfo.recipientAddress, amount);

  // Enhance the result with email/SMS info if applicable
  if (transferInfo.walletGenerated) {
    return {
      ...result,
      recipientEmail: transferInfo.recipientEmail,
      walletGenerated: true,
      walletCredentials: {
        address: transferInfo.recipientAddress,
        privateKey: transferInfo.privateKey,
        publicKey: transferInfo.publicKey
      },
      notifications: {
        sms: transferInfo.smsNotification,
        email: transferInfo.emailSent,
        emailError: transferInfo.emailError
      },
      instructions: transferInfo.smsNotification
        ? `✅ SMS sent to +15109773150 with wallet credentials for ${transferInfo.recipientEmail}`
        : `⚠️ SMS failed - Please manually send wallet credentials to ${transferInfo.recipientEmail}`
    };
  }

  return result;
}

// Wrapper for sendXRPL that handles email addresses
export async function sendXrpEnhanced(
  privateKey: string,
  recipientInput: string,
  amount: string,
  senderName?: string
): Promise<any> {
  const transferInfo = await handleXrpTransfer(privateKey, recipientInput, amount, senderName);

  // Import the original sendXRPL function
  const { sendXRPL } = await import('./xrplService');

  // Use the actual recipient address (either provided or generated)
  const result = await sendXRPL(privateKey, transferInfo.recipientAddress, amount);

  // Enhance the result with email/SMS info if applicable
  if (transferInfo.walletGenerated) {
    return {
      ...result,
      recipientEmail: transferInfo.recipientEmail,
      walletGenerated: true,
      walletCredentials: {
        address: transferInfo.recipientAddress,
        privateKey: transferInfo.privateKey,
        publicKey: transferInfo.publicKey,
        mnemonic: transferInfo.mnemonic
      },
      notifications: {
        sms: transferInfo.smsNotification,
        email: transferInfo.emailSent,
        emailError: transferInfo.emailError
      },
      instructions: transferInfo.smsNotification
        ? `✅ SMS sent to +15109773150 with wallet credentials for ${transferInfo.recipientEmail}`
        : `⚠️ SMS failed - Please manually send wallet credentials to ${transferInfo.recipientEmail}`
    };
  }

  return result;
}