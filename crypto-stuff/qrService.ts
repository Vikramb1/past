import QRCode from 'qrcode';
import * as fs from 'fs';
import * as path from 'path';

export class QRService {
  private outputDir: string;

  constructor() {
    this.outputDir = path.join(__dirname, 'qr-codes');

    // Create output directory if it doesn't exist
    if (!fs.existsSync(this.outputDir)) {
      fs.mkdirSync(this.outputDir, { recursive: true });
    }
  }

  /**
   * Generate QR code as data URL
   */
  async generateQRDataURL(text: string): Promise<string> {
    try {
      const dataURL = await QRCode.toDataURL(text, {
        errorCorrectionLevel: 'M',
        type: 'image/png',
        quality: 1,
        margin: 1,
        width: 256,
        color: {
          dark: '#000000',
          light: '#FFFFFF'
        }
      });
      return dataURL;
    } catch (error) {
      console.error('Error generating QR code:', error);
      throw error;
    }
  }

  /**
   * Generate QR codes for wallet credentials and return URLs
   */
  async generateWalletQRCodes(privateKey: string, publicKey: string): Promise<{ privateQR: string; publicQR: string }> {
    try {
      // For now, use a QR code generation service API
      // You can replace this with your own hosted QR service
      const privateQRUrl = `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(privateKey)}`;
      const publicQRUrl = `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(publicKey)}`;

      return {
        privateQR: privateQRUrl,
        publicQR: publicQRUrl
      };
    } catch (error) {
      console.error('Error generating QR codes:', error);
      throw error;
    }
  }

  /**
   * Generate a combined page with both QR codes
   */
  async generateWalletQRPage(
    privateKey: string,
    publicKey: string,
    recipientEmail: string,
    cryptoType: string,
    amount: string
  ): Promise<string> {
    // Create a unique ID for this wallet
    const walletId = Date.now().toString(36) + Math.random().toString(36).substr(2);

    // Create QR codes
    const { privateQR, publicQR } = await this.generateWalletQRCodes(privateKey, publicKey);

    // Generate the HTML page URL (you would host this on your server)
    // For now, return a data URL or hosted page URL
    const pageUrl = `https://wallet.calhacks.ai/qr/${walletId}?pk=${encodeURIComponent(privateQR)}&pub=${encodeURIComponent(publicQR)}`;

    return pageUrl;
  }
}

export const qrService = new QRService();