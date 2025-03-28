from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.pydantic_schemas import TradingViewAlert
from app.redis.redis_queue import add_task_to_queue

alert_router = APIRouter(prefix="/alerts", tags=["Alerts"])

# route to receive alerts from TradingView
@alert_router.post("/receive-tradingview-alert")
async def receive_tradingview_alert(alert: TradingViewAlert):
    try:
        # Process the alert here
        # just print the alert to console
        print(alert)
        
        # just add the alert to the redis queue
        add_task_to_queue(alert.dict())
        return {"Alert received and added to queue": alert}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))