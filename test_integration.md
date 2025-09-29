# 🚀 Frontend-Backend Integration Test Guide

## Quick Test Steps

### 1. Start the Backend
```bash
cd backend
./start.sh
```
This will:
- Create virtual environment
- Install dependencies
- Copy `.env.example` to `.env`
- Start FastAPI server on http://localhost:8000

### 2. Configure Environment (Optional)
If you have a DeepSeek API key, edit `backend/.env`:
```bash
DEEPSEEK_API_KEY=your_actual_api_key_here
```

Without an API key, the system will use fallback templates (still works!).

### 3. Test Backend Directly
Open: http://localhost:8000/docs
- Try the `/health` endpoint
- Test `/api/v1/ads/generate` with sample data

### 4. Open Frontend
Open your `ai_ad_copy_generator.jsx` in a React app or browser.

You should see:
- ✅ Green "API Connected" indicator in header
- Backend integration working in generate function
- Ad history in Library tab fetched from API

### 5. Test the Integration

**Generate Ads:**
1. Fill in the form (try the "Quick preset (Dealers)" button)
2. Click "Generate" 
3. Should see AI-generated ads (or fallback templates)
4. Ads automatically saved to backend database

**Check Library:**
1. Go to "Library" tab
2. Should see generated ads from backend
3. Can copy/delete ads
4. Mix of local storage + API data

**Test Fallback:**
1. Stop the backend server
2. Frontend should show "API Offline" 
3. Generate still works with fallback templates
4. Graceful degradation

## Expected Behavior

### With Backend Running:
- 🟢 "API Connected" status
- Real AI generation (if API key set) or smart templates
- Ads saved to MongoDB
- Library shows API + local data
- Full delete/copy functionality

### With Backend Offline:
- 🔴 "API Offline" status  
- Fallback to local template generation
- Local storage only
- Toast: "Backend offline - using fallback mode"

## Sample Test Data

**Car Dealership (Primary Market):**
```
Name: 2019 Toyota Camry SE
Description: Clean CarFax, 62k miles, Apple CarPlay, 35 MPG, $289/mo with approved credit. 90-day warranty included.
Audience: first-time buyers, OKC
Tone: Trustworthy
Platform: Meta
```

**E-commerce:**
```
Name: Wireless Headphones Pro
Description: Noise-canceling, 30-hour battery, premium sound quality. Free shipping and returns.
Audience: music lovers, commuters
Tone: Casual
Platform: Google Search
```

## Troubleshooting

**Backend Won't Start:**
- Check Python installation: `python3 --version`
- Install requirements manually: `pip install -r requirements.txt`
- Check port 8000 isn't in use: `lsof -i :8000`

**API Connection Failed:**
- Verify backend running: http://localhost:8000/health
- Check CORS settings in `main.py`
- Browser console for network errors

**No AI Generation:**
- Add DEEPSEEK_API_KEY to `.env`
- Check API quota/billing
- Fallback templates should still work

## API Endpoints Being Used

- `POST /api/v1/ads/generate` - Generate ad variations
- `GET /api/v1/ads/history` - Fetch ad library  
- `DELETE /api/v1/ads/{id}` - Delete ad
- `GET /health` - Check backend status

## Next Steps After Testing

1. **Deploy Backend**: Railway, Render, or fly.io
2. **Update Frontend URLs**: Change localhost to production URL
3. **Add Authentication**: Implement user accounts
4. **Payment Integration**: Stripe for subscription plans
5. **Production Database**: MongoDB Atlas

The integration is complete and ready for production deployment!
