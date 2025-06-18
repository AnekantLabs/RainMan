"""
WebSocket connection manager for Bybit trading accounts.
Handles real-time order and wallet updates with automatic fund transfers.
"""

import json
import logging
from datetime import datetime
import threading
from time import sleep
from typing import Dict, Any, Optional, List
from decimal import Decimal, InvalidOperation

from celery import Celery
from pybit.unified_trading import WebSocket
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

from celery_app import celery_app
from bybit_client import BybitClient
from tasks.constants import MAIN_ACCOUNT
from models import SessionLocal
from db_session import get_active_accounts
from logging_event import get_logger

logger = get_logger()
# logger = logging.getLogger(__name__)

# --- Insert trade to DB ---
def insert_trade_raw(trade_data):
    session = SessionLocal()
    try:
        sql = text("""
        INSERT INTO trades (
            order_id, account_name, symbol, side, order_type, price, qty, status,
            avg_price, cum_exec_qty, cum_exec_value, cum_exec_fee, closed_pnl,
            category, created_time, updated_time, raw_event
        )
        VALUES (
            :order_id, :account_name, :symbol, :side, :order_type, :price, :qty, :status,
            :avg_price, :cum_exec_qty, :cum_exec_value, :cum_exec_fee, :closed_pnl,
            :category, :created_time, :updated_time, :raw_event
        )
        ON CONFLICT (order_id) DO UPDATE SET
            account_name = EXCLUDED.account_name,
            symbol = EXCLUDED.symbol,
            side = EXCLUDED.side,
            order_type = EXCLUDED.order_type,
            price = EXCLUDED.price,
            qty = EXCLUDED.qty,
            status = EXCLUDED.status,
            avg_price = EXCLUDED.avg_price,
            cum_exec_qty = EXCLUDED.cum_exec_qty,
            cum_exec_value = EXCLUDED.cum_exec_value,
            cum_exec_fee = EXCLUDED.cum_exec_fee,
            closed_pnl = EXCLUDED.closed_pnl,
            category = EXCLUDED.category,
            created_time = EXCLUDED.created_time,
            updated_time = EXCLUDED.updated_time,
            raw_event = EXCLUDED.raw_event;
        """)
        if "raw_event" in trade_data and not isinstance(trade_data["raw_event"], str):
            trade_data["raw_event"] = json.dumps(trade_data["raw_event"])
        session.execute(sql, trade_data)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database error saving trade (raw): {e}", exc_info=True)
    finally:
        session.close()


# --- WebSocket Manager ---
class WebSocketConnectionManager:
    def __init__(self):
        self._active_connections: Dict[str, Dict[str, Any]] = {}
        self._transfer_threshold = Decimal('5.00')
        self._safety_buffer = Decimal('0.95')

    @property
    def active_connections(self):
        return self._active_connections

    def is_connected(self, subaccount_name: str) -> bool:
        return self._active_connections.get(subaccount_name, {}).get("connected", False)

    def get_credentials(self, subaccount_name: str) -> Optional[Dict[str, str]]:
        conn = self._active_connections.get(subaccount_name)
        if not conn:
            return None
        return {
            "api_key": conn.get("api_key"),
            "api_secret": conn.get("api_secret")
        }


# --- Transfer Manager ---
class TransferManager:
    def __init__(self, connection_manager: WebSocketConnectionManager):
        self.connection_manager = connection_manager

    def perform_internal_transfer(self, from_subaccount: str, to_subaccount: str, amount: Decimal, coin="USDT") -> str:
        try:
            if amount <= 0:
                return "INVALID_AMOUNT"
            from_creds = self.connection_manager.get_credentials(from_subaccount)
            to_creds = self.connection_manager.get_credentials(to_subaccount)
            if not from_creds or not to_creds:
                return "MISSING_CREDENTIALS"
            from_client = BybitClient(from_creds["api_key"], from_creds["api_secret"])
            to_client = BybitClient(to_creds["api_key"], to_creds["api_secret"])
            from_uid = from_client.get_acc_uid()
            to_uid = to_client.get_acc_uid()
            return from_client.transfer_funds(from_uid, to_uid, float(amount), coin)
        except Exception as e:
            logger.error(f"Transfer error: {e}", exc_info=True)
            return "TRANSFER_FAILED"


