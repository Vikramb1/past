# Voice-Controlled Crypto Payment Guide

## Overview

This system now supports voice-controlled SUI cryptocurrency payments! Say an amount out loud, then hold a snap gesture for 2+ seconds to send the crypto.

## Quick Start

### 1. Install Dependencies

```bash
cd face_recognition
pip install -r requirements.txt
```

**Important**: Make sure you have Ollama installed and the llama3.2 model downloaded:

```bash
# Install Ollama (if not already installed)
# For macOS: brew install ollama

# Pull the llama3.2 model
ollama pull llama3.2
```

### 2. Run the Application

```bash
python main.py
```

The system will automatically:
- Start listening to your microphone (Deepgram transcription)
- Show live transcription at the bottom of the video feed
- Parse amounts when you perform snap gestures

## How to Use

### Basic Usage

1. **Say the amount you want to send:**
   - "send 0.5 SUI"
   - "send 0.0001 SUI"
   - "0.25 SUI"

2. **Perform and hold a snap gesture:**
   - Bring your thumb and index finger together (snap position)
   - Hold for 2+ seconds
   - You'll see a "SNAP!" indicator on screen

3. **Watch the payment flow:**
   - At 1.5s hold: Amount preview appears at top right
   - At 2.0s hold: Payment triggers
   - Success/failure notification appears

### Example Commands

#### Voice Commands
- ✅ "send 0.5 SUI"
- ✅ "send 0.0001 SUI"
- ✅ "0.25 SUI"
- ✅ "send five SUI" (natural language)
- ✅ "transfer 1.5 SUI"

#### What Happens
1. You say: **"send 0.5 SUI"**
2. Transcription appears at bottom: "send 0.5 SUI"
3. You snap and hold for 2 seconds
4. Top right shows: "Sending: 0.5 SUI"
5. Payment is sent (500,000,000 MIST)
6. Success message appears

### Fallback Behavior

If no amount is detected in your speech, the system will:
- Use the default amount: **0.0001 SUI**
- Show: "Using default: 0.0001 SUI"
- Still send the payment with the default amount

## Visual Feedback

### On-Screen Displays

1. **Transcription (Bottom Center)**
   - Small, gray text
   - Shows last thing you said
   - Updates in real-time

2. **Amount Preview (Top Right)**
   - Appears when you hold snap for 1.5s+
   - Yellow text with border
   - Shows: "Sending: X SUI"

3. **Payment Status (Top Center)**
   - Green: Success ✅
   - Red: Failure ❌
   - Shows transaction digest

4. **Gesture Detection**
   - Green box: Snap detected
   - Blue box: Hand detected (no snap)
   - Label shows which hand

## Configuration

Edit `config.py` to customize:

```python
# Speech transcription settings
ENABLE_SPEECH_TRANSCRIPTION = True
DEEPGRAM_API_KEY = "your-key-here"
TRANSCRIPTION_BUFFER_SECONDS = 10  # Parse last N seconds

# Amount parsing settings
OLLAMA_MODEL = "llama3.2"
DEFAULT_PAYMENT_AMOUNT_SUI = 0.0001

# Display settings
TRANSCRIPTION_FONT_SCALE = 0.4  # Smaller = smaller text
AMOUNT_FONT_SCALE = 0.7
```

## Troubleshooting

### Transcription Not Working

**Issue**: No text appears at bottom of screen

**Solutions**:
- Check your Deepgram API key is correct in `config.py`
- Verify microphone permissions
- Check console for connection errors
- Test with: `python -m pyaudio` to verify audio input

### Amount Not Parsing

**Issue**: Always uses default amount (0.0001 SUI)

**Solutions**:
- Make sure Ollama is running: `ollama list`
- Pull llama3.2 model: `ollama pull llama3.2`
- Check console logs for parsing errors
- Try simpler phrases: "send 0.5 SUI"

### Payment Not Triggering

**Issue**: Snap gesture doesn't trigger payment

**Solutions**:
- Hold snap for **full 2 seconds**
- Make sure fingers are close together (snap position)
- Check hand is visible to camera
- Wait for cooldown period (30s between payments)

