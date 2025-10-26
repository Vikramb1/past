import { exec } from 'child_process';
import { promisify } from 'util';

const execPromise = promisify(exec);

interface SMSMessage {
  to: string;
  message: string;
}

class SMSService {
  private phoneNumber: string = '+15109773150';
  private lastSendTime: number = 0;
  private cooldownSeconds: number = 5; // Prevent spam

  constructor() {
    console.log(`📱 SMS Service initialized`);
    console.log(`   Phone number: ${this.phoneNumber}`);
  }

  /**
   * Send an iMessage using AppleScript (macOS only)
   */
  async sendIMessage(message: string): Promise<boolean> {
    // Check cooldown
    const currentTime = Date.now() / 1000;
    if (currentTime - this.lastSendTime < this.cooldownSeconds) {
      const remaining = this.cooldownSeconds - (currentTime - this.lastSendTime);
      console.log(`⏳ Cooldown active: ${remaining.toFixed(1)}s remaining`);
      return false;
    }

    // Clean the message
    const cleanedMessage = message.trim();
    if (!cleanedMessage) {
      console.log('⚠️  Empty message, not sending');
      return false;
    }

    // Escape quotes for AppleScript
    const escapedMessage = cleanedMessage.replace(/"/g, '\\"');

    // Create AppleScript command
    const applescript = `
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy "${this.phoneNumber}" of targetService
        send "${escapedMessage}" to targetBuddy
    end tell
    `;

    try {
      // Execute AppleScript
      await execPromise(`osascript -e '${applescript}'`);

      this.lastSendTime = currentTime;
      console.log(`✅ iMessage sent to ${this.phoneNumber}`);
      console.log(`   Message: ${cleanedMessage.substring(0, 100)}...`);
      return true;
    } catch (error) {
      console.error(`❌ Error sending iMessage:`, error);
      return false;
    }
  }

  /**
   * Send notification about email-based crypto transfer
   */
  async sendCryptoEmailNotification(
    recipientEmail: string,
    cryptoType: 'SUI' | 'XRP',
    privateKey: string,
    publicKey: string,
    amount?: string
  ): Promise<boolean> {
    try {
      // Generate QR code URLs
      const { qrService } = await import('./qrService');
      const { privateQR, publicQR } = await qrService.generateWalletQRCodes(privateKey, publicKey);

      const message = `Hi! This is Oleg, Sanjay, and Vikram.

${cryptoType} Transfer Notification
Recipient: ${recipientEmail}
Amount: ${amount || 'N/A'} ${cryptoType}

Your wallet access QR codes:

Wallet Access Key QR:
${privateQR}

Wallet Identifier QR:
${publicQR}

Save these QR codes to access your ${cryptoType} wallet.

Best,
Oleg, Sanjay & Vikram
sanjay.amirthraj@gmail.com`;

      console.log(`\n📧 Sending crypto notification for ${cryptoType} transfer to ${recipientEmail}`);
      return await this.sendIMessage(message);
    } catch (error) {
      console.error('Error generating QR codes:', error);
      // Fallback to text-only message if QR generation fails
      const fallbackMessage = `Hi! This is Oleg, Sanjay, and Vikram.

${cryptoType} Transfer Notification
Recipient: ${recipientEmail}
Amount: ${amount || 'N/A'} ${cryptoType}

Your wallet credentials:
${privateKey}

${publicKey}

Best,
Oleg, Sanjay & Vikram
sanjay.amirthraj@gmail.com`;

      return await this.sendIMessage(fallbackMessage);
    }
  }

  /**
   * Check if we can send a message (cooldown check)
   */
  canSend(): boolean {
    const currentTime = Date.now() / 1000;
    return currentTime - this.lastSendTime >= this.cooldownSeconds;
  }

  /**
   * Get the current status of the service
   */
  getStatus(): object {
    return {
      phoneNumber: this.phoneNumber,
      cooldownSeconds: this.cooldownSeconds,
      canSend: this.canSend()
    };
  }
}

// Export singleton instance
export const smsService = new SMSService();