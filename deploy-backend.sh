#!/bin/bash
# Deploy DoxTract Backend to Google Cloud Run

set -e

echo "🚀 Deploying DoxTract Backend to Cloud Run..."
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first."
    exit 1
fi
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ No project set. Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "📦 Building and deploying to project: $PROJECT_ID"
cd backend
echo "🔨 Building container image..."
gcloud builds submit --config cloudbuild.yaml

# Get the deployed service URL
echo "🌐 Getting service URL..."
SERVICE_URL=$(gcloud run services describe doxtract-backend \
    --region=us-central1 \
    --format='value(status.url)')

echo ""
echo "✅ Backend deployed successfully!"
echo "🌐 Backend URL: $SERVICE_URL"
echo ""
echo "📋 Next steps:"
echo "1. Copy the backend URL above"
echo "2. Update frontend configuration: python ../configure.py --backend-url $SERVICE_URL"
echo "3. Deploy frontend to Vercel: cd ../frontend && vercel --prod"
echo "$SERVICE_URL" > ../backend-url.txt
echo "💾 Backend URL saved to backend-url.txt"
