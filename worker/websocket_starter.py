# worker/websocket_starter.py
from tasks.websocket_alert import connect_websocket_task
from db_session import get_active_accounts

def bootstrap_websockets_on_startup():
    try:
        accounts_data = get_active_accounts()
        if accounts_data:
            connect_websocket_task(accounts_data)
            print(f"✅ WebSockets started for {len(accounts_data)} accounts")
        else:
            print("⚠️ No active accounts found")
    except Exception as e:
        print(f"❌ Failed to bootstrap websockets: {e}")
