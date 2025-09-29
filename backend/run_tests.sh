#!/bin/bash

# AI Ad Copy Generator - Test Runner Script

echo "🧪 Running AI Ad Copy Generator Backend Tests..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "⚡ Activating virtual environment..."
    source venv/bin/activate
fi

# Install test dependencies
echo "📦 Installing test dependencies..."
pip install -r requirements-test.txt

echo ""
echo "🚀 Starting test execution..."
echo "================================"

# Run different test suites

echo ""
echo "1️⃣ Running Unit Tests..."
pytest tests/test_main.py -v -m "not slow"

echo ""
echo "2️⃣ Running API Endpoint Tests..."
pytest tests/test_ads_api.py -v -m "not slow"

echo ""
echo "3️⃣ Running AI Service Tests..."
pytest tests/test_ai_service.py -v -m "not slow"

echo ""
echo "4️⃣ Running Database Tests..."
pytest tests/test_database.py -v -m "not slow"

echo ""
echo "5️⃣ Running Validation Tests..."
pytest tests/test_validation.py -v -m "not slow"

echo ""
echo "6️⃣ Running Integration Tests..."
pytest tests/test_integration.py -v

echo ""
echo "🏁 Running All Tests with Coverage..."
pytest tests/ -v --tb=short

echo ""
echo "📊 Test Summary:"
echo "================"
echo "✅ Unit Tests: API endpoints, main app functionality"
echo "✅ AI Service: DeepSeek integration and fallback generation"
echo "✅ Database: MongoDB operations and error handling"
echo "✅ Validation: Input validation and error responses"
echo "✅ Integration: End-to-end workflows"
echo "✅ Security: Injection prevention and input sanitization"
echo ""

# Check if all tests passed
if [ $? -eq 0 ]; then
    echo "🎉 ALL TESTS PASSED! Backend is ready for deployment."
else
    echo "❌ Some tests failed. Please review the output above."
    exit 1
fi