# --- Message Handler ---
class MessageHandler:
    def __init__(self, connection_manager: WebSocketConnectionManager, transfer_manager: TransferManager):
        self.connection_manager = connection_manager
        self.transfer_manager = transfer_manager

    def _safe_decimal(self, value, default=Decimal("0")):
        try:
            return Decimal(str(value)) if value not in [None, '', 'null'] else default
        except Exception:
            return default

    def _safe_float(self, value):
        try:
            return float(value)
        except:
            return None

    def _convert_time(self, t):
        try:
            return datetime.fromtimestamp(int(t) / 1000)
        except:
            return None

    def handle_wallet_message(self, msg: Dict[str, Any], subaccount_name: str):
        try:
            if subaccount_name == MAIN_ACCOUNT or "data" not in msg:
                return
            data = msg["data"][0]
            avail = self._safe_decimal(data.get("totalAvailableBalance"))
            upl = self._safe_decimal(data.get("totalPerpUPL"))
            creds = self.connection_manager.get_credentials(subaccount_name)
            if not creds:
                return
            client = BybitClient(**creds)
            transfer_bal = self._safe_decimal(client.get_transferable_amount(["USDT"]).get("USDT", 0))
            amt = transfer_bal * self.connection_manager._safety_buffer if upl != 0 else transfer_bal
            if amt > self.connection_manager._transfer_threshold:
                self.transfer_manager.perform_internal_transfer(subaccount_name, MAIN_ACCOUNT, amt)
        except Exception as e:
            logger.error(f"Wallet msg error for {subaccount_name}: {e}", exc_info=True)

    def handle_private_orders_message(self, order: Dict[str, Any], account_name: str):
        try:
            oid = order.get("orderId")
            if not oid:
                return
            data = {
                "order_id": oid,
                "account_name": account_name,
                "symbol": order.get("symbol"),
                "side": order.get("side"),
                "order_type": order.get("orderType"),
                "price": self._safe_float(order.get("price")),
                "qty": self._safe_float(order.get("qty")),
                "status": order.get("orderStatus"),
                "avg_price": self._safe_float(order.get("avgPrice")),
                "cum_exec_qty": self._safe_float(order.get("cumExecQty")),
                "cum_exec_value": self._safe_float(order.get("cumExecValue")),
                "cum_exec_fee": self._safe_float(order.get("cumExecFee")),
                "closed_pnl": self._safe_float(order.get("closedPnl")),
                "category": order.get("category"),
                "created_time": self._convert_time(order.get("createdTime")),
                "updated_time": self._convert_time(order.get("updatedTime")),
                "raw_event": order,
            }
            insert_trade_raw(data)
        except Exception as e:
            logger.error(f"Trade insert error: {e}", exc_info=True)


# --- Managers ---
connection_manager = WebSocketConnectionManager()
transfer_manager = TransferManager(connection_manager)
message_handler = MessageHandler(connection_manager, transfer_manager)


# --- Connection Establishment ---
def _establish_connection(subaccount_name: str, credentials: Dict[str, str]) -> bool:
    api_key, api_secret = credentials.get("api_key"), credentials.get("api_secret")
    if not api_key or not api_secret:
        return False
    if connection_manager.is_connected(subaccount_name):
        return True
    try:
        ws = WebSocket(testnet=True, channel_type="private", api_key=api_key, api_secret=api_secret)

        def wallet_cb(msg):
            if msg.get("op") != "pong":
                message_handler.handle_wallet_message(msg, subaccount_name)

        def order_cb(msg):
            if msg.get("op") != "pong":
                for order in msg.get("data", []):
                    message_handler.handle_private_orders_message(order, subaccount_name)

        ws.wallet_stream(callback=wallet_cb)
        ws.order_stream(callback=order_cb)

        connection_manager.active_connections[subaccount_name] = {
            "ws": ws,
            "connected": True,
            "api_key": api_key,
            "api_secret": api_secret
        }

        def send_ping():
            while True:
                try:
                    if not connection_manager.is_connected(subaccount_name):
                        break
                    if ws.ws and ws.ws.sock and ws.ws.sock.connected:
                        ws.ws.send(json.dumps({"req_id": "ping_heartbeat", "op": "ping"}))
                        logger.info(f"Sent ping to {subaccount_name}")
                    sleep(20)
                except Exception as e:
                    logger.error(f"Ping failed for {subaccount_name}: {e}", exc_info=True)
                    break

        threading.Thread(target=send_ping, daemon=True).start()
        return True
    except Exception as e:
        logger.error(f"WebSocket error for {subaccount_name}: {e}", exc_info=True)
        return False


def _maintain_connections():
    logger.info("Maintaining WebSocket connections")
    while True:
        sleep(30)


# --- Celery Tasks ---
@celery_app.task(name="tasks.connect_websocket")
def connect_websocket_task(accounts_data: Dict[str, Dict[str, str]]):
    for name, creds in accounts_data.items():
        _establish_connection(name, creds)
    _maintain_connections()


@celery_app.task(name="tasks.connect_websocket_startup")
def connect_websocket_startup():
    try:
        accounts_data = get_active_accounts()
        if accounts_data:
            connect_websocket_task(accounts_data)
        else:
            logger.warning("No active accounts found")
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)
