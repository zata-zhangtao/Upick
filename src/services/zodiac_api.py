# zodiac_api.py

from fastapi import FastAPI, HTTPException, Query, APIRouter
from typing import Dict, Any
from src.services.ZodiacService import ZodiacService
from src.utils.logger import get_logger
from pydantic import BaseModel

# Initialize logger
logger = get_logger(__name__)

# Initialize router
zodiac_router = APIRouter(prefix="/api/zodiac", tags=["Zodiac"])

# Initialize zodiac service
zodiac_service = ZodiacService()

class ZodiacRequest(BaseModel):
    zodiac_sign: str
    horoscope_type: str = 'daily'

class CompatibilityRequest(BaseModel):
    sign1: str
    sign2: str

@zodiac_router.get("/horoscope/{zodiac_sign}", response_model=Dict[str, Any])
async def get_horoscope(
    zodiac_sign: str,
    horoscope_type: str = Query('daily', description="Type of horoscope (daily, weekly, monthly, yearly)")
):
    """
    Get horoscope for a specific zodiac sign.
    
    - **zodiac_sign**: The zodiac sign (e.g., 'aries', 'taurus')
    - **horoscope_type**: Type of horoscope (daily, weekly, monthly, yearly)
    """
    try:
        logger.info(f"Fetching {horoscope_type} horoscope for {zodiac_sign}")
        
        result = await zodiac_service.get_horoscope(zodiac_sign, horoscope_type)
        
        if not result:
            raise HTTPException(status_code=404, detail=f"No horoscope found for {zodiac_sign}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error while fetching horoscope: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@zodiac_router.post("/compatibility", response_model=Dict[str, Any])
async def get_compatibility(request: CompatibilityRequest):
    """
    Get compatibility between two zodiac signs.
    
    - **sign1**: First zodiac sign
    - **sign2**: Second zodiac sign
    """
    try:
        logger.info(f"Fetching compatibility between {request.sign1} and {request.sign2}")
        
        result = await zodiac_service.get_compatibility(request.sign1, request.sign2)
        
        if not result:
            raise HTTPException(status_code=404, detail="Compatibility information not found")
        
        return result
    
    except Exception as e:
        logger.error(f"Error while fetching compatibility: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Function to include router in main app
def include_zodiac_router(app: FastAPI):
    app.include_router(zodiac_router)