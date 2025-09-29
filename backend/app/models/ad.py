"""
Ad generation models and schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from enum import Enum

# Platform definitions matching your frontend
class PlatformType(str, Enum):
    GOOGLE_SEARCH = "google_search"
    GOOGLE_DISPLAY = "google_display"
    META = "meta"  # Facebook/Instagram
    TIKTOK = "tiktok"

class ToneType(str, Enum):
    URGENT = "Urgent"
    LUXURY = "Luxury" 
    CASUAL = "Casual"
    TRUSTWORTHY = "Trustworthy"

class BusinessType(str, Enum):
    DEALERSHIP = "dealership"
    ECOMMERCE = "ecommerce"
    RESTAURANT = "restaurant"
    SALON = "salon"
    GYM = "gym"
    REAL_ESTATE = "real_estate"
    GENERAL = "general"

# Platform-specific limits (matching your frontend)
PLATFORM_LIMITS = {
    "google_search": {
        "label": "Google Search (RSA)",
        "fields": {
            "headlines": {"max": 30, "count": 3},
            "descriptions": {"max": 90, "count": 2},
        },
        "soft": False,
    },
    "google_display": {
        "label": "Google Display",
        "fields": {
            "shortHeadline": {"max": 30, "count": 1},
            "longHeadline": {"max": 90, "count": 1},
            "descriptions": {"max": 90, "count": 2},
        },
        "soft": False,
    },
    "meta": {
        "label": "Meta (FB/IG)",
        "fields": {
            "primary": {"max": 125, "count": 1},
            "headline": {"max": 40, "count": 1},
            "description": {"max": 30, "count": 1},
        },
        "soft": True,
    },
    "tiktok": {
        "label": "TikTok", 
        "fields": {
            "caption": {"max": 100, "count": 1},
        },
        "soft": True,
    },
}

# Request/Response Models
class AdGenerationRequest(BaseModel):
    """Request model for ad generation"""
    name: str = Field(..., min_length=1, max_length=100, description="Product/service name")
    desc: str = Field(..., min_length=10, max_length=500, description="Product description")
    audience: List[str] = Field(default=[], description="Target audience tags")
    tone: ToneType = Field(default=ToneType.TRUSTWORTHY, description="Ad tone")
    platform: PlatformType = Field(default=PlatformType.META, description="Target platform")
    variants: int = Field(default=3, ge=1, le=5, description="Number of variations to generate")

class GoogleSearchVariation(BaseModel):
    """Google Search ad variation"""
    id: str
    platform: str = "google_search"
    tone: str
    headlines: List[str] = Field(..., min_items=3, max_items=3)
    descriptions: List[str] = Field(..., min_items=2, max_items=2)

class GoogleDisplayVariation(BaseModel):
    """Google Display ad variation"""
    id: str
    platform: str = "google_display"
    tone: str
    shortHeadline: str
    longHeadline: str
    descriptions: List[str] = Field(..., min_items=2, max_items=2)

class MetaVariation(BaseModel):
    """Meta (Facebook/Instagram) ad variation"""
    id: str
    platform: str = "meta"
    tone: str
    primary: str
    headline: str
    description: str

class TikTokVariation(BaseModel):
    """TikTok ad variation"""
    id: str
    platform: str = "tiktok"
    tone: str
    caption: str

class AdGenerationResponse(BaseModel):
    """Response model for ad generation"""
    success: bool
    variations: List[Dict[str, Any]]  # Flexible to handle different platform formats
    generated_at: datetime
    request_id: str

# Database Models (using plain dicts for PyMongo)
class AdModel(BaseModel):
    """Ad model for MongoDB storage"""
    input_data: Dict[str, Any]
    generated_variations: List[Dict[str, Any]]
    platform: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_favorite: bool = Field(default=False)
    tags: List[str] = Field(default_factory=list)
    request_id: str
