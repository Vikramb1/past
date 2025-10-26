"""
Crypto payment handler for sending multi-chain cryptocurrency (SUI & XRPL) via gesture triggers.
Manages Node.js server subprocess and handles payment API calls.
"""
import subprocess
import time
import os
import sys
import requests
from typing import Optional, Dict
import config
from transaction_logger import TransactionLogger


class CryptoPaymentHandler:
    """Handles multi-chain crypto payments triggered by gestures."""
    
    def __init__(self):
        """Initialize the crypto payment handler."""
        self.server_process = None
        self.last_payment_time = 0
        self.payment_cooldown = config.PAYMENT_COOLDOWN
        self.server_url = "http://localhost:3001"  # Updated to match server port
        self.server_ready = False
        
        # Initialize transaction logger
        self.transaction_logger = TransactionLogger()
        
        print(f"\nMulti-Chain Crypto Payment Handler initialized")
        print(f"Supported chains: SUI, XRPL")
        print(f"Payment cooldown: {self.payment_cooldown}s")
        print(f"Default SUI amount: {config.DEFAULT_PAYMENT_AMOUNT_SUI} SUI")
        print(f"Default XRPL amount: {config.DEFAULT_PAYMENT_AMOUNT_XRPL} XRPL")
    
    def start_server(self) -> bool:
        """
        Start the Node.js crypto server.
        
        Returns:
            True if server started successfully, False otherwise
        """
        try:
            # Get the crypto-stuff directory path
            crypto_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), config.CRYPTO_SERVER_PATH)
            )
            
            if not os.path.exists(crypto_path):
                print(f"❌ Crypto server directory not found: {crypto_path}")
                return False
            
            suicrypto_file = os.path.join(crypto_path, "suicrypto.ts")
            if not os.path.exists(suicrypto_file):
                print(f"❌ suicrypto.ts not found in {crypto_path}")
                return False
            
            print(f"\n🚀 Starting crypto server...")
            print(f"Directory: {crypto_path}")
            
            # Start the server using npx ts-node
            self.server_process = subprocess.Popen(
                ["npx", "ts-node", "suicrypto.ts"],
                cwd=crypto_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Wait for server to be ready (check root endpoint)
            print("Waiting for server to start...")
            max_attempts = 30
            for i in range(max_attempts):
                try:
                    response = requests.get(f"{self.server_url}/", timeout=1)
                    if response.status_code == 200:
                        self.server_ready = True
                        print(f"✅ Crypto server ready at {self.server_url}")
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(1)
                    if i % 5 == 0:
                        print(f"  Still waiting... ({i + 1}/{max_attempts})")
            
            print("⚠️  Server did not respond to health check, but continuing...")
            print("   Payment functionality may not work until server is fully ready.")
            return True
            
        except FileNotFoundError:
            print("❌ npx or ts-node not found. Please install Node.js and run 'npm install' in crypto-stuff/")
            return False
        except Exception as e:
            print(f"❌ Failed to start crypto server: {e}")
            return False
    
    def stop_server(self):
        """Stop the Node.js crypto server."""
        if self.server_process:
            print("\n🛑 Stopping crypto server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
                print("✅ Crypto server stopped")
            except subprocess.TimeoutExpired:
                print("⚠️  Server didn't stop gracefully, forcing...")
                self.server_process.kill()
                self.server_process.wait()
            self.server_process = None
            self.server_ready = False
    
    def can_send_payment(self) -> bool:
        """
        Check if a payment can be sent (cooldown check).
        
        Returns:
            True if cooldown period has passed, False otherwise
        """
        current_time = time.time()
        time_since_last = current_time - self.last_payment_time
        
        if time_since_last < self.payment_cooldown:
            remaining = self.payment_cooldown - time_since_last
            print(f"⏳ Payment cooldown active: {remaining:.1f}s remaining")
            return False
        
        return True
    
    def send_payment(self, amount: Optional[float] = None, currency: str = 'SUI', display_text: str = None) -> Dict:
        """
        Send a crypto payment via the API (supports both SUI and XRPL).
        
        Args:
            amount: Amount to send in the specified currency
            currency: Currency type ('SUI' or 'XRPL')
            display_text: Display text for currency (e.g., 'XRP', 'XRPL', 'SUI')
        
        Returns:
            Dictionary with success status and transaction details
        """
        if not self.server_ready:
            return {
                'success': False,
                'message': 'Server not ready',
                'error': 'Crypto server is still starting up'
            }
        
        # Set default display text if not provided
        if display_text is None:
            display_text = 'XRP' if currency == 'XRPL' else 'SUI'
        
        # Route to the correct payment method
        if currency == 'XRPL':
            return self._send_xrpl_payment(amount, display_text)
        else:
            return self._send_sui_payment(amount, display_text)
    
    def _send_sui_payment(self, amount_sui: Optional[float] = None, display_text: str = 'SUI') -> Dict:
        """
        Send a SUI payment via the API.
        
        Args:
            amount_sui: Amount to send in SUI (default: config.DEFAULT_PAYMENT_AMOUNT_SUI)
            display_text: Display text for currency (default: 'SUI')
        
        Returns:
            Dictionary with success status and transaction details
        """
        # Use provided amount or default from config
        if amount_sui is None:
            amount_sui = config.DEFAULT_PAYMENT_AMOUNT_SUI
        
        # Convert to MIST (1 SUI = 1,000,000,000 MIST)
        amount_mist = int(amount_sui * 1_000_000_000)
        
        try:
            print("\n💸 Initiating SUI crypto gift payment...")
            print(f"Amount: {amount_mist} MIST ({amount_sui} SUI)")
            print(f"Generating new SUI wallet for recipient...")
            
            # Prepare the gift-crypto request
            # This endpoint generates a new wallet for the recipient and emails them
            recipient_email = getattr(config, 'RECIPIENT_EMAIL', 'sanjay.amirthraj@gmail.com')
            sender_name = getattr(config, 'SENDER_NAME', 'Face Recognition Payment System')
            
            payload = {
                'senderPrivateKey': config.FUNDED_WALLET_PRIVATE_KEY,
                'recipientEmail': recipient_email,
                'amount': amount_mist,
                'senderName': sender_name
            }
            
            print(f"Email will be sent to: {recipient_email}")
            
            # Send the gift-crypto request
            response = requests.post(
                f"{self.server_url}/gift-crypto",
                json=payload,
                timeout=30
            )
            
            result = response.json()
            
            if result.get('success'):
                # Update last payment time
                self.last_payment_time = time.time()
                
                # Extract transaction details from gift-crypto response
                transaction = result.get('transaction', {})
                recipient = result.get('recipient', {})
                
                print(f"✅ SUI crypto gift successful!")
                print(f"Transaction: {transaction.get('digest', 'N/A')}")
                print(f"New wallet address: {recipient.get('address', 'N/A')}")
                print(f"Explorer: {transaction.get('explorerUrl', 'N/A')}")
                
                # Log the transaction
                self.transaction_logger.log_transaction(
                    amount=amount_sui,
                    currency='SUI',
                    transaction_digest=transaction.get('digest', 'unknown'),
                    recipient_address=recipient.get('address', 'unknown'),
                    explorer_url=transaction.get('explorerUrl', ''),
                    recipient_email=recipient_email,
                    sender_name=sender_name,
                    status='success'
                )
                
                return {
                    'success': True,
                    'currency': 'SUI',
                    'transactionDigest': transaction.get('digest'),
                    'explorerUrl': transaction.get('explorerUrl'),
                    'amount': amount_sui,
                    'amountDisplay': f"{amount_sui} {display_text}",
                    'recipientAddress': recipient.get('address'),
                    'message': 'SUI crypto gift sent successfully'
                }
            else:
                error_msg = result.get('message', 'Unknown error')
                print(f"❌ SUI payment failed: {error_msg}")
                
                return {
                    'success': False,
                    'currency': 'SUI',
                    'message': error_msg,
                    'error': result.get('error', 'Transaction failed')
                }
        
        except requests.exceptions.Timeout:
            print("❌ SUI payment request timed out")
            return {
                'success': False,
                'currency': 'SUI',
                'message': 'Request timed out',
                'error': 'Server took too long to respond'
            }
        
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to crypto server")
            return {
                'success': False,
                'currency': 'SUI',
                'message': 'Server not reachable',
                'error': 'Failed to connect to localhost:3001'
            }
        
        except Exception as e:
            print(f"❌ SUI payment error: {e}")
            return {
                'success': False,
                'currency': 'SUI',
                'message': str(e),
                'error': f'Unexpected error: {type(e).__name__}'
            }
    
    def _send_xrpl_payment(self, amount_xrpl: Optional[float] = None, display_text: str = 'XRP') -> Dict:
        """
        Send an XRPL payment via the API.
        
        Args:
            amount_xrpl: Amount to send in XRPL/XRP (default: config.DEFAULT_PAYMENT_AMOUNT_XRPL)
            display_text: Display text for currency (e.g., 'XRP' or 'XRPL')
        
        Returns:
            Dictionary with success status and transaction details
        """
        # Use provided amount or default from config
        if amount_xrpl is None:
            amount_xrpl = config.DEFAULT_PAYMENT_AMOUNT_XRPL
        
        try:
            print("\n💸 Initiating XRPL crypto gift payment...")
            print(f"Amount: {amount_xrpl} XRP")
            print(f"Generating new XRPL EVM wallet for recipient...")
            
            # Prepare the XRPL gift-crypto request
            recipient_email = getattr(config, 'RECIPIENT_EMAIL', 'sanjay.amirthraj@gmail.com')
            sender_name = getattr(config, 'SENDER_NAME', 'Face Recognition Payment System')
            
            payload = {
                'senderPrivateKey': config.XRPL_FUNDED_WALLET_PRIVATE_KEY,
                'recipientEmail': recipient_email,
                'amount': str(amount_xrpl),  # Send as string for consistency
                'senderName': sender_name
            }
            
            print(f"Email will be sent to: {recipient_email}")
            
            # Send the XRPL gift-crypto request
            response = requests.post(
                f"{self.server_url}/xrpl/gift-crypto",
                json=payload,
                timeout=30
            )
            
            result = response.json()
            
            if result.get('success'):
                # Update last payment time
                self.last_payment_time = time.time()
                
                # Extract transaction details from XRPL gift-crypto response
                transaction = result.get('transaction', {})
                recipient = result.get('recipient', {})
                
                print(f"✅ XRPL crypto gift successful!")
                print(f"Transaction: {transaction.get('hash', 'N/A')}")
                print(f"New wallet address: {recipient.get('address', 'N/A')}")
                print(f"Explorer: {transaction.get('explorerUrl', 'N/A')}")
                
                # Log the transaction
                self.transaction_logger.log_transaction(
                    amount=amount_xrpl,
                    currency='XRPL',
                    transaction_digest=transaction.get('hash', 'unknown'),
                    recipient_address=recipient.get('address', 'unknown'),
                    explorer_url=transaction.get('explorerUrl', ''),
                    recipient_email=recipient_email,
                    sender_name=sender_name,
                    status='success'
                )
                
                return {
                    'success': True,
                    'currency': 'XRPL',
                    'transactionDigest': transaction.get('hash'),
                    'explorerUrl': transaction.get('explorerUrl'),
                    'amount': amount_xrpl,
                    'amountDisplay': f"{amount_xrpl} {display_text}",
                    'recipientAddress': recipient.get('address'),
                    'message': 'XRPL crypto gift sent successfully'
                }
            else:
                error_msg = result.get('message', 'Unknown error')
                print(f"❌ XRPL payment failed: {error_msg}")
                
                return {
                    'success': False,
                    'currency': 'XRPL',
                    'message': error_msg,
                    'error': result.get('error', 'Transaction failed')
                }
        
        except requests.exceptions.Timeout:
            print("❌ XRPL payment request timed out")
            return {
                'success': False,
                'currency': 'XRPL',
                'message': 'Request timed out',
                'error': 'Server took too long to respond'
            }
        
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to crypto server")
            return {
                'success': False,
                'currency': 'XRPL',
                'message': 'Server not reachable',
                'error': 'Failed to connect to localhost:3001'
            }
        
        except Exception as e:
            print(f"❌ XRPL payment error: {e}")
            return {
                'success': False,
                'currency': 'XRPL',
                'message': str(e),
                'error': f'Unexpected error: {type(e).__name__}'
            }
    
    def get_cooldown_remaining(self) -> float:
        """
        Get remaining cooldown time in seconds.
        
        Returns:
            Seconds remaining in cooldown, or 0 if no cooldown active
        """
        current_time = time.time()
        time_since_last = current_time - self.last_payment_time
        remaining = self.payment_cooldown - time_since_last
        
        return max(0, remaining)
    
    def get_transaction_stats(self) -> Dict:
        """
        Get transaction statistics.
        
        Returns:
            Dictionary with transaction stats
        """
        total = self.transaction_logger.get_total_sent()
        recent = self.transaction_logger.get_recent_transactions(limit=5)
        
        return {
            'total_sent': total,
            'transaction_count': len(recent),
            'recent_transactions': recent
        }

