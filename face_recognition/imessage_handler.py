"""
iMessage handler for sending messages on macOS.
Uses AppleScript to send messages via the Messages app.
"""
import subprocess
import time
from typing import Optional, Tuple
import re


class IMessageHandler:
    """Handles sending iMessages on macOS."""

    def __init__(self):
        """Initialize the iMessage handler."""
        self.phone_number = "+15109773150"
        self.last_send_time = 0
        self.cooldown_seconds = 5  # Prevent spam
        self.transcript_lookback_seconds = 15  # How many seconds of transcript to capture

        print(f"\n📱 iMessage Handler initialized")
        print(f"   Phone number: {self.phone_number}")
        print(f"   Will capture last {self.transcript_lookback_seconds} seconds of transcript")
        print(f"   Trigger: Peace sign gesture ✌️")

    def send_imessage(self, message: str) -> bool:
        """
        Send an iMessage using AppleScript.

        Args:
            message: The message text to send

        Returns:
            True if sent successfully, False otherwise
        """
        # Check cooldown
        current_time = time.time()
        if current_time - self.last_send_time < self.cooldown_seconds:
            remaining = self.cooldown_seconds - (current_time - self.last_send_time)
            print(f"⏳ Cooldown active: {remaining:.1f}s remaining")
            return False

        # Clean the message
        message = message.strip()
        if not message:
            print("⚠️  Empty message, not sending")
            return False

        # Escape quotes for AppleScript
        message = message.replace('"', '\\"')

        # Create AppleScript command
        applescript = f'''
        tell application "Messages"
            set targetService to 1st service whose service type = iMessage
            set targetBuddy to buddy "{self.phone_number}" of targetService
            send "{message}" to targetBuddy
        end tell
        '''

        try:
            # Execute AppleScript
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                self.last_send_time = current_time
                print(f"✅ iMessage sent to {self.phone_number}")
                print(f"   Message: {message[:100]}...")
                return True
            else:
                print(f"❌ Failed to send iMessage: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("❌ AppleScript timed out")
            return False
        except Exception as e:
            print(f"❌ Error sending iMessage: {e}")
            return False

    def can_send(self) -> bool:
        """
        Check if we can send a message (cooldown check).

        Returns:
            True if cooldown period has passed
        """
        current_time = time.time()
        return current_time - self.last_send_time >= self.cooldown_seconds

    def send_transcript(self, transcript: str) -> bool:
        """
        Send the provided transcript via iMessage.

        Args:
            transcript: The transcript text to send

        Returns:
            True if sent successfully, False otherwise
        """
        if not transcript or not transcript.strip():
            print("⚠️  No transcript to send")
            return False

        # Clean up the transcript
        transcript = transcript.strip()

        # Truncate if too long (iMessage has limits)
        max_length = 1000
        if len(transcript) > max_length:
            transcript = transcript[:max_length] + "..."

        print(f"\n📱 Sending last {self.transcript_lookback_seconds}s of transcript via iMessage")
        print(f"   Preview: {transcript[:100]}...")

        return self.send_imessage(transcript)

    def get_status(self) -> dict:
        """
        Get the current status of the handler.

        Returns:
            Status dictionary
        """
        return {
            'phone_number': self.phone_number,
            'lookback_seconds': self.transcript_lookback_seconds,
            'cooldown': self.cooldown_seconds,
            'can_send': self.can_send()
        }