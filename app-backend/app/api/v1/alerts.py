import asyncio
from uuid import uuid4
from fastapi import APIRouter, Body, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.celery.celery_app import celery
from app.core.db_session import get_db
import json
from app.utils.fetch_api_credential import fetch_api_credentials
from app.models.db_models import Account, AlertLog
# logs_api.py
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
import redis
import json

alert_router = APIRouter(prefix="/alerts", tags=["Alerts"])

# route to receive alerts from TradingView
@alert_router.post("/receive-tradingview-alert")
async def receive_tradingview_alert(alert: dict = Body(...) , db: Session = Depends(get_db)):
    try:
        alert_data = alert
        alert_id = str(uuid4())

        # Insert raw alert immediately into the database
        alert_entry = AlertLog(
            id=alert_id,
            data=alert_data
        )
        db.add(alert_entry)
        db.commit()

        # Fetch API credentials after saving
        account_name = alert_data.get("account")
        credentials = fetch_api_credentials(db, account_name)
        alert_data.update(credentials)

        # Queue for processing
        celery.send_task(
            name="tasks.process_alert",
            args=[json.dumps(alert_data)],
            queue="alerts"
        )

        return {
            "message": "Alert stored in DB and queued for processing.",
            "alert_id": alert_id
        }

    except Exception as e:
        print(f"Error processing alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@alert_router.get("/latest")
async def get_latest_alerts(db: Session = Depends(get_db)):
    alerts = db.query(AlertLog).order_by(AlertLog.created_at.desc()).limit(2).all()
    return [a.data for a in alerts]


@alert_router.post("/close-all-positions")
async def close_all_positions(db: Session = Depends(get_db)):
    """
    API to close all open positions across all active, non-deleted accounts.
    Dispatches one Celery task per account.
    """
    active_accounts = db.query(Account).filter(
        Account.is_activate == True,
        Account.is_deleted == False
    ).all()

    if not active_accounts:
        raise HTTPException(status_code=404, detail="No active accounts found.")

    results = []

    for account in active_accounts:
        try:
            alert_id = str(uuid4())
            alert_data = {
                "action": "CLOSE",
                "symbol": None,  # Or make dynamic if needed
                "account": account.account_name
            }

            # Attach API credentials
            if account.role == "main":
                alert_data.update({
                    "main_api_key": account.api_key,
                    "main_api_secret": account.api_secret,
                    "role": "main"
                })
            elif "sub" in account.role:
                main_account = db.query(Account).filter(
                    Account.role == "main",
                    Account.is_activate == True,
                    Account.is_deleted == False
                ).first()
                if not main_account:
                    raise ValueError(f"No active main account for subaccount {account.account_name}")
                alert_data.update({
                    "main_api_key": main_account.api_key,
                    "main_api_secret": main_account.api_secret,
                    "api_key": account.api_key,
                    "api_secret": account.api_secret,
                    "role": account.role
                })

            # Log to DB
            db_alert = AlertLog(id=alert_id, data=alert_data)
            db.add(db_alert)
            db.commit()

            # Send task to Celery
            celery.send_task(
                name="tasks.process_alert",
                args=[json.dumps(alert_data)],
                queue="alerts"
            )

            results.append({"account": account.account_name, "alert_id": alert_id, "status": "queued"})

        except Exception as e:
            results.append({"account": account.account_name, "error": str(e)})

    return {
        "message": f"Dispatched close alerts to {len(results)} accounts.",
        "results": results
    }


router = APIRouter()
r = redis.Redis(host="localhost", port=6379, db=0)

@alert_router.get("/logs/stream")
async def log_stream(request: Request):
    async def event_generator():
        last_seen_logs = set()

        while True:
            if await request.is_disconnected():
                break

            logs = r.lrange("worker_logs", 0, 50)
            new_logs = []

            for raw in reversed(logs):
                if isinstance(raw, bytes):
                    raw = raw.decode()
                if raw not in last_seen_logs:
                    try:
                        log = json.loads(raw)
                        new_logs.append(log)
                        last_seen_logs.add(raw)
                    except Exception as e:
                        print("Invalid log entry:", e)

            for log in new_logs:
                yield {
                    "event": "log",
                    "data": json.dumps(log)  # ONLY ONE 'data:' is added by SSE wrapper
                }

            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())