### Crypto Server Not Starting

**Issue**: "Server not ready" error

**Solutions**:
- Check Node.js is installed: `node --version`
- Install dependencies: `cd ../crypto-stuff && npm install`
- Check port 3001 is not in use
- Look for server logs in console

## Technical Details

### Architecture

```
Speech → Deepgram → Transcription Buffer (10s)
                          ↓
Snap Gesture → Amount Parser (Ollama) → Payment
                          ↓
                    Crypto Server → SUI Blockchain
```

### Components

1. **SpeechTranscriber** (`speech_transcription.py`)
   - Captures microphone audio with PyAudio
   - Streams to Deepgram real-time API
   - Maintains 10-second rolling buffer
   - Runs in background thread

2. **AmountParser** (`amount_parser.py`)
   - First tries regex patterns (fast)
   - Falls back to Ollama LLM (smart)
   - Validates amounts (min/max checks)
   - Converts SUI to MIST

3. **Main Application** (`main.py`)
   - Integrates all components
   - Displays transcription overlay
   - Shows amount preview
   - Triggers payments on snap hold

4. **Crypto Handler** (`crypto_payment.py`)
   - Accepts dynamic amounts
   - Manages Node.js server
   - Handles cooldown periods
   - Reports transaction status

### Data Flow

1. **Continuous**: Audio → Deepgram → Buffer
2. **On Snap Hold (1.5s)**: Buffer → Parser → Preview
3. **On Snap Hold (2.0s)**: Amount → Payment → Blockchain
4. **After Payment**: Status → Display

## API Keys & Configuration

### Deepgram API Key

Your key is configured in `config.py`:
```python
DEEPGRAM_API_KEY = "b6dd69dddfa27a355aa91f7b1c7688c7c8805f72"
```

**Security Note**: For production, use environment variables instead:
```python
import os
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
```

### Wallet Configuration

Configured in `config.py`:
```python
FUNDED_WALLET_PRIVATE_KEY = "suiprivkey1qr..."
RECIPIENT_WALLET_ADDRESS = "0xbf8ba7..."
```

## Safety Features

1. **Amount Validation**
   - Minimum: 0.00001 SUI
   - Maximum: 1000 SUI
   - No negative amounts
   - No zero amounts

2. **Cooldown Period**
   - 30 seconds between payments
   - Prevents accidental double-sends
   - Shows remaining cooldown time

3. **Confirmation Preview**
   - Shows amount for 2 seconds
   - Gives time to release snap if wrong
   - Clear visual feedback

## Performance Tips

- Close other apps using microphone
- Speak clearly near microphone
- Keep hand visible to camera
- Good lighting helps gesture detection
- Wait for transcription to appear before snapping

## What's New

### Added Files
- `speech_transcription.py` - Deepgram integration
- `amount_parser.py` - Ollama LLM parsing
- `VOICE_PAYMENT_GUIDE.md` - This guide

### Modified Files
- `main.py` - Integrated speech & display overlays
- `config.py` - Added speech/parsing settings
- `crypto_payment.py` - Accepts dynamic amounts
- `requirements.txt` - Added new dependencies

### Dependencies Added
- `deepgram-sdk>=3.0.0` - Speech-to-text
- `ollama>=0.1.0` - Local LLM
- `pyaudio>=0.2.13` - Audio capture
- `requests>=2.31.0` - HTTP client

## Next Steps

### Try It Out
1. Start the app: `python main.py`
2. Say: "send 0.5 SUI"
3. Snap and hold for 2 seconds
4. Watch your payment go through! 🚀

### Customize
- Adjust font sizes in `config.py`
- Change default amount
- Modify transcription buffer duration
- Swap Ollama model

### Extend
- Add more natural language patterns
- Support multiple currencies
- Add voice commands for other actions
- Integrate with more LLMs

## Support

For issues or questions:
- Check console logs for detailed errors
- Verify all dependencies are installed
- Test components individually
- Review configuration settings

---

**Happy voice-controlled crypto payments!** 🎤💰🚀

