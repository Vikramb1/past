"""
Composio workflow handler for executing AI-powered workflows triggered by gestures and voice commands.
Interfaces with the TypeScript Composio service to execute workflows using the Composio SDK.
"""
import subprocess
import time
import os
import requests
import re
from typing import Optional, Dict
import config


class ComposioHandler:
    """Handles Composio workflow execution by interfacing with TypeScript service."""

    def __init__(self):
        """Initialize the Composio handler."""
        self.server_process = None
        self.server_url = "http://localhost:3002"
        self.server_ready = False

        # Workflow detection settings
        self.workflow_keyword = "workflow"
        self.workflow_detection_window = 10  # seconds
        self.last_workflow_trigger = 0
        self.workflow_cooldown = 5  # seconds between workflows

        # Gmail authorization status
        self.gmail_authorized = False

        print(f"\n🤖 Composio Workflow Handler initialized")
        print(f"   Server URL: {self.server_url}")
        print(f"   Workflow keyword: '{self.workflow_keyword}'")
        print(f"   Detection window: {self.workflow_detection_window}s")

    def start_server(self) -> bool:
        """
        Start the TypeScript Composio workflow server.

        Returns:
            True if server started successfully, False otherwise
        """
        try:
            # Get the current directory
            current_dir = os.path.dirname(os.path.abspath(__file__))

            # Check if composio-workflow.ts exists
            workflow_file = os.path.join(current_dir, "composio-workflow.ts")
            if not os.path.exists(workflow_file):
                print(f"❌ Composio workflow file not found: {workflow_file}")
                return False

            print(f"\n🚀 Starting Composio workflow server...")
            print(f"Directory: {current_dir}")

            # First, install dependencies if needed
            package_json = os.path.join(current_dir, "package.json")
            if os.path.exists(package_json):
                node_modules = os.path.join(current_dir, "node_modules")
                if not os.path.exists(node_modules):
                    print("📦 Installing npm dependencies...")
                    install_process = subprocess.run(
                        ["npm", "install"],
                        cwd=current_dir,
                        capture_output=True,
                        text=True
                    )
                    if install_process.returncode != 0:
                        print(f"❌ Failed to install dependencies: {install_process.stderr}")
                        return False
                    print("✅ Dependencies installed")

            # Start the server using npx ts-node
            self.server_process = subprocess.Popen(
                ["npx", "ts-node", "composio-workflow.ts"],
                cwd=current_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                env={**os.environ, 'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY', '')}
            )

            # Wait for server to be ready
            print("Waiting for Composio server to start...")
            max_attempts = 30
            for i in range(max_attempts):
                try:
                    response = requests.get(f"{self.server_url}/", timeout=1)
                    if response.status_code == 200:
                        self.server_ready = True
                        print(f"✅ Composio workflow server ready at {self.server_url}")

                        # Check Gmail authorization status
                        self._check_authorization()
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(1)
                    if i % 5 == 0:
                        print(f"  Still waiting... ({i + 1}/{max_attempts})")

            print("⚠️  Server did not respond, but continuing...")
            return True

        except FileNotFoundError:
            print("❌ npx or ts-node not found. Please install Node.js and run 'npm install'")
            return False
        except Exception as e:
            print(f"❌ Failed to start Composio server: {e}")
            return False

    def stop_server(self):
        """Stop the TypeScript Composio workflow server."""
        if self.server_process:
            print("\n🛑 Stopping Composio workflow server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
                print("✅ Composio server stopped")
            except subprocess.TimeoutExpired:
                print("⚠️  Server didn't stop gracefully, forcing...")
                self.server_process.kill()
                self.server_process.wait()
            self.server_process = None
            self.server_ready = False

    def _check_authorization(self):
        """Check if Gmail is authorized."""
        try:
            response = requests.get(f"{self.server_url}/auth-status", timeout=5)
            if response.status_code == 200:
                result = response.json()
                self.gmail_authorized = result.get('authorized', False)
                auth_config = result.get('authConfig', 'unknown')
                if self.gmail_authorized:
                    print(f"✅ Gmail is authorized via auth config: {auth_config}")
                else:
                    print(f"⚠️  Gmail not authorized. Check auth config: {auth_config}")
        except Exception as e:
            print(f"⚠️  Could not check authorization status: {e}")
            self.gmail_authorized = False

    def authorize_gmail(self):
        """
        Check Gmail authorization status.
        With auth config, Gmail is already connected.
        """
        if not self.server_ready:
            print("❌ Server not ready. Start the server first.")
            return None

        try:
            print(f"\n🔗 Checking Gmail connection...")
            response = requests.get(f"{self.server_url}/authorize", timeout=10)

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    auth_config = result.get('authConfig')
                    print(f"✅ Gmail already connected via auth config: {auth_config}")
                    print(f"   No additional authorization needed!")
                    return True
                else:
                    print(f"❌ Error: {result.get('error')}")
                    return False
            else:
                print(f"❌ Server error: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Failed to check authorization: {e}")
            return False

    def detect_workflow_trigger(self, recent_transcription: str) -> bool:
        """
        Check if the workflow keyword was mentioned in recent speech.

        Args:
            recent_transcription: Recent transcription text

        Returns:
            True if workflow should be triggered
        """
        if not recent_transcription:
            return False

        # Check if workflow keyword is in transcription
        text_lower = recent_transcription.lower()
        if self.workflow_keyword in text_lower:
            # Check cooldown
            current_time = time.time()
            if current_time - self.last_workflow_trigger < self.workflow_cooldown:
                remaining = self.workflow_cooldown - (current_time - self.last_workflow_trigger)
                print(f"⏳ Workflow cooldown active: {remaining:.1f}s remaining")
                return False

            self.last_workflow_trigger = current_time
            return True

        return False

    def parse_workflow_command(self, transcription: str) -> Optional[str]:
        """
        Extract the command that comes after the workflow keyword.

        Args:
            transcription: Full transcription text

        Returns:
            Command text after 'workflow' keyword, or None if not found
        """
        if not transcription:
            return None

        # Find text after "workflow" keyword
        text_lower = transcription.lower()
        workflow_index = text_lower.find(self.workflow_keyword)

        if workflow_index == -1:
            return None

        # Extract action text (everything after "workflow")
        command_text = transcription[workflow_index + len(self.workflow_keyword):].strip()

        if not command_text:
            print("⚠️  No command specified after workflow keyword")
            return None

        print(f"📝 Extracted command: '{command_text}'")
        return command_text

    def execute_workflow(
        self,
        command: str,
        person_info: Optional[Dict] = None,
        focused_person_email: Optional[str] = None
    ) -> Dict:
        """
        Execute the workflow command using the TypeScript Composio service.

        Args:
            command: The command to execute (text after 'workflow')
            person_info: Information about the person in focus
            focused_person_email: Email of the person in focus (if available)

        Returns:
            Result dictionary with success status and details
        """
        if not self.server_ready:
            print("❌ Composio server not ready")
            return {
                'success': False,
                'error': 'Composio server not ready',
                'command': command
            }

        print(f"\n🚀 Executing workflow command: '{command}'")

        # Extract email from person info if not provided
        if not focused_person_email and person_info:
            focused_person_email = self._extract_email_from_person_info(person_info)
            if focused_person_email:
                print(f"📧 Extracted email from person info: {focused_person_email}")

        try:
            # Prepare request payload
            payload = {
                'command': command,
                'personInfo': person_info,
                'focusedPersonEmail': focused_person_email
            }

            # Send request to TypeScript service
            response = requests.post(
                f"{self.server_url}/execute-workflow",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ Workflow executed successfully!")
                    if 'result' in result:
                        print(f"   Result: {result['result']}")
                    elif 'aiResponse' in result:
                        print(f"   AI Response: {result['aiResponse']}")
                    return result
                else:
                    print(f"❌ Workflow failed: {result.get('error')}")
                    return result
            else:
                print(f"❌ Server error: {response.status_code}")
                return {
                    'success': False,
                    'error': f'Server returned status {response.status_code}',
                    'command': command
                }

        except requests.exceptions.Timeout:
            print("❌ Request timed out")
            return {
                'success': False,
                'error': 'Request timed out',
                'command': command
            }
        except Exception as e:
            print(f"❌ Workflow execution error: {e}")
            return {
                'success': False,
                'error': str(e),
                'command': command
            }

    def _extract_email_from_person_info(self, person_info: Dict) -> Optional[str]:
        """
        Extract email address from person info data using the TypeScript service.

        Args:
            person_info: Person information dictionary

        Returns:
            Email address if found, None otherwise
        """
        if not self.server_ready:
            # Fallback to local extraction
            summary = person_info.get('summary', '')
            if summary:
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                matches = re.findall(email_pattern, summary)
                if matches:
                    return matches[0]
            return None

        try:
            response = requests.post(
                f"{self.server_url}/extract-email",
                json={'personInfo': person_info},
                timeout=5
            )

            if response.status_code == 200:
                result = response.json()
                return result.get('email')

        except Exception:
            # Fallback to local extraction
            summary = person_info.get('summary', '')
            if summary:
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                matches = re.findall(email_pattern, summary)
                if matches:
                    return matches[0]

        return None

    def can_execute_workflow(self) -> bool:
        """
        Check if a workflow can be executed (cooldown check).

        Returns:
            True if cooldown period has passed
        """
        current_time = time.time()
        time_since_last = current_time - self.last_workflow_trigger

        return time_since_last >= self.workflow_cooldown

    def get_status(self) -> Dict:
        """
        Get current status of the workflow handler.

        Returns:
            Status dictionary
        """
        return {
            'server_ready': self.server_ready,
            'gmail_authorized': self.gmail_authorized,
            'workflow_keyword': self.workflow_keyword,
            'detection_window': self.workflow_detection_window,
            'cooldown': self.workflow_cooldown,
            'can_execute': self.can_execute_workflow()
        }