# AI Ad Copy Generator

A full-stack application that generates high-converting ad copy for multiple platforms using AI. Built with FastAPI backend, React frontend, and MongoDB database, deployed on Fly.io.

## 🚀 Features

- **Multi-Platform Support**: Generate ads for Google Search, Google Display, Meta (Facebook/Instagram), and TikTok
- **AI-Powered Generation**: Uses DeepSeek API for intelligent ad copy generation with fallback templates
- **Platform-Specific Optimization**: Respects character limits and platform best practices
- **Ad Library**: Save, manage, and organize generated ads
- **Real-time Backend Integration**: Seamless connection between frontend and backend with graceful fallback
- **Responsive Design**: Modern UI built with React and Tailwind CSS
- **Production Ready**: Dockerized deployment on Fly.io with MongoDB persistence

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with Python 3.12
- **AI Service**: DeepSeek API integration with intelligent fallback
- **Database**: MongoDB with PyMongo
- **API Features**: RESTful endpoints, background tasks, health checks
- **Deployment**: Docker container on Fly.io

### Frontend (React)
- **Framework**: React 19 with modern hooks
- **Styling**: Tailwind CSS for responsive design
- **State Management**: Local state with localStorage persistence
- **API Integration**: Dynamic backend connection with fallback mode
- **Deployment**: Nginx-served static build on Fly.io

### Database (MongoDB)
- **Engine**: MongoDB 6.0
- **Storage**: Persistent volume on Fly.io
- **Collections**: Ads with metadata, variations, and timestamps

## 📁 Project Structure

```
adcopy/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/v1/         # API routes
│   │   ├── core/           # Configuration & database
│   │   ├── models/         # Pydantic models
│   │   └── services/        # AI service integration
│   ├── tests/              # Comprehensive test suite
│   ├── Dockerfile          # Backend container
│   ├── fly.toml           # Fly.io deployment config
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.js         # Main application component
│   │   └── config.js      # API configuration
│   ├── Dockerfile         # Frontend container
│   ├── nginx.conf         # Nginx configuration
│   └── package.json       # Node.js dependencies
├── mongo/                  # MongoDB setup
│   ├── Dockerfile         # MongoDB container
│   └── fly.toml          # Database deployment
└── test_integration.md    # Integration testing guide
```

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation and serialization
- **PyMongo** - MongoDB driver
- **httpx** - Async HTTP client for AI API calls
- **Uvicorn** - ASGI server
- **Gunicorn** - Production WSGI server

### Frontend
- **React 19** - Frontend framework
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Icon library
- **React Scripts** - Build tooling

