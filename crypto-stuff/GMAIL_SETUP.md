# Gmail Email Setup Guide for Crypto Gifting

## Current Status
- ✅ Keypair generation is working perfectly
- ❌ Email sending requires Gmail app-specific password

## Quick Setup (3 minutes)

### Step 1: Enable 2-Factor Authentication
1. Visit: https://myaccount.google.com/security
2. Click "2-Step Verification"
3. Follow the setup wizard (if not already enabled)

### Step 2: Generate App Password
1. Visit: https://myaccount.google.com/apppasswords
2. Sign in with your Gmail account
3. Under "Select app" → Choose "Mail"
4. Under "Select device" → Choose "Other (Custom name)"
5. Enter name: "SUI Crypto App"
6. Click "Generate"
7. **Copy the 16-character password shown** (looks like: xxxx xxxx xxxx xxxx)

### Step 3: Update .env File
Open `/crypto-stuff/.env` and update:
```
EMAIL_USER=sanjay.amirthraj@gmail.com
EMAIL_PASSWORD=xxxx xxxx xxxx xxxx  # Your app password from Step 2 (can include spaces)
```

### Step 4: Restart the Server
```bash
# Stop the current server (Ctrl+C)
# Then restart:
npm run dev
```

### Step 5: Test Email
```bash
curl -X POST http://localhost:3000/test-email \
  -H "Content-Type: application/json" \
  -d '{"recipientEmail": "sanjay.amirthraj@gmail.com"}'
```

## Why App Passwords?
- Gmail blocks "less secure apps" from using regular passwords
- App passwords are Google's secure way to allow SMTP access
- Each app password can be revoked independently
- Protects your main account password

## Troubleshooting
If you still get authentication errors:
1. Make sure 2-factor authentication is enabled
2. Try removing spaces from the app password
3. Wait a few minutes after generating (sometimes takes time to activate)
4. Check that you're using the app password, not your regular Gmail password

## Alternative: Less Secure Apps (NOT Recommended)
If you can't use 2FA, you can enable "Less secure app access":
1. Go to: https://myaccount.google.com/lesssecureapps
2. Turn ON "Allow less secure apps"
3. Use your regular Gmail password in .env

⚠️ This method is deprecated by Google and may stop working soon.

## Success Indicators
When working correctly, you'll see:
- Server shows: "✅ Email service configured and ready"
- Test endpoint returns: `"sent": true`
- Email arrives in inbox with wallet credentials