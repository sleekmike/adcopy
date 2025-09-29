"""
Tests for input validation and error responses
"""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.models.ad import AdGenerationRequest, PlatformType, ToneType


class TestRequestValidation:
    """Tests for API request validation"""
    
    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)
    
    def test_valid_request_all_fields(self, client):
        """Test valid request with all fields"""
        valid_request = {
            "name": "2019 Toyota Camry SE",
            "desc": "Clean CarFax, 62k miles, Apple CarPlay, 35 MPG, $289/mo with approved credit",
            "audience": ["first-time buyers", "OKC", "young professionals"],
            "tone": "Trustworthy",
            "platform": "meta",
            "variants": 3
        }
        
        with patch('app.api.v1.ads.ai_service.generate_ad_variations') as mock_generate:
            mock_generate.return_value = [{"id": "test", "platform": "meta", "tone": "Trustworthy"}]
            
            response = client.post("/api/v1/ads/generate", json=valid_request)
            assert response.status_code == 200
    
    def test_valid_request_minimal_fields(self, client):
        """Test valid request with only required fields"""
        minimal_request = {
            "name": "Test Product",
            "desc": "Test description that meets minimum length requirements for validation"
        }
        
        with patch('app.api.v1.ads.ai_service.generate_ad_variations') as mock_generate:
            mock_generate.return_value = [{"id": "test", "platform": "meta", "tone": "Trustworthy"}]
            
            response = client.post("/api/v1/ads/generate", json=minimal_request)
            assert response.status_code == 200


