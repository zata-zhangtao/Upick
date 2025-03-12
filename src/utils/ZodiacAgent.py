from metagpt.roles import Role
from typing import List, Dict, Any
from datetime import datetime

class ZodiacAction:
    """Base class for zodiac horoscope actions"""
    async def run(self, content: str) -> str:
        """Run the action on the given content"""
        raise NotImplementedError

class FetchHoroscope(ZodiacAction):
    """Action to fetch horoscope data from a source"""
    async def run(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch horoscope data based on zodiac sign and type"""
        # In a real implementation, this would call an API or scrape a website
        # For now, we'll return mock data
        zodiac_sign = content.get('zodiac_sign', 'aries')
        horoscope_type = content.get('horoscope_type', 'daily')
        
        # Mock horoscope data
        horoscopes = {
            'aries': {
                'daily': f"Today is a great day for Aries! Your energy is high and you'll accomplish much. {datetime.now().strftime('%Y-%m-%d')}",
                'weekly': "This week brings opportunities for growth. Focus on personal development.",
                'monthly': "This month will bring financial stability and career advancement.",
                'yearly': "This year is about transformation and embracing new beginnings.",
            },
            'taurus': {
                'daily': f"Taurus, today is about stability and patience. Take things slow. {datetime.now().strftime('%Y-%m-%d')}",
                'weekly': "This week, focus on self-care and maintaining your boundaries.",
                'monthly': "This month brings opportunities for romance and creative expression.",
                'yearly': "This year will test your resilience but bring rewards for your patience.",
            },
            # Add more signs as needed
        }
        
        # Get the horoscope for the requested sign and type
        sign_data = horoscopes.get(zodiac_sign.lower(), horoscopes['aries'])
        horoscope = sign_data.get(horoscope_type.lower(), sign_data['daily'])
        
        return {
            'zodiac_sign': zodiac_sign,
            'horoscope_type': horoscope_type,
            'horoscope': horoscope,
            'date': datetime.now().strftime('%Y-%m-%d')
        }

class GenerateCompatibility(ZodiacAction):
    """Action to generate compatibility between zodiac signs"""
    async def run(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate compatibility report for two zodiac signs"""
        sign1 = content.get('sign1', 'aries').lower()
        sign2 = content.get('sign2', 'taurus').lower()
        
        # Mock compatibility data
        compatibility_matrix = {
            ('aries', 'aries'): "Two Aries can create a passionate but competitive relationship. 70% compatibility.",
            ('aries', 'taurus'): "Aries and Taurus can complement each other well, with Aries bringing excitement and Taurus bringing stability. 65% compatibility.",
            ('taurus', 'aries'): "Taurus and Aries have different approaches to life, but can learn from each other. 65% compatibility.",
            ('taurus', 'taurus'): "Two Taurus create a stable, comfortable relationship with strong values. 85% compatibility.",
            # Add more combinations as needed
        }
        
        # Get compatibility or provide a default message
        compatibility = compatibility_matrix.get((sign1, sign2), 
                                              f"The compatibility between {sign1.capitalize()} and {sign2.capitalize()} is moderate. They have differences to overcome but also complementary traits.")
        
        return {
            'sign1': sign1,
            'sign2': sign2,
            'compatibility': compatibility,
            'date': datetime.now().strftime('%Y-%m-%d')
        }

class ZodiacHoroscopeAgent(Role):
    """A zodiac horoscope agent based on MetaGPT framework.
    This agent provides horoscope readings and zodiac sign compatibility analysis.
    """
    name: str = "Zara"
    profile: str = "ZodiacHoroscopeAgent"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([FetchHoroscope(), GenerateCompatibility()])
    
    async def _act(self) -> Dict[str, Any]:
        """Main action loop for the zodiac horoscope agent."""
        # Get the latest message from the environment
        todo = self.rc.todo
        msg = self.get_memories(k=1)[0]
        content = await todo.run(msg.content)
        return content
    
    async def get_horoscope(self, zodiac_sign: str, horoscope_type: str = 'daily') -> Dict[str, Any]:
        """Get horoscope for a specific zodiac sign and type"""
        fetch_action = FetchHoroscope()
        result = await fetch_action.run({
            'zodiac_sign': zodiac_sign,
            'horoscope_type': horoscope_type
        })
        return result
    
    async def get_compatibility(self, sign1: str, sign2: str) -> Dict[str, Any]:
        """Get compatibility between two zodiac signs"""
        compatibility_action = GenerateCompatibility()
        result = await compatibility_action.run({
            'sign1': sign1,
            'sign2': sign2
        })
        return result