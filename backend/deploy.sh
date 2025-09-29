#!/bin/bash

# AI Ad Copy Generator - Backend Deployment Script for Fly.io

set -e  # Exit on any error

echo "🚀 AI Ad Copy Generator - Backend Deployment"
echo "=============================================="

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ flyctl is not installed. Please install it first:"
    echo "   curl -L https://fly.io/install.sh | sh"
    exit 1
fi

# Check if user is logged in
if ! flyctl auth whoami &> /dev/null; then
    echo "❌ Not logged in to Fly.io. Please run:"
    echo "   flyctl auth login"
    exit 1
fi

# Set app name to "adcopy"
APP_NAME="adcopy"

echo "📱 App name: $APP_NAME"

# Check if fly.toml exists, if not create the app
if [ ! -f "fly.toml" ]; then
    echo "🏗️  Creating new Fly.io app..."
    #flyctl launch --name "$APP_NAME" --dockerfile Dockerfile --no-deploy
    flyctl launch --dockerfile Dockerfile --no-deploy
else
    echo "📝 Using existing fly.toml configuration"
fi

# Set environment variables
echo "🔧 Setting environment variables..."
flyctl secrets set \
    DEEPSEEK_API_KEY="sk-***************" \
    DEEPSEEK_BASE_URL="https://api.deepseek.com/v1" \
    DEEPSEEK_MODEL="deepseek-chat" \
    MONGODB_URL="mongodb://localhost:27017" 
    DATABASE_NAME="ad_copy_generator" 
    #DEBUG="false" \
    #MAX_REQUESTS_PER_MINUTE="120" \
    #MAX_ADS_PER_REQUEST="5" \
    #APP_NAME="AI Ad Copy Generator" \
    #API_V1_STR="/api/v1" \
    #-a "$APP_NAME" 


# Deploy the application
echo "🚀 Deploying application..."
#flyctl deploy -a "$APP_NAME"
flyctl deploy

# Get the app URL
APP_URL=$(flyctl info -a "$APP_NAME" | grep Hostname | awk '{print $2}')

echo ""
echo "✅ Deployment completed successfully!"
echo "🌐 Your backend is available at: https://$APP_URL"
echo ""
echo "🧪 Testing endpoints..."

# Test health endpoint
if curl -f "https://$APP_URL/health" > /dev/null 2>&1; then
    echo "✅ Health check: PASSED"
else
    echo "❌ Health check: FAILED"
fi

# Test docs endpoint
if curl -f "https://$APP_URL/docs" > /dev/null 2>&1; then
    echo "✅ API docs: AVAILABLE at https://$APP_URL/docs"
else
    echo "❌ API docs: NOT ACCESSIBLE"
fi

echo ""
echo "📋 Next steps:"
echo "1. Set up MongoDB database"
echo "2. Update MONGODB_URL secret: flyctl secrets set MONGODB_URL='[connection-string]' -a $APP_NAME"
echo "3. Deploy frontend with backend URL: https://$APP_URL"
echo ""
echo "📊 Useful commands:"
echo "   View logs: flyctl logs -a $APP_NAME"
echo "   SSH to app: flyctl ssh console -a $APP_NAME"
echo "   Restart app: flyctl restart -a $APP_NAME"
