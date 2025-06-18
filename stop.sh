#!/bin/bash

echo "🛑 Stopping RainMan System..."

# Stop client (npm)
echo "🔻 Stopping Client..."
pkill -f "npm start"
echo "✅ Client stopped."

# Stop backend (uvicorn)
echo "🔻 Stopping Backend..."
pkill -f "uvicorn app.main:app"
echo "✅ Backend stopped."

# Stop Celery worker
echo "🔻 Stopping Celery Worker..."
pkill -f "celery -A celery_app worker"
echo "✅ Worker stopped."

echo "🎉 All components stopped successfully!"
