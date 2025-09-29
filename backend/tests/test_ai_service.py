"""
Comprehensive tests for AI service (DeepSeek integration and fallback)
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
import httpx
import json

from app.services.ai_service import DeepSeekService
from app.models.ad import AdGenerationRequest, PlatformType, ToneType


class TestDeepSeekService:
    """Tests for DeepSeek AI service"""
    
    @pytest.fixture
    def ai_service(self):
        """Create AI service instance"""
        return DeepSeekService()
    
    @pytest.fixture
    def sample_request(self):
        """Sample ad generation request"""
        return AdGenerationRequest(
            name="2019 Toyota Camry SE",
            desc="Clean CarFax, 62k miles, Apple CarPlay, 35 MPG, $289/mo",
            audience=["first-time buyers", "OKC"],
            tone=ToneType.TRUSTWORTHY,
            platform=PlatformType.META,
            variants=3
        )
    
    @pytest.fixture
    def sample_ad_request(self):
        """Another sample ad generation request for consistency"""
        return AdGenerationRequest(
            name="Test Product",
            desc="Test description that meets minimum length requirements",
            audience=["test audience"],
            tone=ToneType.TRUSTWORTHY,
            platform=PlatformType.META,
            variants=3
        )
    
    async def test_generate_with_api_key_success(self, ai_service, sample_request, mock_deepseek_api):
        """Test successful AI generation with API key"""
        with patch.object(ai_service, 'api_key', 'test_api_key'):
            with patch.object(ai_service, '_call_deepseek_api', return_value=mock_deepseek_api):
                variations = await ai_service.generate_ad_variations(sample_request)
                
                assert len(variations) > 0
                assert variations[0]['platform'] == 'meta'
                assert variations[0]['tone'] == 'Trustworthy'
                assert 'primary' in variations[0]
                assert 'headline' in variations[0]
                assert 'description' in variations[0]
    
    async def test_generate_without_api_key_fallback(self, ai_service, sample_request):
        """Test fallback generation when no API key"""
        with patch.object(ai_service, 'api_key', ''):
            variations = await ai_service.generate_ad_variations(sample_request)
            
            assert len(variations) == 3  # Should match requested variants
            assert all(v['platform'] == 'meta' for v in variations)
            assert all(v['tone'] == 'Trustworthy' for v in variations)
    
    async def test_generate_api_error_fallback(self, ai_service, sample_request):
        """Test fallback when API call fails"""
        with patch.object(ai_service, 'api_key', 'test_api_key'):
            with patch.object(ai_service, '_call_deepseek_api', side_effect=Exception("API Error")):
                variations = await ai_service.generate_ad_variations(sample_request)
                
                assert len(variations) == 3  # Should still generate fallback
                assert all(v['platform'] == 'meta' for v in variations)
    
    def test_create_prompt_structure(self, ai_service, sample_request):
        """Test prompt creation structure"""
        prompt = ai_service._create_prompt(sample_request)
        
        # Check that all essential elements are in prompt
        assert "2019 Toyota Camry SE" in prompt
        assert "Clean CarFax" in prompt
        assert "first-time buyers" in prompt
        assert "Trustworthy" in prompt
        assert "meta" in prompt
        assert "JSON" in prompt
        assert "variations" in prompt
    
    def test_platform_specs_all_platforms(self, ai_service):
        """Test platform specifications for all platforms"""
        platforms = [PlatformType.GOOGLE_SEARCH, PlatformType.GOOGLE_DISPLAY, PlatformType.META, PlatformType.TIKTOK]
        
        for platform in platforms:
            specs = ai_service._get_platform_specs(platform)
            assert len(specs) > 0
            assert isinstance(specs, str)
    
    def test_business_context_detection(self, ai_service):
        """Test business context detection"""
        # Test automotive detection
        auto_context = ai_service._get_business_context("2019 Toyota Camry", "Clean CarFax, low miles")
        assert "automotive" in auto_context.lower() or "financing" in auto_context.lower()
        
        # Test ecommerce detection
        ecom_context = ai_service._get_business_context("iPhone Case", "Buy online with free shipping")
        assert "ecommerce" in ecom_context.lower() or "shipping" in ecom_context.lower()
    
    def test_response_format_all_platforms(self, ai_service):
        """Test JSON response format for all platforms"""
        platforms = [PlatformType.GOOGLE_SEARCH, PlatformType.GOOGLE_DISPLAY, PlatformType.META, PlatformType.TIKTOK]
        
        for platform in platforms:
            format_str = ai_service._get_response_format(platform)
            assert "variations" in format_str
            assert "{" in format_str and "}" in format_str  # Valid JSON structure
    
    async def test_call_deepseek_api_request_structure(self, ai_service):
        """Test DeepSeek API call structure"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {"choices": [{"message": {"content": "test"}}]}
            mock_response.raise_for_status.return_value = None
            
            mock_client_instance = Mock()
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            with patch.object(ai_service, 'api_key', 'test_key'):
                await ai_service._call_deepseek_api(mock_client_instance, "test prompt")
                
                # Verify API call structure
                call_args = mock_client_instance.post.call_args
                assert call_args[0][0] == "https://api.deepseek.com/v1/chat/completions"
                
                headers = call_args[1]['headers']
                assert headers['Authorization'] == 'Bearer test_key'
                assert headers['Content-Type'] == 'application/json'
                
                payload = call_args[1]['json']
                assert payload['model'] == 'deepseek-chat'
                assert 'messages' in payload
                assert payload['messages'][0]['content'] == 'test prompt'
    
    def test_parse_ai_response_valid_json(self, ai_service, sample_request, mock_deepseek_api):
        """Test parsing valid AI response"""
        variations = ai_service._parse_ai_response(mock_deepseek_api, sample_request)
        
        assert len(variations) > 0
        assert 'id' in variations[0]
        assert variations[0]['platform'] == 'meta'
        assert variations[0]['tone'] == 'Trustworthy'
    
    def test_parse_ai_response_invalid_json(self, ai_service, sample_request):
        """Test parsing invalid AI response falls back"""
        invalid_response = {
            "choices": [
                {
                    "message": {
                        "content": "Invalid JSON content"
                    }
                }
            ]
        }
        
        variations = ai_service._parse_ai_response(invalid_response, sample_request)
        
        # Should fallback to template generation
        assert len(variations) == 3
        assert all(v['platform'] == 'meta' for v in variations)


