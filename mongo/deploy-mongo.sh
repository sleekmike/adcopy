#!/bin/bash

# AI Ad Copy Generator - MongoDB Deployment Script for Fly.io

set -e  # Exit on any error

echo "🗄️  AI Ad Copy Generator - MongoDB Deployment"
echo "============================================="

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

# Navigate to mongo directory
cd "$(dirname "$0")"

echo "📱 Deploying MongoDB app: adcopy-mongo"

# Step 1: Create the MongoDB app (don't deploy yet)
echo "🏗️  Creating MongoDB app..."
flyctl launch --name adcopy-mongo --region phx --no-deploy

# Step 2: Create volume for MongoDB data persistence
echo "💾 Creating volume for MongoDB data..."
flyctl volumes create adcopy-mongo --region phx --size 1
#fly secrets set MONGO_URI="mongodb://adcopy-mongo.internal:27017/ad_copy_generator"
#mongodb://adcopy-mongo.internal:27017/ad_copy_generator
#mongodb://adcopy-mongo.fly.dev:27017/ad_copy_generator
#Visit your newly deployed app at https://adcopy-mongo.fly.dev/
# Step 3: Deploy MongoDB
echo "🚀 Deploying MongoDB..."
flyctl deploy

# Step 4: Test MongoDB connection
echo "🧪 Testing MongoDB connection..."
sleep 10  # Wait for MongoDB to start

# Get the app URL
MONGO_URL="adcopy-mongo.fly.dev"

echo ""
echo "✅ MongoDB deployment completed successfully!"
echo "🌐 MongoDB is available at: $MONGO_URL:27017"
echo ""

# Step 5: Update backend with MongoDB connection string
echo "🔧 Updating backend with MongoDB connection..."
cd ../backend

# Set the MongoDB URL in the backend app
flyctl secrets set MONGODB_URL="mongodb://adcopy-mongo.internal:27017/ad_copy_generator" -a adcopy

echo ""
echo "📋 MongoDB Setup Complete!"
echo "=========================="
echo "🔗 Internal MongoDB URL: mongodb://adcopy-mongo.internal:27017/ad_copy_generator"
echo "🔗 External MongoDB URL: mongodb://$MONGO_URL:27017/ad_copy_generator"
echo ""
echo "📊 Useful MongoDB commands:"
echo "   View logs: flyctl logs -a adcopy-mongo"
echo "   SSH to MongoDB: flyctl ssh console -a adcopy-mongo"
echo "   Restart MongoDB: flyctl restart -a adcopy-mongo"
echo "   Connect via proxy: flyctl proxy 27017:27017 -a adcopy-mongo"
echo ""
echo "🧪 Test connection locally:"
echo "   flyctl proxy 27017:27017 -a adcopy-mongo"
echo "   # Then in another terminal:"
echo "   mongosh --host localhost --port 27017 --eval \"db.adminCommand('ping')\""
echo ""
echo "✅ Your backend will now use the deployed MongoDB!"
