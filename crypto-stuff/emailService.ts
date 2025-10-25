import Mailgun from 'mailgun.js';
import FormData from 'form-data';

// HARDCODED Mailgun configuration
const MAILGUN_API_KEY = 'e3ad96a6c4a661efd1accdd5e62a7801-ba8a60cd-e09445c0';
const MAILGUN_DOMAIN = 'sandbox1ae38be4c9284d629e03f2454a25619c.mailgun.org';
const FROM_EMAIL = 'monkeyman20204@gmail.com';

// Initialize Mailgun client with hardcoded API key
const mailgun = new Mailgun(FormData);
const mg = mailgun.client({
    username: 'api',
    key: MAILGUN_API_KEY,
    url: 'https://api.mailgun.net' // Explicitly set US region
});

interface CryptoGiftEmailParams {
    recipientEmail: string;
    publicKey: string;
    privateKey: string;
    suiAddress: string;
    amountSent: string;
    transactionDigest: string;
    explorerUrl: string;
    senderName?: string;
}

// HTML email template for crypto gift notification
function createCryptoGiftEmailHTML(params: CryptoGiftEmailParams): string {
    return `
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>You've Received SUI Cryptocurrency!</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f4f4f4;
            }
            .container {
                background-color: white;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #4A90E2;
                border-bottom: 3px solid #4A90E2;
                padding-bottom: 10px;
            }
            .highlight {
                background-color: #E8F4FD;
                border-left: 4px solid #4A90E2;
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
            }
            .amount {
                font-size: 24px;
                font-weight: bold;
                color: #27AE60;
            }
            .credentials {
                background-color: #FFF9C4;
                border: 2px dashed #FFA726;
                padding: 20px;
                margin: 20px 0;
                border-radius: 5px;
            }
            .key-item {
                background-color: #F5F5F5;
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
                word-break: break-all;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
            .warning {
                background-color: #FFE5E5;
                border: 2px solid #FF6B6B;
                color: #C41E3A;
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
                font-weight: bold;
            }
            .button {
                display: inline-block;
                padding: 12px 24px;
                background-color: #4A90E2;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 10px 0;
            }
            .footer {
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #E0E0E0;
                color: #666;
                font-size: 12px;
            }
            .steps {
                background-color: #F0F7FF;
                padding: 20px;
                margin: 20px 0;
                border-radius: 5px;
            }
            .step {
                margin: 15px 0;
                padding-left: 30px;
                position: relative;
            }
            .step::before {
                content: "✓";
                position: absolute;
                left: 0;
                color: #27AE60;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎉 Congratulations! You've Received Cryptocurrency!</h1>

            <p>Hello!</p>

            <p>${params.senderName ? `<strong>${params.senderName}</strong>` : 'Someone'} has sent you a gift of cryptocurrency on the SUI blockchain (testnet)!</p>

            <div class="highlight">
                <p>Amount Received:</p>
                <p class="amount">${params.amountSent} SUI</p>
                <p style="color: #666;">Transaction ID: <code>${params.transactionDigest}</code></p>
            </div>

            <div class="credentials">
                <h2>🔑 Your Wallet Credentials</h2>
                <p><strong>IMPORTANT:</strong> Save these credentials securely. They provide complete access to your cryptocurrency wallet!</p>

                <h3>Wallet Address (Public):</h3>
                <div class="key-item">${params.suiAddress}</div>

                <h3>Public Key:</h3>
                <div class="key-item">${params.publicKey}</div>

                <h3>Private Key (KEEP SECRET!):</h3>
                <div class="key-item">${params.privateKey}</div>
            </div>

            <div class="warning">
                ⚠️ SECURITY WARNING: Never share your private key with anyone! It's like the password to your bank account. Anyone with this key can access and transfer your funds.
            </div>

            <div class="steps">
                <h2>📝 How to Access Your Funds:</h2>
                <div class="step">
                    <strong>Save your credentials:</strong> Copy and store your private key in a secure location (password manager recommended).
                </div>
                <div class="step">
                    <strong>Install a wallet:</strong> Download a SUI wallet like Sui Wallet, Ethos, or Martian from their official websites.
                </div>
                <div class="step">
                    <strong>Import your wallet:</strong> Use your private key to import your wallet into the app.
                </div>
                <div class="step">
                    <strong>Check your balance:</strong> Once imported, you'll see your ${params.amountSent} SUI balance.
                </div>
            </div>

            <p><strong>View your transaction on the blockchain:</strong></p>
            <a href="${params.explorerUrl}" class="button" style="color: white;">View Transaction on Explorer</a>

            <div class="footer">
                <p><strong>What is SUI?</strong><br>
                SUI is a next-generation blockchain platform designed for speed, security, and scalability. The tokens you received are on the testnet (test network) for experimentation and learning.</p>

                <p><strong>Need help?</strong><br>
                Visit the official SUI documentation at <a href="https://sui.io">sui.io</a> or reach out to the person who sent you this gift.</p>

                <p style="margin-top: 20px; color: #999;">
                This is an automated message sent on behalf of ${params.senderName || 'a SUI user'}.
                Sent via Crypto Gift Service.
                </p>
            </div>
        </div>
    </body>
    </html>
    `;
}

// Send crypto gift email using Mailgun
export async function sendCryptoGiftEmail(params: CryptoGiftEmailParams): Promise<{ success: boolean; message: string; error?: any }> {
    try {
        const messageData = {
            from: `Crypto Gift Service <mailgun@${MAILGUN_DOMAIN}>`,
            to: params.recipientEmail,
            subject: '🎁 You\'ve Received SUI Cryptocurrency!',
            html: createCryptoGiftEmailHTML(params),
            text: `
Congratulations! You've Received Cryptocurrency!

${params.senderName ? params.senderName : 'Someone'} has sent you ${params.amountSent} SUI on the SUI blockchain (testnet)!

YOUR WALLET CREDENTIALS (SAVE THESE SECURELY):
================================================
Wallet Address: ${params.suiAddress}
Public Key: ${params.publicKey}
Private Key: ${params.privateKey}

IMPORTANT SECURITY WARNING:
Never share your private key with anyone! It provides complete access to your wallet.

HOW TO ACCESS YOUR FUNDS:
1. Save your credentials in a secure location
2. Download a SUI wallet (Sui Wallet, Ethos, or Martian)
3. Import your wallet using the private key
4. Your ${params.amountSent} SUI will be available

View your transaction: ${params.explorerUrl}

Transaction ID: ${params.transactionDigest}

For more information about SUI, visit: https://sui.io

This is an automated message. Sent via Crypto Gift Service.
            `
        };

        const result = await mg.messages.create(MAILGUN_DOMAIN, messageData);
        console.log('Email sent successfully:', result);

        return {
            success: true,
            message: `Email sent successfully to ${params.recipientEmail} (ID: ${result.id})`
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

// Verify email configuration
export async function verifyEmailConfig(): Promise<boolean> {
    // For sandbox domains, we can't validate the domain via API
    // But we can verify the configuration is set
    console.log('Mailgun configuration:');
    console.log('  Domain:', MAILGUN_DOMAIN);
    console.log('  API Key:', MAILGUN_API_KEY.substring(0, 10) + '...');
    console.log('  From Email:', FROM_EMAIL);
    console.log('✅ Mailgun service configured with sandbox domain.');
    return true;
}