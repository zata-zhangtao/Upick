from src.utils.ZodiacAgent import ZodiacHoroscopeAgent
import asyncio
from typing import Dict, Any

class ZodiacService:
    """Service class for interacting with the Zodiac Horoscope Agent"""
    
    def __init__(self):
        """Initialize the Zodiac Horoscope Service"""
        self.agent = ZodiacHoroscopeAgent()
    
    async def get_horoscope(self, zodiac_sign: str, horoscope_type: str = 'daily') -> Dict[str, Any]:
        """Get horoscope for a specific zodiac sign and type
        
        Args:
            zodiac_sign: The zodiac sign (e.g., 'aries', 'taurus')
            horoscope_type: Type of horoscope ('daily', 'weekly', 'monthly', 'yearly')
            
        Returns:
            Dictionary containing horoscope information
        """
        result = await self.agent.get_horoscope(zodiac_sign, horoscope_type)
        return result
    
    async def get_compatibility(self, sign1: str, sign2: str) -> Dict[str, Any]:
        """Get compatibility between two zodiac signs
        
        Args:
            sign1: First zodiac sign
            sign2: Second zodiac sign
            
        Returns:
            Dictionary containing compatibility information
        """
        result = await self.agent.get_compatibility(sign1, sign2)
        return result
    
    def get_horoscope_sync(self, zodiac_sign: str, horoscope_type: str = 'daily') -> Dict[str, Any]:
        """Synchronous wrapper for get_horoscope"""
        return asyncio.run(self.get_horoscope(zodiac_sign, horoscope_type))
    
    def get_compatibility_sync(self, sign1: str, sign2: str) -> Dict[str, Any]:
        """Synchronous wrapper for get_compatibility"""
        return asyncio.run(self.get_compatibility(sign1, sign2))