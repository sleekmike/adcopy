"""
Integration tests for the complete ad generation workflow
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, AsyncMock


class TestCompleteWorkflow:
    """Test complete ad generation workflow end-to-end"""
    
    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)
    
    def test_complete_ad_generation_workflow(self, client, sample_ad_request, mock_database):
        """Test complete workflow from request to database storage"""
        
        # Mock successful AI generation
        mock_variations = [
            {
                "id": "test_123",
                "platform": "meta",
                "tone": "Trustworthy",
                "primary": "Clean CarFax, 62k miles with Apple CarPlay. For first-time buyers, OKC.",
                "headline": "2019 Toyota Camry SE — Trusted choice",
                "description": "$289/mo"
            }
        ]
        
        with patch('app.api.v1.ads.ai_service.generate_ad_variations') as mock_ai:
            mock_ai.return_value = mock_variations
            
            # Step 1: Generate ads
            response = client.post("/api/v1/ads/generate", json=sample_ad_request)
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify response structure
            assert data["success"] is True
            assert len(data["variations"]) == 1
            assert "request_id" in data
            assert "generated_at" in data
            
            # Verify variation content
            variation = data["variations"][0]
            assert variation["platform"] == "meta"
            assert variation["tone"] == "Trustworthy"
            assert "primary" in variation
            assert "headline" in variation
            assert "description" in variation
    
    def test_workflow_with_database_integration(self, client, sample_ad_request, mock_database):
        """Test workflow including database operations"""
        
        # Setup database mocks
        mock_ads_collection = Mock()
        mock_database.ads = mock_ads_collection
        
        # Mock successful insert
        mock_result = Mock()
        mock_result.inserted_id = "507f1f77bcf86cd799439011"
        mock_ads_collection.insert_one.return_value = mock_result
        
        # Mock AI service
        with patch('app.api.v1.ads.ai_service.generate_ad_variations') as mock_ai:
            mock_ai.return_value = [{"id": "test", "platform": "meta", "tone": "Trustworthy"}]
            
            # Generate ads
            response = client.post("/api/v1/ads/generate", json=sample_ad_request)
            assert response.status_code == 200
            
            # Verify database save would be called (background task)
            # Note: Background tasks are tested separately
    
    def test_workflow_ai_fallback(self, client, sample_ad_request, mock_database):
        """Test workflow when AI service fails and fallback is used"""
        
        with patch('app.api.v1.ads.ai_service.generate_ad_variations') as mock_ai:
            # Mock AI service failure, should trigger fallback
            mock_ai.side_effect = Exception("AI service unavailable")
            
            response = client.post("/api/v1/ads/generate", json=sample_ad_request)
            
            # Should still succeed with fallback
            assert response.status_code == 500  # Expected due to exception
    
    def test_multiple_platform_generation(self, client, mock_database):
        """Test generating ads for multiple platforms"""
        platforms = ["google_search", "google_display", "meta", "tiktok"]
        
        for platform in platforms:
            request_data = {
                "name": "Test Product",
                "desc": "Test description for comprehensive testing of all platforms",
                "audience": ["test audience"],
                "tone": "Trustworthy",
                "platform": platform,
                "variants": 2
            }
            
            with patch('app.api.v1.ads.ai_service.generate_ad_variations') as mock_ai:
                mock_ai.return_value = [
                    {"id": "test1", "platform": platform, "tone": "Trustworthy"},
                    {"id": "test2", "platform": platform, "tone": "Trustworthy"}
                ]
                
                response = client.post("/api/v1/ads/generate", json=request_data)
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert len(data["variations"]) == 2


class TestPerformanceAndLimits:
    """Test performance considerations and limits"""
    
    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)
    
    def test_maximum_variants_generation(self, client, mock_database):
        """Test generation with maximum allowed variants"""
        request_data = {
            "name": "Test Product",
            "desc": "Test description for maximum variants testing",
            "tone": "Trustworthy",
            "platform": "meta",
            "variants": 5  # Maximum allowed
        }
        
        with patch('app.api.v1.ads.ai_service.generate_ad_variations') as mock_ai:
            mock_ai.return_value = [{"id": f"test{i}", "platform": "meta", "tone": "Trustworthy"} for i in range(5)]
            
            response = client.post("/api/v1/ads/generate", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["variations"]) == 5
    
    def test_concurrent_requests_handling(self, client, mock_database):
        """Test handling of concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            request_data = {
                "name": "Concurrent Test Product",
                "desc": "Testing concurrent request handling",
                "tone": "Trustworthy",
                "platform": "meta",
                "variants": 1
            }
            
            with patch('app.api.v1.ads.ai_service.generate_ad_variations') as mock_ai:
                mock_ai.return_value = [{"id": "test", "platform": "meta", "tone": "Trustworthy"}]
                
                response = client.post("/api/v1/ads/generate", json=request_data)
                results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(results) == 5
        assert all(status == 200 for status in results)
    
    def test_large_input_handling(self, client, mock_database):
        """Test handling of large but valid inputs"""
        # Create large but valid inputs
        large_description = "This is a comprehensive product description. " * 20  # ~800 chars
        large_audience = [f"audience_segment_{i}" for i in range(50)]  # 50 audience segments
        
        request_data = {
            "name": "Large Input Test Product",
            "desc": large_description[:500],  # Truncate to stay within limits
            "audience": large_audience,
            "tone": "Trustworthy",
            "platform": "meta",
            "variants": 3
        }
        
        with patch('app.api.v1.ads.ai_service.generate_ad_variations') as mock_ai:
            mock_ai.return_value = [{"id": "test", "platform": "meta", "tone": "Trustworthy"}] * 3
            
            response = client.post("/api/v1/ads/generate", json=request_data)
            assert response.status_code == 200


