#!/usr/bin/env python3
"""
Test script for peace sign detection and iMessage integration.
"""
import time
from imessage_handler import IMessageHandler


def test_basic_imessage():
    """Test basic iMessage functionality."""
    print("\n=== Test 1: Basic iMessage Sending ===")
    handler = IMessageHandler()

    test_message = "Test message from peace sign detector"
    print(f"Sending test message: {test_message}")

    success = handler.send_imessage(test_message)
    if success:
        print("✅ Test 1 passed: Message sent successfully")
    else:
        print("❌ Test 1 failed: Could not send message")

    return success


def test_transcript_sending():
    """Test sending transcript via iMessage."""
    print("\n=== Test 2: Transcript Sending ===")
    handler = IMessageHandler()

    # Simulate a transcript
    test_transcript = "This is a test transcript. We talked about the meeting tomorrow at 3 PM in the conference room. Don't forget to bring the documents."

    print(f"Sending transcript: {test_transcript[:50]}...")
    success = handler.send_transcript(test_transcript)

    if success:
        print("✅ Test 2 passed: Transcript sent successfully")
    else:
        print("❌ Test 2 failed: Could not send transcript")

    return success


def test_cooldown():
    """Test cooldown functionality."""
    print("\n=== Test 3: Cooldown Test ===")
    handler = IMessageHandler()

    # First message
    print("Sending first message...")
    handler.send_imessage("First message")

    # Check cooldown immediately
    if not handler.can_send():
        print("✅ Cooldown active (expected)")
    else:
        print("❌ Cooldown not active (unexpected)")
        return False

    # Wait for cooldown
    print(f"Waiting {handler.cooldown_seconds} seconds for cooldown...")
    time.sleep(handler.cooldown_seconds + 0.5)

    # Check cooldown after waiting
    if handler.can_send():
        print("✅ Can send after cooldown (expected)")
        # Send second message
        success = handler.send_imessage("Second message after cooldown")
        if success:
            print("✅ Test 3 passed: Cooldown works correctly")
            return True
        else:
            print("❌ Failed to send after cooldown")
            return False
    else:
        print("❌ Still can't send after cooldown (unexpected)")
        return False


def test_empty_transcript():
    """Test handling of empty transcript."""
    print("\n=== Test 4: Empty Transcript Handling ===")
    handler = IMessageHandler()

    # Test with empty string
    print("Testing with empty transcript...")
    success = handler.send_transcript("")

    if not success:
        print("✅ Test 4 passed: Correctly rejected empty transcript")
        return True
    else:
        print("❌ Test 4 failed: Should have rejected empty transcript")
        return False


def test_long_transcript():
    """Test handling of very long transcript."""
    print("\n=== Test 5: Long Transcript Truncation ===")
    handler = IMessageHandler()

    # Create a very long transcript
    long_text = "This is a very long transcript. " * 100  # About 3200 characters

    print(f"Original length: {len(long_text)} characters")
    print("Sending long transcript...")

    success = handler.send_transcript(long_text)

    if success:
        print("✅ Test 5 passed: Long transcript handled successfully (truncated if needed)")
        return True
    else:
        print("❌ Test 5 failed: Could not send long transcript")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Peace Sign iMessage Integration Test Suite")
    print("=" * 60)
    print("\n📱 Testing iMessage integration with peace sign detection")
    print("✌️  Peace sign will trigger sending last 15 seconds of transcript")

    tests = [
        ("Basic iMessage", test_basic_imessage),
        ("Transcript Sending", test_transcript_sending),
        ("Cooldown", test_cooldown),
        ("Empty Transcript", test_empty_transcript),
        ("Long Transcript", test_long_transcript),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' raised an exception: {e}")
            results.append((test_name, False))

        # Small delay between tests
        time.sleep(1)

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
        print("\n🎉 All tests passed! Peace sign iMessage integration is ready.")
        print("\n✌️ To use in the main app:")
        print("1. Start the face recognition app")
        print("2. Enable speech transcription")
        print("3. Speak normally (transcript is captured)")
        print("4. Show a peace sign to send the last 15 seconds of transcript")
    else:
        print(f"\n⚠️  {len(tests) - total_passed} test(s) failed.")


if __name__ == "__main__":
    main()