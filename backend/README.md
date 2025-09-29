# AI Ad Copy Generator - Backend

A production-ready FastAPI backend for generating high-converting ad copy using DeepSeek AI, with MongoDB storage and comprehensive testing.

## 🚀 Features

- 🤖 **AI-powered ad generation** using DeepSeek LLM
- 🎯 **Platform-specific optimization** (Google Search, Google Display, Meta, TikTok)
- 📊 **Character limit compliance** for each platform
- 💾 **MongoDB storage** with PyMongo for persistence
- 🚀 **Fast async API** with automatic OpenAPI docs
- 🔄 **Robust fallback system** when AI is unavailable
- ✅ **Comprehensive unit tests** with pytest
- 🐳 **Docker containerization** for easy deployment
- 🌐 **Production deployment** on Fly.io
- 🔒 **CORS security** configured for frontend integration
- 📝 **Detailed logging** and health monitoring

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Environment Configuration](#environment-configuration)
- [Testing](#testing)
- [Deployment](#deployment)
- [Platform Specifications](#platform-specifications)
- [Development](#development)
- [Architecture](#architecture)

## 🏃 Quick Start

### 1. Clone and Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the backend directory:

```bash
# Required - DeepSeek AI Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=ad_copy_generator

# Optional - Development Settings
DEBUG=true
FRONTEND_URL=http://localhost:3000
```

### 3. Start Dependencies

```bash
# Start MongoDB (using Docker)
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or use MongoDB Atlas cloud (update MONGODB_URL in .env)
```

### 4. Get DeepSeek API Key

1. Visit [DeepSeek Platform](https://platform.deepseek.com)
2. Sign up and create an API key
3. Add it to your `.env` file

### 5. Run the Server

```bash
# Using the provided script
chmod +x start.sh
./start.sh

# Or manually
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

## 🛠 API Endpoints

### Health Check
```http
GET /health
```
Returns server health status, database connection, and AI service availability.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "ai_service": "ready"
}
```

### Generate Ad Copy
```http
POST /api/v1/ads/generate
```

Generate AI-powered ad variations for different platforms.

**Request Body:**
```json
{
  "name": "2019 Toyota Camry SE",
  "desc": "Clean CarFax, 62k miles, Apple CarPlay, 35 MPG, financing available",
  "audience": ["first-time buyers", "Oklahoma City"],
  "tone": "trustworthy",
  "platform": "meta",
  "variants": 3,
  "business_type": "auto_dealership"
}
```

**Request Fields:**
- `name` (string, required): Product/service name
- `desc` (string, required): Product description
- `audience` (array, optional): Target audience segments
- `tone` (enum, required): `trustworthy`, `exciting`, `professional`, `friendly`
- `platform` (enum, required): `google_search`, `google_display`, `meta`, `tiktok`
- `variants` (integer, 1-5): Number of variations to generate
- `business_type` (enum, optional): `auto_dealership`, `real_estate`, `e_commerce`, `saas`, `local_business`

**Response:**
```json
{
  "success": true,
  "variations": [
    {
      "id": "var_123",
      "platform": "meta", 
      "tone": "trustworthy",
      "primary": "🚗 2019 Toyota Camry SE - Clean CarFax & Only 62k Miles! Apple CarPlay, 35 MPG efficiency. Perfect for first-time buyers in OKC.",
      "headline": "Reliable Toyota Camry SE - Trusted Choice",
      "description": "Clean history, low miles, great MPG"
    }
  ],
  "generated_at": "2025-08-29T03:15:00Z",
  "request_id": "req_abc123",
  "ad_id": "ad_def456"
}
```

### Get Ad History
```http
GET /api/v1/ads/history?limit=50&skip=0
```

Retrieve previously generated ads with pagination.

**Query Parameters:**
- `limit` (integer, 1-100): Number of results (default: 50)
- `skip` (integer, ≥0): Number of results to skip (default: 0)

**Response:**
```json
{
  "ads": [
    {
      "_id": "ad_def456",
      "input_data": { ... },
      "generated_variations": [ ... ],
      "platform": "meta",
      "created_at": "2025-08-29T03:15:00Z",
      "is_favorite": false,
      "tags": []
    }
  ],
  "total": 1,
  "limit": 50,
  "skip": 0
}
```

### Get Specific Ad
```http
GET /api/v1/ads/{ad_id}
```

Retrieve a specific ad by ID.

### Toggle Favorite
```http
PUT /api/v1/ads/{ad_id}/favorite
```

Toggle the favorite status of an ad.

**Request Body:**
```json
{
  "is_favorite": true
}
```

### Delete Ad
```http
DELETE /api/v1/ads/{ad_id}
```

Delete a specific ad and all its variations.

### Get Platform Specifications
```http
GET /api/v1/ads/platforms
```

Get character limits and requirements for all supported platforms.

**Response:**
```json
{
  "google_search": {
    "name": "Google Search (RSA)",
    "character_limits": {
      "headlines": 30,
      "descriptions": 90
    },
    "requirements": {
      "headlines_count": 3,
      "descriptions_count": 2
    }
  },
  // ... other platforms
}
```

## ⚙️ Environment Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DEEPSEEK_API_KEY` | DeepSeek API key | `sk-xxx...` |
| `DEEPSEEK_BASE_URL` | DeepSeek API endpoint | `https://api.deepseek.com/v1` |
| `DEEPSEEK_MODEL` | AI model to use | `deepseek-chat` |
| `MONGODB_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `DATABASE_NAME` | Database name | `ad_copy_generator` |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:3000` |
| `DEBUG` | Enable debug logging | `true` |

## 🧪 Testing

We've implemented a comprehensive test suite covering all critical functionality.

### Running Tests

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
./run_tests.sh

# Or run manually
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

### Test Coverage

Our test suite includes:

- ✅ **Unit Tests**: All API endpoints, models, and services
- ✅ **Integration Tests**: Database operations and AI service integration
- ✅ **Validation Tests**: Request/response validation and error handling
- ✅ **Mock Tests**: External API calls and database operations
- ✅ **Edge Cases**: Network timeouts, malformed responses, rate limiting

**Test Files:**
- `tests/test_main.py` - Main app and health endpoints
- `tests/test_ads_api.py` - Ad generation and CRUD operations
- `tests/test_ai_service.py` - AI service and fallback mechanisms
- `tests/test_database.py` - Database connection and operations
- `tests/test_validation.py` - Request validation and edge cases

### Test Reports

After running tests, detailed reports are available:
- `TEST_REPORT.md` - Comprehensive test documentation
- `FIXES_APPLIED.md` - History of test fixes and improvements

## 🚀 Deployment

### Local Development

```bash
# Start all services
./start.sh

# Or manually
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Deployment

```bash
# Build image
docker build -t adcopy-backend .

# Run container
docker run -p 8000:8000 --env-file .env adcopy-backend
```

### Fly.io Production Deployment

We provide complete Fly.io deployment setup:

```bash
# Deploy backend
./deploy.sh

# Or manually
flyctl launch --name adcopy --region phx --no-deploy
flyctl secrets set \
  DEEPSEEK_API_KEY="your_key_here" \
  DEEPSEEK_BASE_URL="https://api.deepseek.com/v1" \
  DEEPSEEK_MODEL="deepseek-chat" \
  MONGODB_URL="mongodb://adcopy-mongo.fly.dev:27017" \
  FRONTEND_URL="https://adcopy-frontend.fly.dev"
flyctl deploy
```

**Deployment includes:**
- Automatic HTTPS with Fly.io certificates
- Health checks and auto-scaling
- MongoDB integration
- CORS configuration for frontend
- Environment secret management

## 📱 Platform Specifications

### Google Search (RSA)
- **Headlines**: 30 characters max (3 required)
- **Descriptions**: 90 characters max (2 required)
- **Best for**: Search intent targeting

### Google Display
- **Short headline**: 30 characters max
- **Long headline**: 90 characters max  
- **Descriptions**: 90 characters max (2 required)
- **Best for**: Visual campaigns

### Meta (Facebook/Instagram)
- **Primary text**: 125 characters (soft limit)
- **Headline**: 40 characters (soft limit)
- **Description**: 30 characters (soft limit)
- **Best for**: Social engagement

### TikTok
- **Caption**: 100 characters (soft limit)
- **Best for**: Short-form video content

## 💻 Development

### Project Structure

```
backend/
├── app/
│   ├── api/v1/
│   │   └── ads.py          # Ad generation endpoints
│   ├── core/
│   │   ├── config.py       # Configuration management
│   │   └── database.py     # Database connection
│   ├── models/
│   │   └── ad.py           # Pydantic models
│   └── services/
│       └── ai_service.py   # DeepSeek AI integration
├── tests/                  # Comprehensive test suite
├── main.py                 # FastAPI application
├── requirements.txt        # Production dependencies
├── requirements-test.txt   # Testing dependencies
├── Dockerfile             # Container configuration
├── fly.toml               # Fly.io deployment config
└── README.md              # This file
```

### API Documentation

Interactive API documentation is automatically generated:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

### Database Schema

Using MongoDB with PyMongo for direct database operations:

**Ad Document:**
```javascript
{
  "_id": ObjectId("..."),
  "input_data": {
    "name": "Product Name",
    "desc": "Description",
    "audience": ["audience1"],
    "tone": "trustworthy",
    "platform": "meta",
    "variants": 3,
    "business_type": "auto_dealership"
  },
  "generated_variations": [
    {
      "id": "var_123",
      "platform": "meta",
      "tone": "trustworthy", 
      "primary": "Ad text...",
      "headline": "Headline...",
      "description": "Description..."
    }
  ],
  "platform": "meta",
  "created_at": ISODate("2025-08-29T03:15:00Z"),
  "is_favorite": false,
  "tags": [],
  "request_id": "req_abc123"
}
```

## 🏗 Architecture

### Core Components

1. **FastAPI Application** (`main.py`)
   - CORS configuration for frontend integration
   - Lifespan events for database initialization
   - Route inclusion and middleware setup

2. **AI Service** (`app/services/ai_service.py`)
   - DeepSeek API integration
   - Intelligent prompt engineering
   - Robust fallback mechanism
   - Platform-specific optimization

3. **Database Layer** (`app/core/database.py`)
   - MongoDB connection management
   - Graceful connection handling
   - Error recovery and logging

4. **API Routes** (`app/api/v1/ads.py`)
   - RESTful endpoint design
   - Request validation with Pydantic
   - Comprehensive error handling
   - Async operation support

5. **Configuration** (`app/core/config.py`)
   - Environment-based settings
   - Type-safe configuration with Pydantic
   - Secure secret management

### Key Design Decisions

- **Direct PyMongo over ODM**: Simpler, more reliable database operations
- **Async/Await**: Non-blocking operations for better performance
- **Comprehensive Testing**: High confidence in production deployments
- **Fallback System**: Ensures service availability even when AI is down
- **Platform Optimization**: Tailored ad generation for each platform's requirements

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Interactive API docs at `/docs`
- **Health Check**: Monitor service status at `/health`
- **Logs**: Check application logs for debugging
- **Tests**: Run the test suite to verify functionality

## 🎯 Roadmap

- [ ] Additional AI providers (OpenAI, Claude)
- [ ] Advanced analytics and performance tracking
- [ ] A/B testing capabilities
- [ ] Bulk ad generation
- [ ] Custom template management
- [ ] Multi-language support

---

Built with ❤️ using FastAPI, MongoDB, and DeepSeek AI