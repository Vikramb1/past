# Quick Test Guide - Voice-Controlled Crypto Payments

## ✅ Prerequisites Check

All systems ready:
- ✅ Deepgram SDK v3 installed
- ✅ Ollama with llama3.2 model installed
- ✅ Speech transcription enabled
- ✅ All code updated and integrated

## 🚀 How to Run

```bash
cd /Users/vikra/past/face_recognition
python main.py
```

## 🎯 Testing Scenarios

### Scenario 1: Voice-Controlled Payment
1. **Say**: "send 0.5 SUI"
2. **Watch**: Transcription appears at bottom of screen
3. **Snap**: Bring thumb and index finger together
4. **Hold**: Keep snap position for 2+ seconds
5. **See**: Amount preview appears at top right (1.5s mark)
6. **Trigger**: Payment sends at 2.0s mark
7. **Confirm**: Success message appears

### Scenario 2: Natural Language
Try these phrases:
- "send 0.0001 SUI"
- "send five SUI"
- "0.25 SUI"
- "transfer 1.5 SUI"

### Scenario 3: Default Amount
1. **Say nothing** or say something unrelated like "hello"
2. **Snap and hold** for 2 seconds
3. **Result**: Uses default 0.0001 SUI

### Scenario 4: Test Without Speech
1. Don't say anything
2. Snap and hold for 2 seconds
3. Should send default 0.0001 SUI

## 📺 What You'll See On Screen

### Bottom Center (Small Gray Text)
```
send 0.5 SUI
```
Latest thing you said

### Top Right (Yellow Text with Border)
```
Sending: 0.5 SUI
```
Appears at 1.5s hold, shows parsed amount

### Top Center (Green/Red)
```
✅ Sent 0.5 SUI!
Transaction: abc123...
```
Success/failure message after payment

### Hand Detection
- **Blue box**: Hand detected (no snap)
- **Green box with "SNAP!"**: Snap gesture detected

## 🐛 Troubleshooting

### No Transcription Appearing
**Issue**: Nothing shows at bottom of screen

**Check**:
1. Microphone permissions: System Preferences → Security & Privacy → Microphone
2. Deepgram connection in console logs
3. Speak clearly and close to microphone

**Fix**:
```bash
# Grant microphone access to Terminal/your IDE
# Check System Preferences → Security & Privacy → Privacy → Microphone
```

### "Server not ready" Error
**Issue**: Payment doesn't send

**Fix**:
```bash
cd /Users/vikra/past/crypto-stuff
npm install
npx ts-node suicrypto.ts
```
Wait for server to start (port 3001), then run face recognition in new terminal

### Snap Gesture Not Detected
**Issue**: Snap box doesn't appear

**Solutions**:
- Make sure hand is visible to camera
- Good lighting helps
- Bring thumb and index finger close together
- Hold position (don't actually snap/make sound)

### Amount Not Parsing
**Issue**: Always uses default 0.0001 SUI

**Check**:
1. Ollama is running: `ollama list`
2. llama3.2 model installed
3. Say "send" before the amount
4. Wait 1-2 seconds after speaking before snapping

**Fix**:
```bash
# Make sure Ollama is running (it should start automatically)
# If not, start it:
ollama serve &

# Pull model if missing:
ollama pull llama3.2
```

### PyAudio Errors
**Issue**: Segmentation fault or pyaudio errors

**Fix**:
```bash
# Install system dependencies
sudo chown -R vikra /opt/homebrew
brew install portaudio
pip install --force-reinstall pyaudio
```

## 📊 Expected Console Output

```
============================================================
Real-Time Face Detection & Recognition System
============================================================

Initializing components...
🧠 Amount Parser initialized
Model: llama3.2
Default amount: 0.0001 SUI

🎤 Speech Transcriber initialized
Sample rate: 16000 Hz
Buffer duration: 10 seconds

✅ Speech transcription started
🎙️  Microphone opened successfully
✅ Deepgram connection established

CONTROLS:
  q or ESC  - Quit application
  s         - Save detected faces manually
  r         - Rebuild face database
  SPACE     - Pause/Resume

CRYPTO PAYMENT: Enabled - Hold snap for 2s to send SUI
SPEECH TRANSCRIPTION: Enabled - Say amount before snap
  Example: 'send 0.5 SUI' then hold snap gesture
============================================================

Starting face recognition...

🗣️  send 0.5 SUI

SNAP detected! Hand: Right_0, Confidence: 0.95

💰 Amount validated: 0.5 SUI

💰 Payment triggered by 2.1s snap hold!
💸 Sending 0.5 SUI (500000000 MIST)

💸 Initiating crypto payment...
Amount: 500000000 MIST (0.5 SUI)
To: 0xbf8ba70997c705101...

✅ Payment successful!
   Transaction: 5vN8xK...
```

## 🎉 Success Indicators

### ✅ Working Correctly If You See:
1. "🗣️" emojis when you speak
2. Transcription text at bottom
3. "SNAP!" label when you snap
4. Amount preview at top right
5. Payment success message
6. Transaction digest

### ❌ Issues If You See:
1. No transcription appearing
2. "Server not ready" errors
3. Always uses default amount
4. No snap detection
5. Connection errors

## 💡 Pro Tips

1. **Speak clearly**: Wait 1 second after speaking before snapping
2. **Hold steady**: Keep snap position stable for full 2 seconds
3. **Good lighting**: Helps with hand detection
4. **Close to mic**: Speak near microphone for better transcription
5. **Watch overlays**: Visual feedback tells you what's happening

## 🔧 Quick Fixes

### If Nothing Works
```bash
# 1. Disable speech transcription to test other features
# Edit config.py:
ENABLE_SPEECH_TRANSCRIPTION = False

# 2. Test with default amount only
python main.py
# Snap and hold → sends 0.0001 SUI
```

### If Crypto Payments Don't Work
```bash
# Check wallet has balance
cd /Users/vikra/past/crypto-stuff
node -e "
const { SuiClient, getFullnodeUrl } = require('@mysten/sui/client');
const client = new SuiClient({ url: getFullnodeUrl('testnet') });
client.getBalance({ owner: '0xbf8ba7...' }).then(console.log);
"
```

## 📱 Test Checklist

- [ ] Run `python main.py` successfully
- [ ] See video feed from camera
- [ ] Speak and see transcription
- [ ] Perform snap gesture → see green box
- [ ] Hold snap for 2s → see amount preview
- [ ] Payment triggers at 2s → see success message
- [ ] Try different amounts (0.1, 0.5, 1.0 SUI)
- [ ] Try natural language ("five SUI")
- [ ] Test default fallback (no speech)

## 🎯 Next Steps

Once everything works:
1. Adjust font sizes in `config.py` if needed
2. Change default amount
3. Modify cooldown period
4. Customize display positions
5. Add more natural language patterns

---

**Ready to test!** 🚀

Run: `cd /Users/vikra/past/face_recognition && python main.py`