### Infrastructure
- **Docker** - Containerization
- **Fly.io** - Cloud deployment platform
- **MongoDB** - NoSQL database
- **Nginx** - Web server for frontend

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- MongoDB (local or cloud)
- DeepSeek API key (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd adcopy
   ```

2. **Start the Backend**
   ```bash
   cd backend
   ./start.sh  # Creates venv, installs deps, starts server
   ```
   Backend will be available at `http://localhost:8000`

3. **Start the Frontend**
   ```bash
   cd frontend
   npm install
   npm start
   ```
   Frontend will be available at `http://localhost:3000`

4. **Configure Environment (Optional)**
   ```bash
   # Add your DeepSeek API key to backend/.env
   echo "DEEPSEEK_API_KEY=your_api_key_here" >> backend/.env
   ```

### Testing the Integration

1. **Backend Health Check**: Visit `http://localhost:8000/health`
2. **API Documentation**: Visit `http://localhost:8000/docs`
3. **Frontend**: Open `http://localhost:3000` and test ad generation

## 📊 API Endpoints

### Core Endpoints
- `POST /api/v1/ads/generate` - Generate ad variations
- `GET /api/v1/ads/history` - Fetch ad library
- `GET /api/v1/ads/{id}` - Get specific ad
- `DELETE /api/v1/ads/{id}` - Delete ad
- `PUT /api/v1/ads/{id}/favorite` - Toggle favorite status
- `GET /health` - Health check

### Request Format
```json
{
  "name": "2019 Toyota Camry SE",
  "desc": "Clean CarFax, 62k miles, Apple CarPlay, 35 MPG, $289/mo with approved credit",
  "audience": ["first-time buyers", "OKC"],
  "tone": "Trustworthy",
  "platform": "meta",
  "variants": 3
}
```

## 🎯 Platform Support

### Google Search (RSA)
- **Headlines**: 30 characters max (3 required)
- **Descriptions**: 90 characters max (2 required)
- **Focus**: Search intent optimization

### Google Display
- **Short Headline**: 30 characters
- **Long Headline**: 90 characters  
- **Descriptions**: 90 characters each (2 required)

### Meta (Facebook/Instagram)
- **Primary Text**: 125 characters (soft limit)
- **Headline**: 40 characters (soft limit)
- **Description**: 30 characters (soft limit)
- **Focus**: Visual-first platform optimization

### TikTok
- **Caption**: 100 characters (soft limit)
- **Focus**: Short, punchy, hook-driven content

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/ -v
```

### Integration Tests
Follow the comprehensive guide in `test_integration.md` for end-to-end testing.

### Test Coverage
- Unit tests for AI service
- API endpoint tests
- Database integration tests
- Validation tests
- Frontend-backend integration tests

## 🚀 Deployment

### Fly.io Deployment

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Deploy Backend**
   ```bash
   cd backend
   fly deploy
   ```

3. **Deploy Frontend**
   ```bash
   cd frontend
   fly deploy
   ```

4. **Deploy MongoDB**
   ```bash
   cd mongo
   fly deploy
   ```

### Environment Variables
- `DEEPSEEK_API_KEY` - Your DeepSeek API key
- `MONGODB_URL` - MongoDB connection string
- `FRONTEND_URL` - Frontend URL for CORS

## 🔧 Configuration

### Backend Configuration
```python
# app/core/config.py
class Settings(BaseSettings):
    APP_NAME: str = "AI Ad Copy Generator"
    DEBUG: bool = True
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "ad_copy_generator"
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"
```

### Frontend Configuration
```javascript
// src/config.js
export const API_CONFIG = {
  BASE_URL: getApiUrl(), // Auto-detects environment
  ENDPOINTS: {
    HEALTH: '/health',
    GENERATE: '/api/v1/ads/generate',
    HISTORY: '/api/v1/ads/history',
    DELETE: '/api/v1/ads',
    PLATFORMS: '/api/v1/ads/platforms'
  },
  TIMEOUT: 30000
};
```

## 🎨 UI/UX Features

- **Modern Design**: Clean, Apple HIG + Material 3 inspired interface
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Real-time Status**: Backend connection indicator
- **Toast Notifications**: User feedback for actions
- **Character Counters**: Platform-specific character limits
- **Compliance Mode**: Content policy checking
- **Preset Templates**: Quick setup for common use cases

## 🔒 Security Features

- **CORS Configuration**: Properly configured for production
- **Input Validation**: Pydantic models for request validation
- **Error Handling**: Graceful error handling and fallbacks
- **Non-root User**: Docker containers run as non-root
- **Health Checks**: Application health monitoring

## 📈 Performance Optimizations

- **Background Tasks**: Database saves don't block responses
- **Caching**: Frontend localStorage for offline capability
- **Lazy Loading**: Components loaded on demand
- **Optimized Builds**: Production-optimized Docker images
- **Connection Pooling**: Efficient database connections

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check `test_integration.md` for detailed setup
- **Issues**: Open an issue on GitHub
- **API Docs**: Visit `/docs` endpoint when backend is running

## 🔮 Future Enhancements

- [ ] User authentication and accounts
- [ ] Payment integration (Stripe)
- [ ] Advanced analytics and reporting
- [ ] Team collaboration features
- [ ] More AI providers (OpenAI, Anthropic)
- [ ] A/B testing capabilities
- [ ] Export to ad platforms
- [ ] Mobile app (React Native)

---

**Built with ❤️ using FastAPI, React, and MongoDB**