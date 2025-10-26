"""
Transaction logger for crypto payments.
Logs all successful transactions to CSV and JSON files.
"""
import csv
import json
import os
from datetime import datetime
from typing import Dict, Optional
import config


class TransactionLogger:
    """Logs crypto transactions to file."""
    
    def __init__(self):
        """Initialize the transaction logger."""
        self.log_dir = config.LOGS_DIR
        self.transactions_file = os.path.join(self.log_dir, 'transactions.csv')
        self.transactions_json = os.path.join(self.log_dir, 'transactions.json')
        
        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Initialize CSV file with headers if it doesn't exist
        if not os.path.exists(self.transactions_file):
            self._initialize_csv()
        
        print(f"💾 Transaction Logger initialized")
        print(f"   CSV: {self.transactions_file}")
        print(f"   JSON: {self.transactions_json}")
    
    def _initialize_csv(self):
        """Initialize CSV file with headers."""
        headers = [
            'timestamp',
            'datetime',
            'currency',
            'amount',
            'transaction_digest',
            'recipient_address',
            'recipient_email',
            'sender_name',
            'explorer_url',
            'status'
        ]
        
        with open(self.transactions_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
    
    def log_transaction(
        self,
        amount: float,
        currency: str,
        transaction_digest: str,
        recipient_address: str,
        explorer_url: str = '',
        recipient_email: str = '',
        sender_name: str = '',
        status: str = 'success'
    ) -> None:
        """
        Log a transaction to CSV and JSON files.
        
        Args:
            amount: Amount in the specified currency
            currency: Currency type ('SUI' or 'XRPL')
            transaction_digest: Transaction hash/digest
            recipient_address: Recipient's wallet address
            explorer_url: Block explorer URL
            recipient_email: Email of recipient (for gift-crypto)
            sender_name: Name of sender (for gift-crypto)
            status: Transaction status (success/failed)
        """
        try:
            timestamp = datetime.now().timestamp()
            datetime_str = datetime.now().isoformat()
            
            # Log to CSV
            self._log_to_csv(
                timestamp,
                datetime_str,
                currency,
                amount,
                transaction_digest,
                recipient_address,
                recipient_email,
                sender_name,
                explorer_url,
                status
            )
            
            # Log to JSON
            self._log_to_json(
                timestamp,
                datetime_str,
                currency,
                amount,
                transaction_digest,
                recipient_address,
                recipient_email,
                sender_name,
                explorer_url,
                status
            )
            
            print(f"💾 {currency} transaction logged successfully")
            
        except Exception as e:
            print(f"⚠️  Error logging transaction: {e}")
    
    def _log_to_csv(
        self,
        timestamp: float,
        datetime_str: str,
        currency: str,
        amount: float,
        transaction_digest: str,
        recipient_address: str,
        recipient_email: str,
        sender_name: str,
        explorer_url: str,
        status: str
    ):
        """Log transaction to CSV file."""
        with open(self.transactions_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                datetime_str,
                currency,
                amount,
                transaction_digest,
                recipient_address,
                recipient_email,
                sender_name,
                explorer_url,
                status
            ])
    
    def _log_to_json(
        self,
        timestamp: float,
        datetime_str: str,
        currency: str,
        amount: float,
        transaction_digest: str,
        recipient_address: str,
        recipient_email: str,
        sender_name: str,
        explorer_url: str,
        status: str
    ):
        """Log transaction to JSON file."""
        transaction_entry = {
            'timestamp': timestamp,
            'datetime': datetime_str,
            'currency': currency,
            'amount': amount,
            'transaction_digest': transaction_digest,
            'recipient': {
                'address': recipient_address,
                'email': recipient_email
            },
            'sender_name': sender_name,
            'explorer_url': explorer_url,
            'status': status
        }
        
        # Load existing transactions
        transactions = []
        if os.path.exists(self.transactions_json):
            try:
                with open(self.transactions_json, 'r') as f:
                    transactions = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                transactions = []
        
        # Append new transaction
        transactions.append(transaction_entry)
        
        # Save back to file
        with open(self.transactions_json, 'w') as f:
            json.dump(transactions, f, indent=2)
    
    def get_recent_transactions(self, limit: int = 10) -> list:
        """
        Get recent transactions from JSON log.
        
        Args:
            limit: Maximum number of transactions to return
        
        Returns:
            List of recent transactions
        """
        if not os.path.exists(self.transactions_json):
            return []
        
        try:
            with open(self.transactions_json, 'r') as f:
                transactions = json.load(f)
                return transactions[-limit:] if len(transactions) > limit else transactions
        except Exception as e:
            print(f"⚠️  Error reading transactions: {e}")
            return []
    
    def get_total_sent(self) -> Dict[str, float]:
        """
        Calculate total amount sent across all transactions per currency.
        
        Returns:
            Dictionary with total amounts by currency {'SUI': X, 'XRPL': Y}
        """
        if not os.path.exists(self.transactions_json):
            return {'SUI': 0.0, 'XRPL': 0.0}
        
        try:
            with open(self.transactions_json, 'r') as f:
                transactions = json.load(f)
                
                totals = {'SUI': 0.0, 'XRPL': 0.0}
                
                for tx in transactions:
                    if tx['status'] == 'success':
                        currency = tx.get('currency', 'SUI')  # Default to SUI for old entries
                        amount = tx.get('amount', 0)
                        
                        # Handle old format (with mist/sui nested structure)
                        if isinstance(amount, dict):
                            amount = amount.get('sui', 0)
                            currency = 'SUI'
                        
                        if currency in totals:
                            totals[currency] += amount
                
                return totals
        except Exception as e:
            print(f"⚠️  Error calculating total: {e}")
            return {'SUI': 0.0, 'XRPL': 0.0}

