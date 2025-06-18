#!/bin/bash

echo "🚀 Starting RainMan System..."

# ---------- APP-CLIENT ----------
echo "📦 Starting Client..."
cd app-client || { echo "❌ app-client directory not found!"; exit 1; }
source rainman-env/bin/activate
npm start > ../client.log 2>&1 &
echo "✅ Client started on default port (check client.log)"
cd ..

# ---------- APP-BACKEND ----------
echo "📦 Starting Backend..."
cd app-backend || { echo "❌ app-backend directory not found!"; exit 1; }
source rainman-backend/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
echo "✅ Backend started at http://0.0.0.0:8000 (check backend.log)"
cd ..

# ---------- WORKER ----------
echo "📦 Starting Celery Worker..."
cd worker || { echo "❌ worker directory not found!"; exit 1; }
source workerenv/bin/activate
celery -A celery_app worker --loglevel=info > ../worker.log 2>&1 &
echo "✅ Worker started (check worker.log)"
cd ..

echo "🎉 All components started successfully!"