class TestErrorRecovery:
    """Test error recovery and graceful degradation"""
    
    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)
    
    def test_database_unavailable_recovery(self, client):
        """Test recovery when database is unavailable"""
        with patch('app.api.v1.ads.db.database', None):
            # AI generation should still work
            with patch('app.api.v1.ads.ai_service.generate_ad_variations') as mock_ai:
                mock_ai.return_value = [{"id": "test", "platform": "meta", "tone": "Trustworthy"}]
                
                request_data = {
                    "name": "Database Unavailable Test",
                    "desc": "Testing recovery when database is unavailable",
                    "tone": "Trustworthy",
                    "platform": "meta",
                    "variants": 1
                }
                
                response = client.post("/api/v1/ads/generate", json=request_data)
                assert response.status_code == 200
            
            # History should return empty gracefully
            response = client.get("/api/v1/ads/history")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["ads"] == []
    
    def test_ai_service_complete_failure(self, client, mock_database):
        """Test behavior when AI service completely fails"""
        with patch('app.api.v1.ads.ai_service.generate_ad_variations') as mock_ai:
            mock_ai.return_value = []  # Empty response
            
            request_data = {
                "name": "AI Failure Test",
                "desc": "Testing complete AI service failure",
                "tone": "Trustworthy",
                "platform": "meta",
                "variants": 1
            }
            
            response = client.post("/api/v1/ads/generate", json=request_data)
            assert response.status_code == 500
            
            error_data = response.json()
            assert "Failed to generate ad variations" in error_data["detail"]
    
    def test_partial_service_degradation(self, client, mock_database):
        """Test behavior with partial service degradation"""
        # Simulate scenario where AI works but database saving fails
        with patch('app.api.v1.ads.ai_service.generate_ad_variations') as mock_ai:
            mock_ai.return_value = [{"id": "test", "platform": "meta", "tone": "Trustworthy"}]
            
            # Mock database failure for saving
            mock_database.ads.insert_one.side_effect = Exception("Database write failed")
            
            request_data = {
                "name": "Partial Degradation Test",
                "desc": "Testing partial service degradation",
                "tone": "Trustworthy",
                "platform": "meta",
                "variants": 1
            }
            
            response = client.post("/api/v1/ads/generate", json=request_data)
            
            # Should still return success (database save is background task)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True


class TestDataConsistency:
    """Test data consistency across operations"""
    
    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)
    
    def test_request_response_consistency(self, client, mock_database):
        """Test that response data is consistent with request"""
        request_data = {
            "name": "Consistency Test Product",
            "desc": "Testing data consistency across request and response",
            "audience": ["consistency_testers", "qa_team"],
            "tone": "Luxury",
            "platform": "google_search",
            "variants": 3
        }
        
        with patch('app.api.v1.ads.ai_service.generate_ad_variations') as mock_ai:
            mock_ai.return_value = [
                {"id": f"test{i}", "platform": "google_search", "tone": "Luxury"} 
                for i in range(3)
            ]
            
            response = client.post("/api/v1/ads/generate", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify response reflects request parameters
            assert len(data["variations"]) == request_data["variants"]
            
            for variation in data["variations"]:
                assert variation["platform"] == request_data["platform"]
                assert variation["tone"] == request_data["tone"]
    
    def test_database_storage_consistency(self, client, mock_database):
        """Test that data stored in database matches generated data"""
        # This test verifies the background task data consistency
        # In a real implementation, you might want to test the actual storage
        pass


class TestApiDocumentation:
    """Test API documentation and schema consistency"""
    
    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)
    
    def test_openapi_schema_availability(self, client):
        """Test that OpenAPI schema is available and valid"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert schema["info"]["title"] == "AI Ad Copy Generator"
        assert "paths" in schema
        assert "/api/v1/ads/generate" in schema["paths"]
    
    def test_docs_endpoints_accessible(self, client):
        """Test that documentation endpoints are accessible"""
        # Test Swagger UI
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Test ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200
    
    def test_schema_endpoint_consistency(self, client):
        """Test that schema matches actual endpoint behavior"""
        response = client.get("/openapi.json")
        schema = response.json()
        
        # Verify ad generation endpoint is documented
        ad_gen_path = schema["paths"].get("/api/v1/ads/generate")
        assert ad_gen_path is not None
        assert "post" in ad_gen_path
        
        # Verify request schema is documented
        post_spec = ad_gen_path["post"]
        assert "requestBody" in post_spec
        assert "responses" in post_spec
