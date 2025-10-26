# iMessage Peace Sign Feature

## Overview
This feature automatically sends the last 15 seconds of transcribed speech via iMessage when a peace sign gesture (✌️) is detected. The transcript is sent to the configured phone number (+15109773150).

## How It Works

### 1. Continuous Transcription
- The system continuously transcribes speech using Deepgram
- Maintains a rolling buffer of recent transcriptions

### 2. Peace Sign Detection
- Uses MediaPipe to detect hand gestures
- Recognizes peace sign: index and middle fingers extended, others folded
- Visual feedback shows "PEACE!" when detected

### 3. Transcript Capture & Send
- When peace sign is detected, captures the **last 15 seconds** of transcript
- Automatically sends via iMessage to **+15109773150**
- Uses macOS native Messages app

## Usage Examples

### Example 1: Meeting Notes
```
You: [Speaking] "The meeting is scheduled for tomorrow at 3 PM in conference room B. We need to discuss the Q4 budget."
You: [Show peace sign ✌️]
System: Captures last 15 seconds → Sends transcript via iMessage
```

### Example 2: Quick Reminder
```
You: [Speaking] "Remember to pick up milk, eggs, and bread from the store. Also need to call the dentist."
You: [Show peace sign ✌️]
System: Captures last 15 seconds → Sends transcript via iMessage
```

## Configuration

### Phone Number
The recipient phone number is configured in `imessage_handler.py`:
```python
self.phone_number = "+15109773150"
```

### Transcript Lookback Duration
The system captures the last 15 seconds of speech:
```python
self.transcript_lookback_seconds = 15  # How many seconds of transcript to capture
```

### Cooldown Period
To prevent spam, there's a 5-second cooldown between messages:
```python
self.cooldown_seconds = 5  # Prevent spam
```

## Requirements

- **macOS** (uses AppleScript to send iMessages)
- **Messages app** signed into iMessage
- **Speech transcription enabled** in config.py
- **Microphone access** for speech recognition

## Testing

Run the test suite to verify functionality:
```bash
python test_peace_sign.py
```

## Troubleshooting

### Messages Not Sending
1. Check that Messages app is signed into iMessage
2. Verify the phone number format (+15109773150)
3. Ensure macOS has permission to control Messages app

### Peace Sign Not Detected
1. Ensure good lighting for hand detection
2. Show clear peace sign with index and middle fingers extended
3. Keep other fingers folded
4. Check that gesture detection is enabled in config.py

### No Transcript Available
1. Ensure speech transcription is enabled
2. Speak clearly before showing peace sign
3. Verify Deepgram API key is valid
4. Check that microphone is working

### Wrong Text Captured
1. The system captures the LAST 15 seconds before the peace sign
2. Wait at least 15 seconds after starting for full buffer
3. Speak clearly and close to the microphone

## Implementation Files

- **imessage_handler.py**: Core iMessage sending logic
- **gesture_detector.py**: Peace sign detection using MediaPipe
- **speech_transcription.py**: Continuous speech transcription with buffer
- **main.py**: Integration of peace sign trigger with iMessage
- **test_peace_sign.py**: Comprehensive test suite

## Security Notes

- Messages are sent to a hardcoded phone number (not configurable at runtime)
- No message history is stored
- Cooldown prevents rapid/accidental sends
- Requires local macOS access (cannot be triggered remotely)