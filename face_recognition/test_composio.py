#!/usr/bin/env python3
"""
Test script for Composio workflow integration.
Sends a test email using the Composio service.
"""
import time
import requests
import subprocess
import os
import sys


def test_composio_workflow():
    """Test the Composio workflow by sending an email."""

    # Server URL
    server_url = "http://localhost:3002"

    print("🚀 Starting Composio Workflow Test\n")
    print("=" * 60)

    # Start the TypeScript server
    print("1️⃣  Starting Composio workflow server...")
    current_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        # Start the server
        server_process = subprocess.Popen(
            ["npx", "ts-node", "composio-workflow.ts"],
            cwd=current_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        # Wait for server to start
        print("   Waiting for server to be ready...")
        max_attempts = 30
        server_ready = False

        for i in range(max_attempts):
            try:
                response = requests.get(f"{server_url}/", timeout=1)
                if response.status_code == 200:
                    server_ready = True
                    print("   ✅ Server is ready!\n")
                    break
            except requests.exceptions.RequestException:
                time.sleep(1)
                if i % 5 == 0 and i > 0:
                    print(f"   Still waiting... ({i}/{max_attempts})")

        if not server_ready:
            print("   ❌ Server failed to start")
            return False

        # Check authorization status
        print("2️⃣  Checking Gmail authorization...")
        response = requests.get(f"{server_url}/auth-status", timeout=5)

        if response.status_code == 200:
            result = response.json()
            if result.get('authorized'):
                print(f"   ✅ Gmail is authorized")
                print(f"   Auth config: {result.get('authConfig')}\n")
            else:
                print(f"   ❌ Gmail not authorized")
                print(f"   Error: {result.get('error')}")
                return False
        else:
            print(f"   ❌ Failed to check auth status")
            return False

        # Send test email
        print("3️⃣  Sending test email...")
        print("   To: sanjay.amirthraj@gmail.com")
        print("   Message: Hi from CalHacks!\n")

        # Prepare the workflow command
        workflow_command = "send an email to sanjay.amirthraj@gmail.com with subject 'Test from CalHacks' and body 'Hi from CalHacks! This is a test email sent via the Composio workflow integration. The face recognition system with workflow automation is working!'"

        payload = {
            'command': workflow_command,
            'personInfo': None,
            'focusedPersonEmail': None
        }

        print("   Executing workflow...")
        response = requests.post(
            f"{server_url}/execute-workflow",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("\n   ✅ Email sent successfully!")
                print(f"   Command: {result.get('command')}")
                if 'result' in result:
                    print(f"   Result: {result.get('result')}")
                print("\n" + "=" * 60)
                print("🎉 Test completed successfully!")
                print("Check sanjay.amirthraj@gmail.com inbox for the email.")
                return True
            else:
                print(f"\n   ❌ Failed to send email")
                print(f"   Error: {result.get('error')}")
                return False
        else:
            print(f"\n   ❌ Server error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Stop the server
        if 'server_process' in locals():
            print("\n🛑 Stopping server...")
            try:
                server_process.terminate()
                server_process.wait(timeout=5)
                print("   Server stopped")
            except:
                server_process.kill()
                print("   Server killed")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("COMPOSIO WORKFLOW TEST")
    print("=" * 60)

    # Run the test
    success = test_composio_workflow()

    # Exit with appropriate code
    sys.exit(0 if success else 1)