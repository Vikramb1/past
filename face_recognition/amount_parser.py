"""
Amount parser module using Ollama (llama3.2) to extract crypto amounts from text.
Parses natural language commands like "send 0.5 SUI" or "send 0.0001 XRPL".
Supports both SUI and XRPL (XRP) cryptocurrencies.
"""
import re
from typing import Optional, Tuple
import ollama
import config


class AmountParser:
    """Parses crypto amounts from transcribed speech using Ollama LLM."""
    
    def __init__(self):
        """Initialize the amount parser."""
        self.model = config.OLLAMA_MODEL
        self.default_amount_sui = config.DEFAULT_PAYMENT_AMOUNT_SUI
        self.default_amount_xrpl = config.DEFAULT_PAYMENT_AMOUNT_XRPL
        
        # Word to number mapping for spoken numbers
        self.word_to_num = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
            'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
            'ten': 10, 'twenty': 20, 'thirty': 30, 'forty': 40,
            'fifty': 50, 'hundred': 100, 'thousand': 1000
        }
        
        print(f"\n🧠 Amount Parser initialized")
        print(f"Model: {self.model}")
        print(f"Default SUI amount: {self.default_amount_sui} SUI")
        print(f"Default XRPL amount: {self.default_amount_xrpl} XRPL")
    
    def parse_amount(self, text: str) -> Tuple[Optional[float], str, str]:
        """
        Parse crypto amount from text using multiple strategies.
        
        Args:
            text: Transcribed text to parse
        
        Returns:
            Tuple of (amount, currency, display_text)
            - amount: Parsed amount or None if not found
            - currency: 'SUI' or 'XRPL'
            - display_text: Original currency text from speech (e.g., 'XRP', 'XRPL', 'SUI')
        """
        if not text or not text.strip():
            return None, 'SUI', 'SUI'
        
        print(f"\n💭 Parsing: '{text}'")
        
        # Strategy 1: Try regex patterns first (faster)
        result = self._parse_with_regex(text)
        if result is not None:
            amount, currency, display_text = result
            print(f"✅ Regex parsed: {amount} {display_text}")
            return amount, currency, display_text
        
        # Strategy 2: Use Ollama LLM for complex parsing
        result = self._parse_with_ollama(text)
        if result is not None:
            amount, currency, display_text = result
            print(f"✅ LLM parsed: {amount} {display_text}")
            return amount, currency, display_text
        
        print(f"ℹ️  No amount detected, using default: {self.default_amount_sui} SUI")
        return None, 'SUI', 'SUI'
    
    def _parse_with_regex(self, text: str) -> Optional[Tuple[float, str, str]]:
        """
        Parse amount using regex patterns for both SUI and XRPL.
        
        Args:
            text: Text to parse
        
        Returns:
            Tuple of (amount, currency, display_text) or None
        """
        text_lower = text.lower()
        
        # XRPL Patterns (check first since XRPL is more specific)
        # Pattern: "send 0.5 XRPL" or "send 0.5 XRP" or "send 0.5 of XRPL"
        xrpl_patterns = [
            (r'(?:send\s+)?(\d+\.?\d*)\s*(?:of\s+)?xrpl\b', 'XRPL'),
            (r'(?:send\s+)?(\d+\.?\d*)\s*(?:of\s+)?xrp\b', 'XRP'),
            (r'(?:send\s+)?(\.\d+)\s*(?:of\s+)?xrpl\b', 'XRPL'),
            (r'(?:send\s+)?(\.\d+)\s*(?:of\s+)?xrp\b', 'XRP'),
        ]
        
        for pattern, display_name in xrpl_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    amount = float(match.group(1))
                    return amount, 'XRPL', display_name
                except ValueError:
                    pass
        
        # SUI Patterns
        sui_patterns = [
            (r'(?:send\s+)?(\d+\.?\d*)\s*(?:of\s+)?sui\b', 'SUI'),
            (r'(?:send\s+)?(\.\d+)\s*(?:of\s+)?sui\b', 'SUI'),
        ]
        
        for pattern, display_name in sui_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    amount = float(match.group(1))
                    return amount, 'SUI', display_name
                except ValueError:
                    pass
        
        return None
    
    def _parse_with_ollama(self, text: str) -> Optional[Tuple[float, str, str]]:
        """
        Parse amount and currency using Ollama LLM.
        
        Args:
            text: Text to parse
        
        Returns:
            Tuple of (amount, currency, display_text) or None
        """
        try:
            prompt = f"""Extract the cryptocurrency amount and type from this text. Return the amount and currency type.

Examples:
- "send 0.5 SUI" -> 0.5 SUI
- "send five XRP" -> 5 XRP
- "transfer 0.0001 XRPL" -> 0.0001 XRPL
- "send one point five SUI" -> 1.5 SUI

Text: "{text}"

Response (amount and currency):"""
            
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': 0.1,  # Low temperature for deterministic output
                    'num_predict': 30,   # Short response expected
                }
            )
            
            # Extract the response
            result = response['response'].strip().lower()
            
            # Try to extract amount and currency
            numbers = re.findall(r'\d+\.?\d*', result)
            if not numbers:
                return None
            
            amount = float(numbers[0])
            
            # Detect currency
            if 'xrpl' in result or 'xrp' in result:
                # Preserve the original text for display
                if 'xrpl' in result:
                    return amount, 'XRPL', 'XRPL'
                else:
                    return amount, 'XRPL', 'XRP'
            elif 'sui' in result:
                return amount, 'SUI', 'SUI'
            else:
                # Default to SUI if no currency detected
                return amount, 'SUI', 'SUI'
            
        except Exception as e:
            print(f"⚠️  Ollama parsing error: {e}")
            return None
    
    def validate_amount(self, amount: Optional[float], currency: str = 'SUI', display_text: str = 'SUI') -> Tuple[bool, Optional[float], str, str, str]:
        """
        Validate parsed amount is reasonable.
        
        Args:
            amount: Parsed amount to validate
            currency: Currency type ('SUI' or 'XRPL')
            display_text: Display text for currency (e.g., 'XRP', 'XRPL', 'SUI')
        
        Returns:
            Tuple of (is_valid, validated_amount, message, currency, display_text)
        """
        # Use defaults if amount is None
        if amount is None:
            if currency == 'XRPL':
                return True, self.default_amount_xrpl, f"Using default: {self.default_amount_xrpl} {display_text}", currency, display_text
            else:
                return True, self.default_amount_sui, f"Using default: {self.default_amount_sui} {display_text}", currency, display_text
        
        # Check for negative
        if amount < 0:
            return False, None, "Amount cannot be negative", currency, display_text
        
        # Check for zero
        if amount == 0:
            return False, None, "Amount cannot be zero", currency, display_text
        
        # Check for unreasonably large amounts (safety check)
        if amount > 1000:
            return False, None, f"Amount too large: {amount} {display_text} (max: 1000)", currency, display_text
        
        # Check for unreasonably small amounts
        if amount < 0.00001:
            return False, None, f"Amount too small: {amount} {display_text} (min: 0.00001)", currency, display_text
        
        return True, amount, f"Amount validated: {amount} {display_text}", currency, display_text
    
    def amount_to_mist(self, amount_sui: float) -> int:
        """
        Convert SUI amount to MIST (smallest unit).
        
        Args:
            amount_sui: Amount in SUI
        
        Returns:
            Amount in MIST (1 SUI = 1,000,000,000 MIST)
        """
        return int(amount_sui * 1_000_000_000)
    
    def amount_to_wei(self, amount_xrpl: float) -> int:
        """
        Convert XRPL amount to Wei (smallest unit for XRPL EVM).
        
        Args:
            amount_xrpl: Amount in XRPL/XRP
        
        Returns:
            Amount in Wei (1 XRP = 10^18 Wei)
        """
        return int(amount_xrpl * 10**18)