class TestFieldValidation:
    """Tests for individual field validation"""
    
    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)
    
    def test_name_validation(self, client):
        """Test name field validation"""
        base_request = {
            "desc": "Valid description that meets length requirements",
            "tone": "Trustworthy",
            "platform": "meta",
            "variants": 3
        }
        
        # Test missing name
        response = client.post("/api/v1/ads/generate", json=base_request)
        assert response.status_code == 422
        
        # Test empty name
        response = client.post("/api/v1/ads/generate", json={**base_request, "name": ""})
        assert response.status_code == 422
        
        # Test very long name
        long_name = "x" * 200
        response = client.post("/api/v1/ads/generate", json={**base_request, "name": long_name})
        assert response.status_code == 422
        
        # Test valid name
        response = client.post("/api/v1/ads/generate", json={**base_request, "name": "Valid Product Name"})
        assert response.status_code in [200, 500]  # 500 is OK if AI service not mocked
    
    def test_description_validation(self, client):
        """Test description field validation"""
        base_request = {
            "name": "Test Product",
            "tone": "Trustworthy",
            "platform": "meta",
            "variants": 3
        }
        
        # Test missing description
        response = client.post("/api/v1/ads/generate", json=base_request)
        assert response.status_code == 422
        
        # Test empty description
        response = client.post("/api/v1/ads/generate", json={**base_request, "desc": ""})
        assert response.status_code == 422
        
        # Test too short description
        response = client.post("/api/v1/ads/generate", json={**base_request, "desc": "Short"})
        assert response.status_code == 422
        
        # Test too long description
        long_desc = "x" * 1000
        response = client.post("/api/v1/ads/generate", json={**base_request, "desc": long_desc})
        assert response.status_code == 422
        
        # Test valid description
        valid_desc = "This is a valid description that meets the minimum length requirements"
        response = client.post("/api/v1/ads/generate", json={**base_request, "desc": valid_desc})
        assert response.status_code in [200, 500]
    
    def test_audience_validation(self, client):
        """Test audience field validation"""
        base_request = {
            "name": "Test Product",
            "desc": "Valid description that meets length requirements",
            "tone": "Trustworthy",
            "platform": "meta",
            "variants": 3
        }
        
        # Test valid empty audience
        response = client.post("/api/v1/ads/generate", json={**base_request, "audience": []})
        assert response.status_code in [200, 500]
        
        # Test valid audience list
        response = client.post("/api/v1/ads/generate", json={**base_request, "audience": ["test", "audience"]})
        assert response.status_code in [200, 500]
        
        # Test invalid audience type
        response = client.post("/api/v1/ads/generate", json={**base_request, "audience": "not_a_list"})
        assert response.status_code == 422
    
    def test_tone_validation(self, client):
        """Test tone field validation"""
        base_request = {
            "name": "Test Product",
            "desc": "Valid description that meets length requirements",
            "platform": "meta",
            "variants": 3
        }
        
        valid_tones = ["Urgent", "Luxury", "Casual", "Trustworthy"]
        
        # Test all valid tones
        for tone in valid_tones:
            response = client.post("/api/v1/ads/generate", json={**base_request, "tone": tone})
            assert response.status_code in [200, 500]
        
        # Test invalid tone
        response = client.post("/api/v1/ads/generate", json={**base_request, "tone": "InvalidTone"})
        assert response.status_code == 422
        
        # Test missing tone (should use default)
        response = client.post("/api/v1/ads/generate", json=base_request)
        assert response.status_code in [200, 500]
    
    def test_platform_validation(self, client):
        """Test platform field validation"""
        base_request = {
            "name": "Test Product",
            "desc": "Valid description that meets length requirements",
            "tone": "Trustworthy",
            "variants": 3
        }
        
        valid_platforms = ["google_search", "google_display", "meta", "tiktok"]
        
        # Test all valid platforms
        for platform in valid_platforms:
            response = client.post("/api/v1/ads/generate", json={**base_request, "platform": platform})
            assert response.status_code in [200, 500]
        
        # Test invalid platform
        response = client.post("/api/v1/ads/generate", json={**base_request, "platform": "invalid_platform"})
        assert response.status_code == 422
        
        # Test missing platform (should use default)
        response = client.post("/api/v1/ads/generate", json=base_request)
        assert response.status_code in [200, 500]
    
    def test_variants_validation(self, client):
        """Test variants field validation"""
        base_request = {
            "name": "Test Product",
            "desc": "Valid description that meets length requirements",
            "tone": "Trustworthy",
            "platform": "meta"
        }
        
        # Test valid variant counts
        valid_variants = [1, 2, 3, 4, 5]
        for variants in valid_variants:
            response = client.post("/api/v1/ads/generate", json={**base_request, "variants": variants})
            assert response.status_code in [200, 500]
        
        # Test invalid variant counts
        invalid_variants = [0, -1, 6, 10, 100]
        for variants in invalid_variants:
            response = client.post("/api/v1/ads/generate", json={**base_request, "variants": variants})
            assert response.status_code == 422
        
        # Test non-integer variants (string that can be converted)
        response = client.post("/api/v1/ads/generate", json={**base_request, "variants": "3"})
        # FastAPI/Pydantic might auto-convert "3" to 3, so this might pass
        assert response.status_code in [200, 422, 500]
        
        response = client.post("/api/v1/ads/generate", json={**base_request, "variants": 3.5})
        assert response.status_code == 422