class TestFallbackGeneration:
    """Tests for template-based fallback generation"""
    
    @pytest.fixture
    def ai_service(self):
        return DeepSeekService()
    
    def test_fallback_all_platforms(self, ai_service):
        """Test fallback generation for all platforms"""
        platforms = [PlatformType.GOOGLE_SEARCH, PlatformType.GOOGLE_DISPLAY, PlatformType.META, PlatformType.TIKTOK]
        
        for platform in platforms:
            request = AdGenerationRequest(
                name="Test Product",
                desc="Test description with features and benefits",
                audience=["test audience"],
                tone=ToneType.TRUSTWORTHY,
                platform=platform,
                variants=3
            )
            
            variations = ai_service._create_fallback_variations(request)
            
            assert len(variations) == 3
            assert all(v['platform'] == platform.value for v in variations)
            assert all(v['tone'] == 'Trustworthy' for v in variations)
    
    def test_fallback_all_tones(self, ai_service):
        """Test fallback generation for all tones"""
        tones = [ToneType.URGENT, ToneType.LUXURY, ToneType.CASUAL, ToneType.TRUSTWORTHY]
        
        for tone in tones:
            request = AdGenerationRequest(
                name="Test Product",
                desc="Test description",
                audience=[],
                tone=tone,
                platform=PlatformType.META,
                variants=2
            )
            
            variations = ai_service._create_fallback_variations(request)
            
            assert len(variations) == 2
            assert all(v['tone'] == tone.value for v in variations)
    
    def test_fallback_automotive_detection(self, ai_service):
        """Test automotive-specific fallback generation"""
        request = AdGenerationRequest(
            name="2019 Honda Civic",
            desc="Low mileage, clean title, great condition",
            audience=["car buyers"],
            tone=ToneType.TRUSTWORTHY,
            platform=PlatformType.META,
            variants=1
        )
        
        variations = ai_service._create_fallback_variations(request)
        variation = variations[0]
        
        # Should include automotive-specific elements
        assert any("miles" in text.lower() for text in [variation.get('primary', ''), variation.get('headline', '')])
    
    def test_fallback_character_limits(self, ai_service):
        """Test that fallback respects character limits"""
        request = AdGenerationRequest(
            name="Very Long Product Name That Exceeds Character Limits For Testing Purposes",
            desc="Very long description " * 10,
            audience=["test"],
            tone=ToneType.TRUSTWORTHY,
            platform=PlatformType.META,
            variants=1
        )
        
        variations = ai_service._create_fallback_variations(request)
        variation = variations[0]
        
        # Check Meta platform limits
        assert len(variation['primary']) <= 125
        assert len(variation['headline']) <= 40
        assert len(variation['description']) <= 30
    
    def test_truncate_function(self, ai_service):
        """Test text truncation utility"""
        # Test basic truncation
        result = ai_service._truncate("This is a long text", 10)
        assert len(result) <= 10
        
        # Test truncation at word boundary
        result = ai_service._truncate("This is a test", 8)
        assert result == "This is"  # Should break at word boundary
        
        # Test text shorter than limit
        result = ai_service._truncate("Short", 10)
        assert result == "Short"
        
        # Test empty text
        result = ai_service._truncate("", 10)
        assert result == ""
    
    def test_get_tone_angle(self, ai_service):
        """Test tone angle generation"""
        angles = {
            ToneType.URGENT: ai_service._get_tone_angle(ToneType.URGENT),
            ToneType.LUXURY: ai_service._get_tone_angle(ToneType.LUXURY),
            ToneType.CASUAL: ai_service._get_tone_angle(ToneType.CASUAL),
            ToneType.TRUSTWORTHY: ai_service._get_tone_angle(ToneType.TRUSTWORTHY)
        }
        
        # Each tone should have a unique angle
        assert len(set(angles.values())) == len(angles)
        assert all(isinstance(angle, str) and len(angle) > 0 for angle in angles.values())
    
    def test_extract_offer(self, ai_service):
        """Test offer extraction from description"""
        # Test price extraction
        desc_with_price = "Great product for $299.99 with free shipping"
        offer = ai_service._extract_offer(desc_with_price)
        assert "$299" in offer  # Extract method might strip decimals
        
        # Test monthly payment
        desc_with_monthly = "Available for $99/month with financing"
        offer = ai_service._extract_offer(desc_with_monthly)
        assert "99" in offer and ("mo" in offer.lower() or "month" in offer.lower())
        
        # Test no offer found
        desc_no_offer = "Great product with amazing features"
        offer = ai_service._extract_offer(desc_no_offer)
        assert "special pricing" in offer.lower() or "available" in offer.lower()


