#!/bin/bash

echo "🚀 Deploying DoxTract Frontend to Vercel..."

# Check if backend URL is provided
if [ -z "$1" ]; then
    # Try to read from saved file
    if [ -f "../backend-url.txt" ]; then
        BACKEND_URL=$(cat ../backend-url.txt)
        echo "📡 Using saved backend URL: $BACKEND_URL"
    else
        echo "❌ No backend URL provided!"
        echo "Usage: $0 <backend-url>"
        echo "   or: Deploy backend first to generate backend-url.txt"
        exit 1
    fi
else
    BACKEND_URL="$1"
fi

# Navigate to frontend directory
cd frontend

# Replace placeholder with actual backend URL
echo "🔧 Configuring backend URL..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|https://your-backend-url.run.app|$BACKEND_URL|g" index.html
else
    # Linux
    sed -i "s|https://your-backend-url.run.app|$BACKEND_URL|g" index.html
fi

echo "✅ Backend URL configured: $BACKEND_URL"

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
vercel --prod

echo ""
echo "✅ Frontend deployed successfully!"
echo "📋 Next steps:"
echo "1. Test your application"
echo "2. Update backend CORS if needed: python ../configure.py --frontend-url YOUR_VERCEL_URL"