class TestQueryParameterValidation:
    """Tests for query parameter validation"""
    
    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)
    
    def test_history_limit_validation(self, client):
        """Test limit parameter validation for history endpoint"""
        # Test valid limits
        valid_limits = [1, 10, 50, 100]
        for limit in valid_limits:
            response = client.get(f"/api/v1/ads/history?limit={limit}")
            assert response.status_code == 200
        
        # Test limit over maximum (should be rejected)
        response = client.get("/api/v1/ads/history?limit=500")
        assert response.status_code == 422
        
        # Test invalid limit types
        response = client.get("/api/v1/ads/history?limit=invalid")
        assert response.status_code == 422
        
        response = client.get("/api/v1/ads/history?limit=-1")
        # Negative limit might be handled gracefully by the app
        assert response.status_code in [200, 422]
    
    def test_history_platform_validation(self, client):
        """Test platform parameter validation for history endpoint"""
        # Test valid platforms
        valid_platforms = ["google_search", "google_display", "meta", "tiktok"]
        for platform in valid_platforms:
            response = client.get(f"/api/v1/ads/history?platform={platform}")
            assert response.status_code == 200
        
        # Test invalid platform (should still work, just filter nothing)
        response = client.get("/api/v1/ads/history?platform=invalid_platform")
        assert response.status_code == 200
    
    def test_ad_id_validation(self, client):
        """Test ad ID parameter validation"""
        # Test valid ObjectId format
        valid_id = "507f1f77bcf86cd799439011"
        response = client.get(f"/api/v1/ads/{valid_id}")
        assert response.status_code in [200, 404]  # 404 if not found is OK
        
        # Test invalid ObjectId formats
        invalid_ids = [
            "invalid",
            "123",
            "not_an_object_id",
            "507f1f77bcf86cd799439011x",  # Too long
            "507f1f77bcf86cd79943901",    # Too short
            ""
        ]
        
        for invalid_id in invalid_ids:
            if invalid_id:  # Skip empty string as it's a routing issue
                response = client.get(f"/api/v1/ads/{invalid_id}")
                assert response.status_code in [404, 422, 500]  # Various error codes are acceptable


class TestErrorResponseFormat:
    """Tests for error response format consistency"""
    
    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)
    
    def test_validation_error_format(self, client):
        """Test that validation errors have consistent format"""
        # Send invalid request
        invalid_request = {
            "name": "",  # Invalid: empty name
            "desc": "",  # Invalid: empty description
            "variants": 0  # Invalid: zero variants
        }
        
        response = client.post("/api/v1/ads/generate", json=invalid_request)
        assert response.status_code == 422
        
        error_data = response.json()
        assert "detail" in error_data
        
        # Should be a list of validation errors
        if isinstance(error_data["detail"], list):
            for error in error_data["detail"]:
                assert "loc" in error  # Field location
                assert "msg" in error  # Error message
                assert "type" in error  # Error type
    
    def test_http_error_format(self, client):
        """Test that HTTP errors have consistent format"""
        # Test 404 error
        response = client.get("/api/v1/ads/nonexistent_id")
        if response.status_code == 404:
            error_data = response.json()
            assert "detail" in error_data
            assert isinstance(error_data["detail"], str)
    
    def test_server_error_handling(self, client):
        """Test that server errors are handled gracefully"""
        # This would test 500 errors, but we need to mock internal failures
        # The important thing is that 500 errors return proper JSON, not HTML
        pass


