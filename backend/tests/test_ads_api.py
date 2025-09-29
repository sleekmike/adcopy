"""
Comprehensive tests for ad generation API endpoints
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from bson import ObjectId
import json

from app.models.ad import PlatformType, ToneType


class TestAdGenerationEndpoint:
    """Tests for POST /api/v1/ads/generate"""
    
    def test_generate_ads_success(self, client: TestClient, sample_ad_request, mock_database):
        """Test successful ad generation"""
        with patch('app.api.v1.ads.ai_service.generate_ad_variations') as mock_generate:
            mock_generate.return_value = [
                {
                    "id": "test123",
                    "platform": "meta",
                    "tone": "Trustworthy",
                    "primary": "Test primary text",
                    "headline": "Test headline",
                    "description": "Test desc"
                }
            ]
            
            response = client.post("/api/v1/ads/generate", json=sample_ad_request)
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert len(data["variations"]) == 1
            assert data["variations"][0]["platform"] == "meta"
            assert data["variations"][0]["tone"] == "Trustworthy"
            assert "request_id" in data
            assert "generated_at" in data
    
    def test_generate_ads_validation_errors(self, client: TestClient, invalid_ad_requests):
        """Test validation errors for invalid requests"""
        for invalid_request in invalid_ad_requests:
            response = client.post("/api/v1/ads/generate", json=invalid_request)
            assert response.status_code == 422  # Validation error
    
    def test_generate_ads_missing_body(self, client: TestClient):
        """Test request without body"""
        response = client.post("/api/v1/ads/generate")
        assert response.status_code == 422
    
    def test_generate_ads_ai_service_failure(self, client: TestClient, sample_ad_request, mock_database):
        """Test handling of AI service failure"""
        with patch('app.api.v1.ads.ai_service.generate_ad_variations') as mock_generate:
            mock_generate.return_value = []  # Empty response
            
            response = client.post("/api/v1/ads/generate", json=sample_ad_request)
            
            assert response.status_code == 500
            assert "Failed to generate ad variations" in response.json()["detail"]
    
    def test_generate_ads_ai_service_exception(self, client: TestClient, sample_ad_request, mock_database):
        """Test handling of AI service exception"""
        with patch('app.api.v1.ads.ai_service.generate_ad_variations') as mock_generate:
            mock_generate.side_effect = Exception("AI service error")
            
            response = client.post("/api/v1/ads/generate", json=sample_ad_request)
            
            assert response.status_code == 500
            assert "Internal server error" in response.json()["detail"]
    
    def test_generate_ads_all_platforms(self, client: TestClient, mock_database):
        """Test ad generation for all supported platforms"""
        platforms = ["google_search", "google_display", "meta", "tiktok"]
        
        for platform in platforms:
            request_data = {
                "name": "Test Product",
                "desc": "Test description for testing purposes",
                "audience": ["test audience"],
                "tone": "Trustworthy",
                "platform": platform,
                "variants": 3
            }
            
            with patch('app.api.v1.ads.ai_service.generate_ad_variations') as mock_generate:
                mock_generate.return_value = [{"id": "test", "platform": platform, "tone": "Trustworthy"}]
                
                response = client.post("/api/v1/ads/generate", json=request_data)
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
    
    def test_generate_ads_all_tones(self, client: TestClient, mock_database):
        """Test ad generation for all supported tones"""
        tones = ["Urgent", "Luxury", "Casual", "Trustworthy"]
        
        for tone in tones:
            request_data = {
                "name": "Test Product",
                "desc": "Test description for testing purposes",
                "audience": ["test audience"],
                "tone": tone,
                "platform": "meta",
                "variants": 3
            }
            
            with patch('app.api.v1.ads.ai_service.generate_ad_variations') as mock_generate:
                mock_generate.return_value = [{"id": "test", "platform": "meta", "tone": tone}]
                
                response = client.post("/api/v1/ads/generate", json=request_data)
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True


class TestAdHistoryEndpoint:
    """Tests for GET /api/v1/ads/history"""
    
    def test_get_history_success(self, client: TestClient, mock_database, sample_database_ad):
        """Test successful history retrieval"""
        mock_database.ads.find.return_value.sort.return_value.limit.return_value = [sample_database_ad]
        
        response = client.get("/api/v1/ads/history")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert len(data["ads"]) == 1
        assert data["total"] == 1
        assert data["ads"][0]["id"] == "507f1f77bcf86cd799439011"
    
    def test_get_history_with_limit(self, client: TestClient, mock_database):
        """Test history with custom limit"""
        mock_database.ads.find.return_value.sort.return_value.limit.return_value = []
        
        response = client.get("/api/v1/ads/history?limit=10")
        
        assert response.status_code == 200
        # Verify limit was applied
        mock_database.ads.find.return_value.sort.return_value.limit.assert_called_with(10)
    
    def test_get_history_with_platform_filter(self, client: TestClient, mock_database):
        """Test history with platform filter"""
        mock_database.ads.find.return_value.sort.return_value.limit.return_value = []
        
        response = client.get("/api/v1/ads/history?platform=meta")
        
        assert response.status_code == 200
        # Verify platform filter was applied
        mock_database.ads.find.assert_called_with({"platform": "meta"})
    
    def test_get_history_max_limit_enforced(self, client: TestClient, mock_database):
        """Test that limit is capped at 100"""
        mock_database.ads.find.return_value.sort.return_value.limit.return_value = []
        
        response = client.get("/api/v1/ads/history?limit=500")
        
        assert response.status_code == 200
        # Verify limit was capped at 100
        mock_database.ads.find.return_value.sort.return_value.limit.assert_called_with(100)
    
    def test_get_history_no_database(self, client: TestClient):
        """Test history when database is not available"""
        with patch('app.api.v1.ads.db.database', None):
            response = client.get("/api/v1/ads/history")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert data["ads"] == []
            assert data["total"] == 0
    
    def test_get_history_database_error(self, client: TestClient, mock_database):
        """Test history when database throws an error"""
        mock_database.ads.find.side_effect = Exception("Database error")
        
        response = client.get("/api/v1/ads/history")
        
        assert response.status_code == 200  # Should return empty result, not error
        data = response.json()
        assert data["success"] is True
        assert data["ads"] == []


class TestAdByIdEndpoint:
    """Tests for GET /api/v1/ads/{ad_id}"""
    
    def test_get_ad_by_id_success(self, client: TestClient, mock_database, sample_database_ad):
        """Test successful ad retrieval by ID"""
        ad_id = "507f1f77bcf86cd799439011"
        mock_database.ads.find_one.return_value = sample_database_ad
        
        response = client.get(f"/api/v1/ads/{ad_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["ad"]["id"] == ad_id
        assert data["ad"]["platform"] == "meta"
        
        # Verify correct ObjectId was used
        mock_database.ads.find_one.assert_called_with({"_id": ObjectId(ad_id)})
    
    def test_get_ad_by_id_not_found(self, client: TestClient, mock_database):
        """Test ad not found"""
        ad_id = "507f1f77bcf86cd799439011"
        mock_database.ads.find_one.return_value = None
        
        response = client.get(f"/api/v1/ads/{ad_id}")
        
        assert response.status_code == 404
        assert "Ad not found" in response.json()["detail"]
    
    def test_get_ad_by_id_invalid_id(self, client: TestClient, mock_database):
        """Test invalid ObjectId"""
        response = client.get("/api/v1/ads/invalid_id")
        
        assert response.status_code == 500
    
    def test_get_ad_by_id_no_database(self, client: TestClient):
        """Test when database is not available"""
        with patch('app.api.v1.ads.db.database', None):
            response = client.get("/api/v1/ads/507f1f77bcf86cd799439011")
            
            assert response.status_code == 404


class TestToggleFavoriteEndpoint:
    """Tests for PUT /api/v1/ads/{ad_id}/favorite"""
    
    def test_toggle_favorite_success(self, client: TestClient, mock_database, sample_database_ad):
        """Test successful favorite toggle"""
        ad_id = "507f1f77bcf86cd799439011"
        mock_database.ads.find_one.return_value = sample_database_ad
        mock_database.ads.update_one.return_value = Mock()
        
        response = client.put(f"/api/v1/ads/{ad_id}/favorite")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "favorites" in data["message"]
        assert isinstance(data["is_favorite"], bool)
        
        # Verify update was called
        mock_database.ads.update_one.assert_called_once()
    
    def test_toggle_favorite_not_found(self, client: TestClient, mock_database):
        """Test toggle favorite for non-existent ad"""
        ad_id = "507f1f77bcf86cd799439011"
        mock_database.ads.find_one.return_value = None
        
        response = client.put(f"/api/v1/ads/{ad_id}/favorite")
        
        assert response.status_code == 404


class TestDeleteAdEndpoint:
    """Tests for DELETE /api/v1/ads/{ad_id}"""
    
    def test_delete_ad_success(self, client: TestClient, mock_database):
        """Test successful ad deletion"""
        ad_id = "507f1f77bcf86cd799439011"
        mock_result = Mock()
        mock_result.deleted_count = 1
        mock_database.ads.delete_one.return_value = mock_result
        
        response = client.delete(f"/api/v1/ads/{ad_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "deleted successfully" in data["message"]
        
        # Verify delete was called with correct ObjectId
        mock_database.ads.delete_one.assert_called_with({"_id": ObjectId(ad_id)})
    
    def test_delete_ad_not_found(self, client: TestClient, mock_database):
        """Test delete non-existent ad"""
        ad_id = "507f1f77bcf86cd799439011"
        mock_result = Mock()
        mock_result.deleted_count = 0
        mock_database.ads.delete_one.return_value = mock_result
        
        response = client.delete(f"/api/v1/ads/{ad_id}")
        
        assert response.status_code == 404


class TestPlatformsEndpoint:
    """Tests for GET /api/v1/platforms"""
    
    def test_get_platforms(self, client: TestClient):
        """Test platforms endpoint returns platform specifications"""
        response = client.get("/api/v1/platforms")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "platforms" in data
        
        platforms = data["platforms"]
        assert "google_search" in platforms
        assert "google_display" in platforms
        assert "meta" in platforms
        assert "tiktok" in platforms
        
        # Verify structure of platform data
        for platform_key, platform_data in platforms.items():
            assert "label" in platform_data
            assert "fields" in platform_data
            assert "soft" in platform_data


class TestAdHealthEndpoint:
    """Tests for GET /api/v1/health"""
    
    def test_health_check_with_database(self, client: TestClient, mock_database):
        """Test health check when database is connected"""
        mock_database.ads.find_one.return_value = None  # Successful query
        
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
    
    def test_health_check_without_database(self, client: TestClient):
        """Test health check when database is not available"""
        with patch('app.api.v1.ads.db.database', None):
            response = client.get("/api/v1/health")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert data["status"] == "healthy"
            assert data["database"] == "disconnected"
    
    def test_health_check_database_error(self, client: TestClient, mock_database):
        """Test health check when database throws an error"""
        mock_database.ads.find_one.side_effect = Exception("Database error")
        
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is False
        assert data["status"] == "unhealthy"
        assert "error" in data
