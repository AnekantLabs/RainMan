#!/bin/bash

echo "🚀 Restarting RainMan System..."

# Kill previous background processes (optional safety)
echo "🧹 Cleaning up previous processes..."
pkill -f "uvicorn app.main:app" || true
pkill -f "celery -A celery_app worker" || true

# ---------- BACKEND ----------
echo "🔄 Restarting FastAPI backend (Gunicorn via systemd)..."
sudo systemctl restart app
echo "✅ Backend restarted (served on port 8000 behind Nginx)"

# ---------- WORKER ----------
echo "🔄 Restarting Celery Worker..."
cd ~/rainman-git/RainMan/worker || { echo "❌ worker directory not found!"; exit 1; }
source workerenv/bin/activate
# Stop existing worker gracefully (if needed)
pkill -f "celery -A celery_app worker" || true
nohup celery -A celery_app worker --loglevel=info -Q alerts,websocket_queue > ../worker.log 2>&1 &
echo "✅ Worker restarted (check worker.log)"
cd -

# ---------- FRONTEND ----------
echo "⚙️ Frontend is served via Nginx. No restart needed if static files in /var/www/rainman-frontend are correct."

echo "🎉 All components restarted successfully!"