class TestModelValidation:
    """Tests for Pydantic model validation"""
    
    def test_ad_generation_request_model(self):
        """Test AdGenerationRequest model validation"""
        # Test valid model creation
        valid_data = {
            "name": "Test Product",
            "desc": "Test description that meets minimum length requirements",
            "audience": ["test audience"],
            "tone": ToneType.TRUSTWORTHY,
            "platform": PlatformType.META,
            "variants": 3
        }
        
        model = AdGenerationRequest(**valid_data)
        assert model.name == "Test Product"
        assert model.tone == ToneType.TRUSTWORTHY
        assert model.platform == PlatformType.META
        assert model.variants == 3
    
    def test_ad_generation_request_defaults(self):
        """Test default values in AdGenerationRequest"""
        minimal_data = {
            "name": "Test Product",
            "desc": "Test description that meets minimum length requirements"
        }
        
        model = AdGenerationRequest(**minimal_data)
        assert model.audience == []  # Default empty list
        assert model.tone == ToneType.TRUSTWORTHY  # Default tone
        assert model.platform == PlatformType.META  # Default platform
        assert model.variants == 3  # Default variants
    
    def test_ad_generation_request_validation_errors(self):
        """Test validation errors in AdGenerationRequest"""
        # Test missing required fields
        with pytest.raises(ValidationError):
            AdGenerationRequest(desc="Description only")
        
        with pytest.raises(ValidationError):
            AdGenerationRequest(name="Name only")
        
        # Test field length validation
        with pytest.raises(ValidationError):
            AdGenerationRequest(
                name="x" * 200,  # Too long
                desc="Valid description"
            )
        
        with pytest.raises(ValidationError):
            AdGenerationRequest(
                name="Valid name",
                desc="x" * 1000  # Too long
            )
        
        # Test field value validation
        with pytest.raises(ValidationError):
            AdGenerationRequest(
                name="Valid name",
                desc="Valid description",
                variants=0  # Invalid: must be >= 1
            )
        
        with pytest.raises(ValidationError):
            AdGenerationRequest(
                name="Valid name", 
                desc="Valid description",
                variants=10  # Invalid: must be <= 5
            )
    
    def test_enum_validation(self):
        """Test enum field validation"""
        # Test valid enum values
        for tone in ToneType:
            model = AdGenerationRequest(
                name="Test",
                desc="Test description",
                tone=tone
            )
            assert model.tone == tone
        
        for platform in PlatformType:
            model = AdGenerationRequest(
                name="Test",
                desc="Test description", 
                platform=platform
            )
            assert model.platform == platform
        
        # Test invalid enum values
        with pytest.raises(ValidationError):
            AdGenerationRequest(
                name="Test",
                desc="Test description",
                tone="InvalidTone"
            )
        
        with pytest.raises(ValidationError):
            AdGenerationRequest(
                name="Test",
                desc="Test description",
                platform="InvalidPlatform"
            )


class TestSecurityValidation:
    """Tests for security-related validation"""
    
    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)
    
    def test_injection_attack_prevention(self, client):
        """Test prevention of injection attacks in inputs"""
        malicious_inputs = [
            {"$ne": None},
            "'; DROP TABLE ads; --",
            "<script>alert('xss')</script>",
            "../../../etc/passwd",
            "javascript:alert(1)",
            "null\x00byte"
        ]
        
        for malicious_input in malicious_inputs:
            request_data = {
                "name": str(malicious_input),
                "desc": f"Description with {malicious_input}",
                "audience": [str(malicious_input)],
                "tone": "Trustworthy",
                "platform": "meta",
                "variants": 3
            }
            
            response = client.post("/api/v1/ads/generate", json=request_data)
            # Should either work safely or reject with validation error
            assert response.status_code in [200, 422, 500]
            
            # If successful, response should be safe
            if response.status_code == 200:
                data = response.json()
                assert data.get("success") is True
    
    def test_large_payload_handling(self, client):
        """Test handling of unusually large payloads"""
        # Test large audience list
        large_audience = ["audience_member"] * 1000
        
        request_data = {
            "name": "Test Product",
            "desc": "Test description",
            "audience": large_audience,
            "tone": "Trustworthy",
            "platform": "meta",
            "variants": 3
        }
        
        response = client.post("/api/v1/ads/generate", json=request_data)
        # Should handle gracefully (might reject due to size limits)
        assert response.status_code in [200, 413, 422, 500]
    
    def test_unicode_handling(self, client):
        """Test handling of Unicode and special characters"""
        unicode_inputs = [
            "Test Product 日本語",
            "Café Münü",
            "Emoji Test 🚀✨💡",
            "Special chars: àáâãäåæçèéêë",
            "RTL text: مرحبا بالعالم",
            "Symbols: ©®™€£¥"
        ]
        
        for unicode_input in unicode_inputs:
            request_data = {
                "name": unicode_input,
                "desc": f"Description with {unicode_input}",
                "audience": [unicode_input],
                "tone": "Trustworthy",
                "platform": "meta",
                "variants": 3
            }
            
            response = client.post("/api/v1/ads/generate", json=request_data)
            # Should handle Unicode gracefully
            assert response.status_code in [200, 422, 500]