class TestEdgeCases:
    """Test edge cases and error scenarios"""
    
    @pytest.fixture
    def ai_service(self):
        return DeepSeekService()
    
    @pytest.fixture
    def sample_ad_request(self):
        """Sample ad generation request for testing"""
        return AdGenerationRequest(
            name="Test Product",
            desc="Test description that meets minimum length requirements",
            audience=["test audience"],
            tone=ToneType.TRUSTWORTHY,
            platform=PlatformType.META,
            variants=3
        )
    
    async def test_empty_request_fields(self, ai_service):
        """Test handling of empty request fields"""
        request = AdGenerationRequest(
            name="",
            desc="",
            audience=[],
            tone=ToneType.TRUSTWORTHY,
            platform=PlatformType.META,
            variants=1
        )
        
        # Should not crash, should generate something
        variations = await ai_service.generate_ad_variations(request)
        assert len(variations) == 1
    
    async def test_maximum_variants(self, ai_service):
        """Test maximum number of variants"""
        request = AdGenerationRequest(
            name="Test Product",
            desc="Test description",
            audience=[],
            tone=ToneType.TRUSTWORTHY,
            platform=PlatformType.META,
            variants=5  # Maximum allowed
        )
        
        variations = await ai_service.generate_ad_variations(request)
        assert len(variations) == 5
    
    def test_unicode_content(self, ai_service):
        """Test handling of unicode content"""
        request = AdGenerationRequest(
            name="Café Münü 日本語",
            desc="Special characters: àáâãäåæçèéêë ñòóôõöøùúûü",
            audience=["international"],
            tone=ToneType.LUXURY,
            platform=PlatformType.META,
            variants=1
        )
        
        variations = ai_service._create_fallback_variations(request)
        assert len(variations) == 1
        # Should not crash with unicode content
    
    async def test_network_timeout_handling(self, ai_service, sample_ad_request):
        """Test handling of network timeouts"""
        with patch.object(ai_service, 'api_key', 'test_key'):
            with patch.object(ai_service, '_call_deepseek_api', side_effect=httpx.TimeoutException("Timeout")):
                variations = await ai_service.generate_ad_variations(sample_ad_request)
                
                # Should fallback gracefully
                assert len(variations) > 0
    
    async def test_malformed_api_response(self, ai_service, sample_ad_request):
        """Test handling of malformed API responses"""
        malformed_responses = [
            {"invalid": "structure"},
            {"choices": []},
            {"choices": [{"message": {}}]},
            {"choices": [{"message": {"content": None}}]},
        ]

        with patch.object(ai_service, 'api_key', 'test_key'):
            for malformed_response in malformed_responses:
                with patch.object(ai_service, '_call_deepseek_api', return_value=malformed_response):
                    variations = await ai_service.generate_ad_variations(sample_ad_request)
                    
                    # Should fallback gracefully
                    assert len(variations) > 0
