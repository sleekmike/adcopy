"""
Ad generation API endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import Field
from typing import List, Dict, Any
import uuid
from datetime import datetime, timezone
from bson import ObjectId

from app.models.ad import AdGenerationRequest, AdGenerationResponse, AdModel
from app.services.ai_service import DeepSeekService
from app.core.database import db

router = APIRouter()

# Initialize AI service
ai_service = DeepSeekService()

@router.post("/ads/generate", response_model=AdGenerationResponse)
async def generate_ads(
    request: AdGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate ad copy variations for specified platform
    
    This endpoint:
    1. Validates the request 
    2. Generates ads using AI service (with fallback)
    3. Saves to database in background
    4. Returns formatted response
    """
    
    try:
        # Generate request ID for tracking
        request_id = str(uuid.uuid4())
        
        # Generate ad variations using AI service
        variations = await ai_service.generate_ad_variations(request)
        
        if not variations:
            raise HTTPException(
                status_code=500, 
                detail="Failed to generate ad variations. Please try again."
            )
        
        # Schedule background save to database
        background_tasks.add_task(
            save_ad_to_database,
            request_id=request_id,
            input_data=request.model_dump(),
            variations=variations,
            platform=request.platform.value
        )
        
        # Return response
        response = AdGenerationResponse(
            success=True,
            variations=variations,
            generated_at=datetime.now(timezone.utc),
            request_id=request_id
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in generate_ads: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later."
        )

@router.get("/ads/history")
async def get_ad_history(
    limit: int = Query(default=50, ge=1, le=100, description="Number of ads to return"),
    platform: str = Query(default=None, description="Filter by platform")
):
    """
    Get recent ad generation history
    
    Query parameters:
    - limit: Number of ads to return (max 100)
    - platform: Filter by platform (optional)
    """
    
    try:
        # Return empty if no database
        if db.database is None:
            return {
                "success": True,
                "ads": [],
                "total": 0
            }
        
        # Limit the results
        limit = min(limit, 100)
        
        # Build query
        query = {}
        if platform:
            query["platform"] = platform
            
        # Fetch from database
        ads_collection = db.database.ads
        ads = list(ads_collection.find(query).sort("created_at", -1).limit(limit))
        
        # Format response
        formatted_ads = []
        for ad in ads:
            formatted_ads.append({
                "id": str(ad["_id"]),
                "platform": ad.get("platform"),
                "input_data": ad.get("input_data"),
                "variations": ad.get("generated_variations", []),
                "created_at": ad.get("created_at"),
                "is_favorite": ad.get("is_favorite", False),
                "tags": ad.get("tags", [])
            })
        
        return {
            "success": True,
            "ads": formatted_ads,
            "total": len(formatted_ads)
        }
        
    except Exception as e:
        print(f"Error fetching ad history: {str(e)}")
        return {
            "success": True,
            "ads": [],
            "total": 0
        }

@router.get("/ads/{ad_id}")
async def get_ad_by_id(ad_id: str):
    """Get specific ad by ID"""
    
    try:
        if db.database is None:
            raise HTTPException(status_code=404, detail="Ad not found")
            
        ads_collection = db.database.ads
        ad = ads_collection.find_one({"_id": ObjectId(ad_id)})
        
        if not ad:
            raise HTTPException(status_code=404, detail="Ad not found")
            
        return {
            "success": True,
            "ad": {
                "id": str(ad["_id"]),
                "platform": ad.get("platform"),
                "input_data": ad.get("input_data"),
                "variations": ad.get("generated_variations", []),
                "created_at": ad.get("created_at"),
                "is_favorite": ad.get("is_favorite", False),
                "tags": ad.get("tags", [])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching ad {ad_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch ad"
        )

@router.put("/ads/{ad_id}/favorite")
async def toggle_favorite(ad_id: str):
    """Toggle favorite status of an ad"""
    
    try:
        if db.database is None:
            raise HTTPException(status_code=404, detail="Ad not found")
            
        ads_collection = db.database.ads
        ad = ads_collection.find_one({"_id": ObjectId(ad_id)})
        
        if not ad:
            raise HTTPException(status_code=404, detail="Ad not found")
            
        # Toggle favorite status
        new_favorite_status = not ad.get("is_favorite", False)
        ads_collection.update_one(
            {"_id": ObjectId(ad_id)},
            {"$set": {"is_favorite": new_favorite_status}}
        )
        
        return {
            "success": True,
            "message": f"Ad {'added to' if new_favorite_status else 'removed from'} favorites",
            "is_favorite": new_favorite_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error toggling favorite for ad {ad_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update favorite status"
        )

@router.delete("/ads/{ad_id}")
async def delete_ad(ad_id: str):
    """Delete an ad"""
    
    try:
        if db.database is None:
            raise HTTPException(status_code=404, detail="Ad not found")
            
        ads_collection = db.database.ads
        result = ads_collection.delete_one({"_id": ObjectId(ad_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Ad not found")
        
        return {
            "success": True,
            "message": "Ad deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting ad {ad_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete ad"
        )

@router.get("/platforms")
async def get_platforms():
    """Get available platforms and their specifications"""
    
    from app.models.ad import PLATFORM_LIMITS
    
    return {
        "success": True,
        "platforms": PLATFORM_LIMITS
    }

@router.get("/health")
async def health_check():
    """Health check for the ads service"""
    
    try:
        # Test database connection
        if db.database is not None:
            db.database.ads.find_one()
            db_status = "connected"
        else:
            db_status = "disconnected"
        
        return {
            "success": True,
            "service": "ads",
            "status": "healthy",
            "database": db_status
        }
        
    except Exception as e:
        print(f"Health check failed: {str(e)}")
        return {
            "success": False,
            "service": "ads", 
            "status": "unhealthy",
            "error": str(e)
        }

# Background task functions
async def save_ad_to_database(
    request_id: str,
    input_data: Dict[str, Any], 
    variations: List[Dict[str, Any]],
    platform: str
):
    """Background task to save ad to database"""
    
    try:
        if db.database is None:
            print("No database connection - skipping save")
            return
            
        ad_doc = {
            "input_data": input_data,
            "generated_variations": variations,
            "platform": platform,
            "request_id": request_id,
            "created_at": datetime.now(timezone.utc),
            "is_favorite": False,
            "tags": []
        }
        
        ads_collection = db.database.ads
        result = ads_collection.insert_one(ad_doc)
        print(f"✅ Saved ad to database: {request_id} (ID: {result.inserted_id})")
        
    except Exception as e:
        print(f"❌ Failed to save ad to database: {str(e)}")
        # Don't raise exception in background task
