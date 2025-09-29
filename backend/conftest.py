"""
Test configuration and fixtures for the AI Ad Copy Generator backend
"""
import pytest
import asyncio
from typing import AsyncGenerator, Dict, Any
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
import httpx

from main import app
from app.core.database import db
from app.services.ai_service import DeepSeekService
from app.models.ad import PlatformType, ToneType


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def mock_database():
    """Mock database for testing without actual MongoDB"""
    original_db = db.database
    mock_db = Mock()
    
    # Mock collections
    mock_ads_collection = Mock()
    mock_db.ads = mock_ads_collection
    
    # Set mock database
    db.database = mock_db
    
    yield mock_db
    
    # Restore original database
    db.database = original_db


@pytest.fixture
def sample_ad_request():
    """Sample ad generation request for testing"""
    return {
        "name": "2019 Toyota Camry SE",
        "desc": "Clean CarFax, 62k miles, Apple CarPlay, 35 MPG, $289/mo with approved credit",
        "audience": ["first-time buyers", "OKC"],
        "tone": "Trustworthy",
        "platform": "meta",
        "variants": 3
    }


@pytest.fixture
def sample_ad_response():
    """Sample ad generation response"""
    return [
        {
            "id": "test123",
            "platform": "meta",
            "tone": "Trustworthy",
            "primary": "Clean CarFax, 62k miles with Apple CarPlay. For first-time buyers, OKC. Top-rated by customers.",
            "headline": "2019 Toyota Camry SE — Trusted choice",
            "description": "$289/mo"
        }
    ]


@pytest.fixture
def mock_ai_service():
    """Mock AI service for testing"""
    mock_service = Mock(spec=DeepSeekService)
    mock_service.generate_ad_variations = AsyncMock()
    return mock_service


@pytest.fixture
def mock_deepseek_api():
    """Mock DeepSeek API responses"""
    return {
        "choices": [
            {
                "message": {
                    "content": '''```json
{
  "variations": [
    {
      "primary": "Clean CarFax, 62k miles with Apple CarPlay. Perfect for first-time buyers in OKC.",
      "headline": "2019 Toyota Camry SE — Trusted choice", 
      "description": "$289/mo"
    }
  ]
}
```'''
                }
            }
        ]
    }


@pytest.fixture
def sample_database_ad():
    """Sample ad document as stored in database"""
    return {
        "_id": "507f1f77bcf86cd799439011",
        "input_data": {
            "name": "2019 Toyota Camry SE",
            "desc": "Clean CarFax, 62k miles, Apple CarPlay",
            "audience": ["first-time buyers"],
            "tone": "Trustworthy",
            "platform": "meta",
            "variants": 3
        },
        "generated_variations": [
            {
                "id": "test123",
                "platform": "meta",
                "tone": "Trustworthy",
                "primary": "Clean CarFax, 62k miles with Apple CarPlay",
                "headline": "2019 Toyota Camry SE — Trusted choice",
                "description": "$289/mo"
            }
        ],
        "platform": "meta",
        "created_at": "2024-01-15T10:30:00Z",
        "is_favorite": False,
        "tags": [],
        "request_id": "req_123"
    }


@pytest.fixture
def invalid_ad_requests():
    """Various invalid ad requests for testing validation"""
    return [
        # Missing required fields
        {"desc": "Test description"},
        {"name": "Test product"},
        
        # Invalid field values
        {"name": "", "desc": "Test description"},
        {"name": "Test", "desc": ""},
        {"name": "Test", "desc": "Test", "variants": 0},
        {"name": "Test", "desc": "Test", "variants": 10},
        {"name": "Test", "desc": "Test", "tone": "InvalidTone"},
        {"name": "Test", "desc": "Test", "platform": "InvalidPlatform"},
        
        # Field length violations
        {"name": "x" * 200, "desc": "Test description"},
        {"name": "Test", "desc": "x" * 1000},
    ]
