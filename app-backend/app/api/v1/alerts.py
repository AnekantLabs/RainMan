from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.pydantic_schemas import TradingViewAlert
from app.celery.celery_app import celery
from app.core.db_session import get_db
import json
from app.utils.fetch_api_credential import fetch_api_credentials
from app.models.db_models import AlertLog

alert_router = APIRouter(prefix="/alerts", tags=["Alerts"])

# route to receive alerts from TradingView
@alert_router.post("/receive-tradingview-alert")
async def receive_tradingview_alert(alert: TradingViewAlert, db: Session = Depends(get_db)):
    try:
        alert_data = alert.model_dump()
        alert_id = str(uuid4())

        # Insert raw alert immediately into the database
        alert_entry = AlertLog(
            id=alert_id,
            data=alert_data
        )
        db.add(alert_entry)
        db.commit()

        # Fetch API credentials after saving
        credentials = fetch_api_credentials(db, alert.account)
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