from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.pydantic_schemas import TradingViewAlert
from app.celery.celery_app import celery

alert_router = APIRouter(prefix="/alerts", tags=["Alerts"])

# route to receive alerts from TradingView
@alert_router.post("/receive-tradingview-alert")
async def receive_tradingview_alert(alert: TradingViewAlert):
    try:
        # Process the alert here
        # just print the alert to console
        print(alert)
        alert = alert.model_dump_json()
        # process_alert.delay(alert)  # Add the task to the Celery queue
        celery.send_task(name="tasks.process_alert", args=[alert], queue="alerts")  # Add the task to the Celery queue
        return {"Alert received and added to queue": alert}
    except Exception as e:
        print(f"Error processing alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))