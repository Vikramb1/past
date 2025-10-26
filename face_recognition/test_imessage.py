#!/usr/bin/env python3
"""
Test script for the iMessage handler.
Tests sending messages and trigger detection.
"""
import time
from imessage_handler import IMessageHandler


def test_basic_send():
    """Test basic iMessage sending."""
    print("\n=== Test 1: Basic iMessage Sending ===")
    handler = IMessageHandler()

    # Test sending a simple message
    print("Sending test message...")
    success = handler.send_imessage("Test message from face recognition system")

    if success:
        print("✅ Test 1 passed: Message sent successfully")
    else:
        print("❌ Test 1 failed: Could not send message")

    return success


def test_trigger_detection():
    """Test trigger phrase detection."""
    print("\n=== Test 2: Trigger Phrase Detection ===")
    handler = IMessageHandler()

    # Test cases
    test_cases = [
        ("Hello world", False),
        ("Send an email to John", True),
        ("Please send an email now", True),
        ("SEND AN EMAIL PLEASE", True),
        ("I need to send a message", False),
    ]

    all_passed = True
    for text, expected in test_cases:
        result = handler.detect_trigger_phrase(text)
        if result == expected:
            print(f"✅ '{text}' -> {result} (expected: {expected})")
        else:
            print(f"❌ '{text}' -> {result} (expected: {expected})")
            all_passed = False

    return all_passed


def test_transcription_processing():
    """Test transcription processing with capture window."""
    print("\n=== Test 3: Transcription Processing ===")
    handler = IMessageHandler()

    # Simulate transcription segments
    segments = [
        {"text": "Hello world", "timestamp": time.time()},
        {"text": "I need to send an email", "timestamp": time.time() + 0.5},
        {"text": "to my colleague John", "timestamp": time.time() + 1.0},
        {"text": "about the meeting tomorrow", "timestamp": time.time() + 1.5},
        {"text": "at 3 PM", "timestamp": time.time() + 2.5},  # After capture window
        {"text": "in the conference room", "timestamp": time.time() + 3.0},
    ]

    captured_message = None
    for segment in segments:
        print(f"Processing: '{segment['text']}' at {segment['timestamp']:.1f}")
        result = handler.process_transcription(segment)

        if result:
            captured_message = result
            print(f"\n✅ Message captured: '{captured_message}'")
            break

        time.sleep(0.1)  # Small delay between segments

    if captured_message:
        print("\n✅ Test 3 passed: Transcription processing works")
        return True
    else:
        print("\n❌ Test 3 failed: No message captured")
        return False


def test_full_flow():
    """Test the full flow: detect trigger, capture, and send."""
    print("\n=== Test 4: Full Flow Test ===")
    handler = IMessageHandler()

    # Simulate a conversation
    print("Simulating conversation...")
    segments = [
        {"text": "Let me check my calendar", "timestamp": time.time()},
        {"text": "Oh wait, I need to send an email", "timestamp": time.time() + 1.0},
        {"text": "Meeting rescheduled to Friday", "timestamp": time.time() + 1.5},
        {"text": "at 2 PM in room 301", "timestamp": time.time() + 2.0},
        {"text": "Thank you", "timestamp": time.time() + 3.5},
    ]

    message_to_send = None
    for i, segment in enumerate(segments):
        print(f"\nSegment {i+1}: '{segment['text']}'")
        result = handler.process_transcription(segment)

        if result:
            message_to_send = result
            print(f"\n📱 Captured message: '{message_to_send}'")
            break

        time.sleep(0.2)

    if message_to_send:
        print("\nSending captured message...")
        success = handler.send_imessage(message_to_send)

        if success:
            print("✅ Test 4 passed: Full flow completed successfully")
            return True
        else:
            print("❌ Test 4 failed: Could not send captured message")
            return False
    else:
        print("❌ Test 4 failed: No message captured")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("iMessage Handler Test Suite")
    print("=" * 60)

    tests = [
        ("Basic Send", test_basic_send),
        ("Trigger Detection", test_trigger_detection),
        ("Transcription Processing", test_transcription_processing),
        ("Full Flow", test_full_flow),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' raised an exception: {e}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    total_passed = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {total_passed}/{len(tests)} tests passed")

    if total_passed == len(tests):
        print("\n🎉 All tests passed! iMessage handler is ready.")
    else:
        print(f"\n⚠️  {len(tests) - total_passed} test(s) failed.")


if __name__ == "__main__":
    main()