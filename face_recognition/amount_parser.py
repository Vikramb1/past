"""
Amount parser module using Ollama (llama3.2) to extract SUI amounts from text.
Parses natural language commands like "send 0.5 SUI" or "send five SUI".
"""
import re
from typing import Optional
import ollama
import config


class AmountParser:
    """Parses SUI amounts from transcribed speech using Ollama LLM."""
    
    def __init__(self):
        """Initialize the amount parser."""
        self.model = config.OLLAMA_MODEL
        self.default_amount = config.DEFAULT_PAYMENT_AMOUNT_SUI
        
        # Word to number mapping for spoken numbers
        self.word_to_num = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
            'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
            'ten': 10, 'twenty': 20, 'thirty': 30, 'forty': 40,
            'fifty': 50, 'hundred': 100, 'thousand': 1000
        }
        
        print(f"\n🧠 Amount Parser initialized")
        print(f"Model: {self.model}")
        print(f"Default amount: {self.default_amount} SUI")
    
    def parse_amount(self, text: str) -> Optional[float]:
        """
        Parse SUI amount from text using multiple strategies.
        
        Args:
            text: Transcribed text to parse
        
        Returns:
            Parsed amount in SUI, or None if not found
        """
        if not text or not text.strip():
            return None
        
        print(f"\n💭 Parsing: '{text}'")
        
        # Strategy 1: Try regex patterns first (faster)
        amount = self._parse_with_regex(text)
        if amount is not None:
            print(f"✅ Regex parsed: {amount} SUI")
            return amount
        
        # Strategy 2: Use Ollama LLM for complex parsing
        amount = self._parse_with_ollama(text)
        if amount is not None:
            print(f"✅ LLM parsed: {amount} SUI")
            return amount
        
        print(f"ℹ️  No amount detected, using default: {self.default_amount} SUI")
        return None
    
    def _parse_with_regex(self, text: str) -> Optional[float]:
        """
        Parse amount using regex patterns.
        
        Args:
            text: Text to parse
        
        Returns:
            Parsed amount or None
        """
        text_lower = text.lower()
        
        # Pattern 1: "send 0.5 SUI" or "0.5 SUI"
        pattern1 = r'(?:send\s+)?(\d+\.?\d*)\s*sui'
        match = re.search(pattern1, text_lower)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        
        # Pattern 2: "send .5 SUI" (leading decimal)
        pattern2 = r'(?:send\s+)?(\.\d+)\s*sui'
        match = re.search(pattern2, text_lower)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        
        # Pattern 3: Just a number followed by SUI
        pattern3 = r'(\d+\.?\d*)\s*sui'
        match = re.search(pattern3, text_lower)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        
        return None
    
    def _parse_with_ollama(self, text: str) -> Optional[float]:
        """
        Parse amount using Ollama LLM.
        
        Args:
            text: Text to parse
        
        Returns:
            Parsed amount or None
        """
        try:
            prompt = f"""Extract the SUI cryptocurrency amount from this text. Return ONLY the numeric value as a decimal number, nothing else.

Examples:
- "send 0.5 SUI" -> 0.5
- "send five SUI" -> 5
- "transfer 0.0001 SUI" -> 0.0001
- "send one point five SUI" -> 1.5

Text: "{text}"

Amount:"""
            
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': 0.1,  # Low temperature for deterministic output
                    'num_predict': 20,   # Short response expected
                }
            )
            
            # Extract the response
            result = response['response'].strip()
            
            # Try to parse as float
            # Remove any extra text and keep only number
            numbers = re.findall(r'\d+\.?\d*', result)
            if numbers:
                return float(numbers[0])
            
            return None
            
        except Exception as e:
            print(f"⚠️  Ollama parsing error: {e}")
            return None
    
    def validate_amount(self, amount: Optional[float]) -> tuple[bool, Optional[float], str]:
        """
        Validate parsed amount is reasonable.
        
        Args:
            amount: Parsed amount to validate
        
        Returns:
            Tuple of (is_valid, validated_amount, message)
        """
        if amount is None:
            return True, self.default_amount, f"Using default: {self.default_amount} SUI"
        
        # Check for negative
        if amount < 0:
            return False, None, "Amount cannot be negative"
        
        # Check for zero
        if amount == 0:
            return False, None, "Amount cannot be zero"
        
        # Check for unreasonably large amounts (safety check)
        if amount > 1000:
            return False, None, f"Amount too large: {amount} SUI (max: 1000)"
        
        # Check for unreasonably small amounts
        if amount < 0.00001:
            return False, None, f"Amount too small: {amount} SUI (min: 0.00001)"
        
        return True, amount, f"Amount validated: {amount} SUI"
    
    def amount_to_mist(self, amount_sui: float) -> int:
        """
        Convert SUI amount to MIST (smallest unit).
        
        Args:
            amount_sui: Amount in SUI
        
        Returns:
            Amount in MIST (1 SUI = 1,000,000,000 MIST)
        """
        return int(amount_sui * 1_000_000_000)

