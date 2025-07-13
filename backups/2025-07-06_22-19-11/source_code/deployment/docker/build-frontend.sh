#!/bin/sh
# Docker-specific frontend build script
# This script builds the frontend without TypeScript checking for Docker deployment

echo "🐳 Building frontend for Docker deployment..."

# Skip TypeScript checking and build directly with Vite
echo "⚠️  Skipping TypeScript checking for Docker build"
npx vite build --mode production

echo "✅ Frontend build completed for Docker"
