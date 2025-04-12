from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.pydantic_schemas import TradingViewAlert
from app.celery.celery_app import celery
from app.api.dependencies.utils.fetch_api_credential import fetch_api_credentials
from app.core.db_session import get_db
import json

alert_router = APIRouter(prefix="/alerts", tags=["Alerts"])

# route to receive alerts from TradingView
@alert_router.post("/receive-tradingview-alert")
async def receive_tradingview_alert(alert: TradingViewAlert, db: Session = Depends(get_db)):
    try:
        
        # fetch the credentials from the database
        credentials = fetch_api_credentials(db, alert.account)
        # print(f"Ctredentials for account {alert.account}: {credentials}")
        
        alert = alert.dict()  # Update the alert with credentials
        alert.update(credentials)  # Add credentials to the alert
        
        # Update the alert with credentials
        # alert.model_copy(update=credentials)
        
        # Process the alert here
        # just print the alert to console
        # print(alert)
        alert = json.dumps(alert)
        # process_alert.delay(alert)  # Add the task to the Celery queue
        celery.send_task(name="tasks.process_alert", args=[alert], queue="alerts")  # Add the task to the Celery queue
        return {"Alert received and added to queue": alert}
    except Exception as e:
        print(f"Error processing alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))