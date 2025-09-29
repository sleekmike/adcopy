"""
AI Service for generating ad copy using DeepSeek API
"""
import httpx
import json
import uuid
from typing import List, Dict, Any
from app.models.ad import (
    AdGenerationRequest, 
    PlatformType, 
    ToneType, 
    PLATFORM_LIMITS,
    GoogleSearchVariation,
    GoogleDisplayVariation, 
    MetaVariation,
    TikTokVariation
)
from app.core.config import settings

class DeepSeekService:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL
        
    async def generate_ad_variations(self, request: AdGenerationRequest) -> List[Dict[str, Any]]:
        """Generate ad variations using DeepSeek API"""
        
        # If no API key, use fallback generator
        if not self.api_key:
            return self._create_fallback_variations(request)
            
        try:
            # Create AI prompt
            prompt = self._create_prompt(request)
            
            # Call DeepSeek API
            async with httpx.AsyncClient() as client:
                response = await self._call_deepseek_api(client, prompt)
                
            # Parse and format response
            variations = self._parse_ai_response(response, request)
            return variations
            
        except Exception as e:
            print(f"AI API error: {str(e)}")
            # Fallback to template-based generation
            return self._create_fallback_variations(request)
    
    def _create_prompt(self, request: AdGenerationRequest) -> str:
        """Create optimized prompt for DeepSeek"""
        
        platform_specs = self._get_platform_specs(request.platform)
        business_context = self._get_business_context(request.name, request.desc)
        audience_str = ", ".join(request.audience) if request.audience else "general audience"
        
        prompt = f"""You are an expert copywriter specializing in high-converting {request.platform.value} ads.

Create {request.variants} different ad variations with these requirements:

PRODUCT/SERVICE: {request.name}
DESCRIPTION: {request.desc}
TARGET AUDIENCE: {audience_str}
TONE: {request.tone.value}
PLATFORM: {request.platform.value}

PLATFORM REQUIREMENTS:
{platform_specs}

{business_context}

FORMAT YOUR RESPONSE AS JSON:
{self._get_response_format(request.platform)}

COPYWRITING BEST PRACTICES:
- Use power words and emotional triggers
- Include social proof when relevant  
- Create urgency without being pushy
- Address pain points and benefits
- Use numbers and specifics when possible
- Match the {request.tone.value} tone exactly
- Stay within character limits

Focus on what converts for {audience_str} on {request.platform.value}."""

        return prompt
    
    def _get_platform_specs(self, platform: PlatformType) -> str:
        """Get platform-specific requirements"""
        specs = {
            PlatformType.GOOGLE_SEARCH: "Headlines: 30 chars max (3 needed), Descriptions: 90 chars max (2 needed). Focus on search intent.",
            PlatformType.GOOGLE_DISPLAY: "Short headline: 30 chars, Long headline: 90 chars, Descriptions: 90 chars each (2 needed).",
            PlatformType.META: "Primary text: 125 chars (soft), Headline: 40 chars (soft), Description: 30 chars (soft). Visual-first platform.",
            PlatformType.TIKTOK: "Caption: 100 chars (soft). Short, punchy, casual. Hook in first 3 words."
        }
        return specs.get(platform, "General social media best practices")
    
    def _get_business_context(self, name: str, desc: str) -> str:
        """Get business-specific context from product info"""
        
        # Detect business type from name/description
        name_lower = name.lower()
        desc_lower = desc.lower()
        
        if any(word in name_lower or word in desc_lower for word in ['car', 'auto', 'vehicle', 'toyota', 'honda', 'ford', 'camry', 'dealership']):
            return """
AUTOMOTIVE CONTEXT:
- Emphasize reliability, financing options, warranties
- Include mileage, year, features if available
- Focus on local market and trade-in value
- Use trust-building language for high-ticket purchases"""
        
        elif any(word in name_lower or word in desc_lower for word in ['shop', 'buy', 'order', 'shipping', 'ecommerce', 'store']):
            return """
ECOMMERCE CONTEXT:  
- Highlight product benefits and unique features
- Include pricing, shipping, or return policies
- Create urgency with limited offers
- Focus on convenience and value"""
        
        else:
            return """
GENERAL BUSINESS CONTEXT:
- Focus on main value proposition
- Highlight what makes you different
- Include social proof when possible
- Create clear call-to-action"""
    
    def _get_response_format(self, platform: PlatformType) -> str:
        """Get expected JSON format for platform"""
        
        if platform == PlatformType.GOOGLE_SEARCH:
            return """
{
  "variations": [
    {
      "headlines": ["30 char headline 1", "30 char headline 2", "30 char headline 3"],
      "descriptions": ["90 char description 1", "90 char description 2"]
    }
  ]
}"""
        
        elif platform == PlatformType.GOOGLE_DISPLAY:
            return """
{
  "variations": [
    {
      "shortHeadline": "30 char short headline",
      "longHeadline": "90 char long headline", 
      "descriptions": ["90 char description 1", "90 char description 2"]
    }
  ]
}"""
        
        elif platform == PlatformType.META:
            return """
{
  "variations": [
    {
      "primary": "125 char primary text",
      "headline": "40 char headline",
      "description": "30 char description"
    }
  ]
}"""
        
        elif platform == PlatformType.TIKTOK:
            return """
{
  "variations": [
    {
      "caption": "100 char caption with hashtags"
    }
  ]
}"""
    
    async def _call_deepseek_api(self, client: httpx.AsyncClient, prompt: str) -> Dict[str, Any]:
        """Make API call to DeepSeek"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": settings.DEEPSEEK_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.8
        }
        
        response = await client.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30.0
        )
        
        response.raise_for_status()
        return response.json()
    
    def _parse_ai_response(self, api_response: Dict[str, Any], request: AdGenerationRequest) -> List[Dict[str, Any]]:
        """Parse DeepSeek API response into structured variations"""
        
        try:
            content = api_response["choices"][0]["message"]["content"]
            
            # Extract JSON from response
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end]
            else:
                json_content = content
                
            parsed = json.loads(json_content)
            variations = []
            
            for i, var_data in enumerate(parsed.get("variations", [])[:request.variants]):
                variation = self._format_variation(var_data, request.platform, request.tone.value, i)
                variations.append(variation)
                
            return variations
            
        except Exception as e:
            print(f"Error parsing AI response: {str(e)}")
            return self._create_fallback_variations(request)
    
    def _format_variation(self, var_data: Dict[str, Any], platform: PlatformType, tone: str, index: int) -> Dict[str, Any]:
        """Format AI response into platform-specific variation"""
        
        variation_id = str(uuid.uuid4())[:8]
        
        if platform == PlatformType.GOOGLE_SEARCH:
            return {
                "id": variation_id,
                "platform": "google_search", 
                "tone": tone,
                "headlines": var_data.get("headlines", ["Default headline"] * 3),
                "descriptions": var_data.get("descriptions", ["Default description"] * 2)
            }
            
        elif platform == PlatformType.GOOGLE_DISPLAY:
            return {
                "id": variation_id,
                "platform": "google_display",
                "tone": tone,
                "shortHeadline": var_data.get("shortHeadline", "Default short"),
                "longHeadline": var_data.get("longHeadline", "Default long headline"),
                "descriptions": var_data.get("descriptions", ["Default description"] * 2)
            }
            
        elif platform == PlatformType.META:
            return {
                "id": variation_id,
                "platform": "meta",
                "tone": tone,
                "primary": var_data.get("primary", "Default primary text"),
                "headline": var_data.get("headline", "Default headline"),
                "description": var_data.get("description", "Default desc")
            }
            
        elif platform == PlatformType.TIKTOK:
            return {
                "id": variation_id,
                "platform": "tiktok",
                "tone": tone,
                "caption": var_data.get("caption", "Default caption #hashtag")
            }
    
    def _create_fallback_variations(self, request: AdGenerationRequest) -> List[Dict[str, Any]]:
        """Create template-based variations when AI fails"""
        
        variations = []
        
        for i in range(request.variants):
            variation_id = str(uuid.uuid4())[:8]
            
            # Template-based generation (similar to your frontend logic)
            angle = self._get_tone_angle(request.tone)
            proof = self._get_proof_element(request.name, request.desc)
            aud = f"For {', '.join(request.audience)}." if request.audience else ""
            benefit = request.desc.split('.')[0] if '.' in request.desc else "Get more for less"
            offer = self._extract_offer(request.desc)
            
            if request.platform == PlatformType.GOOGLE_SEARCH:
                variation = {
                    "id": variation_id,
                    "platform": "google_search",
                    "tone": request.tone.value,
                    "headlines": [
                        self._truncate(f"{request.name} — {angle}", 30),
                        self._truncate(benefit, 30),
                        self._truncate(f"In Stock • {request.tone.value}", 30)
                    ],
                    "descriptions": [
                        self._truncate(f"{benefit}. {aud} {proof}", 90),
                        self._truncate(f"{offer}. Visit now.", 90)
                    ]
                }
                
            elif request.platform == PlatformType.GOOGLE_DISPLAY:
                variation = {
                    "id": variation_id,
                    "platform": "google_display",
                    "tone": request.tone.value,
                    "shortHeadline": self._truncate(request.name, 30),
                    "longHeadline": self._truncate(f"{angle}: {benefit}", 90),
                    "descriptions": [
                        self._truncate(f"{benefit}. {aud}", 90),
                        self._truncate(f"{offer}. {proof}", 90)
                    ]
                }
                
            elif request.platform == PlatformType.META:
                variation = {
                    "id": variation_id,
                    "platform": "meta",
                    "tone": request.tone.value,
                    "primary": self._truncate(f"{benefit}. {aud} {proof}", 125),
                    "headline": self._truncate(f"{request.name} — {angle}", 40),
                    "description": self._truncate(offer or "Shop now", 30)
                }
                
            elif request.platform == PlatformType.TIKTOK:
                variation = {
                    "id": variation_id,
                    "platform": "tiktok", 
                    "tone": request.tone.value,
                    "caption": self._truncate(f"{angle}! {benefit}. {offer} #{request.name.split()[0]}", 100)
                }
            
            variations.append(variation)
            
        return variations
    
    def _get_tone_angle(self, tone: ToneType) -> str:
        """Get angle based on tone"""
        angles = {
            ToneType.URGENT: "Today only",
            ToneType.LUXURY: "Premium experience", 
            ToneType.CASUAL: "No hassle",
            ToneType.TRUSTWORTHY: "Trusted choice"
        }
        return angles.get(tone, "Great value")
    
    def _get_proof_element(self, name: str, desc: str) -> str:
        """Generate proof element"""
        if any(char.isdigit() for char in name) and "20" in name:
            return "Low miles. Clean title."
        return "Top-rated by customers."
    
    def _extract_offer(self, desc: str) -> str:
        """Extract offer from description"""
        import re
        offer_match = re.search(r'\$[^\s,.]+[^.]*|\d+\s?(?:mo|month|down)', desc, re.IGNORECASE)
        return offer_match.group(0) if offer_match else "Special pricing available"
    
    def _truncate(self, text: str, max_length: int) -> str:
        """Truncate text to character limit"""
        if not text or len(text) <= max_length:
            return text or ""
            
        # Find last space before limit
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > 0:
            return truncated[:last_space].strip()
        return truncated.strip()
