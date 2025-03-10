# api.py

from fastapi import FastAPI, HTTPException, Query
from typing import List
from src.services.recommendation_service import RecommendationService
from src.services.zodiac_api import include_zodiac_router
from src.utils.logger import get_logger

# 初始化日志记录器
logger = get_logger(__name__)

# 初始化 FastAPI 应用
app = FastAPI(
    title="Recommendation System API",
    description="A custom recommendation system that provides personalized recommendations.",
    version="1.0.0"
)

# 初始化推荐服务
recommendation_service = RecommendationService()

# 包含星座运势API路由
include_zodiac_router(app)

@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    Health check endpoint to verify if the service is running.
    """
    return {"status": "OK"}

@app.get("/api/recommendations", tags=["Recommendations"])
async def get_recommendations(
    user_id: int = Query(..., description="The ID of the user"),
    limit: int = Query(10, description="Maximum number of recommendations to return")
):
    """
    Get personalized recommendations for a user.

    - **user_id**: The ID of the user for whom recommendations are generated.
    - **limit**: The maximum number of recommendations to return (default: 10).
    """
    try:
        logger.info(f"Fetching recommendations for user_id={user_id}, limit={limit}")
        
        # 调用推荐服务生成推荐结果
        recommendations = recommendation_service.get_recommendations(user_id, limit)
        
        if not recommendations:
            raise HTTPException(status_code=404, detail="No recommendations found for the given user.")
        
        return {"user_id": user_id, "recommendations": recommendations}
    
    except Exception as e:
        logger.error(f"Error while fetching recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/feedback", tags=["Feedback"])
async def log_feedback(
    user_id: int,
    item_id: int,
    action: str = Query(..., description="User action (e.g., 'click', 'like', 'dislike')")
):
    """
    Log user feedback for a specific item.

    - **user_id**: The ID of the user providing feedback.
    - **item_id**: The ID of the item being interacted with.
    - **action**: The type of user action (e.g., 'click', 'like', 'dislike').
    """
    try:
        logger.info(f"Logging feedback: user_id={user_id}, item_id={item_id}, action={action}")
        
        # 调用推荐服务记录反馈
        success = recommendation_service.log_user_feedback(user_id, item_id, action)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to log feedback.")
        
        return {"message": "Feedback logged successfully"}
    
    except Exception as e:
        logger.error(f"Error while logging feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")