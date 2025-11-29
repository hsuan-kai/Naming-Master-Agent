#!/bin/bash
# deploy.sh - Deploys Namer Agent to Google Cloud Run

# 1. Set your Project ID
PROJECT_ID="your-project-id-here"
REGION="us-central1"
SERVICE_NAME="naming-master"

echo "🚀 Deploying $SERVICE_NAME to Project: $PROJECT_ID..."

# 2. Set the project
gcloud config set project $PROJECT_ID

# 3. Build and Deploy
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=$GOOGLE_API_KEY

echo "✅ Deployment Complete!"
