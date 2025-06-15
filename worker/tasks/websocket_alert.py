"""
WebSocket connection manager for Bybit trading accounts.
Handles real-time order and wallet updates with automatic fund transfers.
"""

import json
import logging
from datetime import datetime
from time import sleep
from typing import Dict, Any, Optional, List
from decimal import Decimal, InvalidOperation

from celery import Celery
from pybit.unified_trading import WebSocket
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text  # Add this import

from celery_app import celery_app
from bybit_client import BybitClient
from tasks.constants import MAIN_ACCOUNT
from models import SessionLocal
# from models import Base, engine

# Base.metadata.create_all(bind=engine)

# Configure logging
logger = logging.getLogger(__name__)


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
            raw_event = EXCLUDED.raw_event
        ;
        """)  # <-- wrap with text()
        # Ensure raw_event is JSON-serializable
        trade_data = dict(trade_data)
        if "raw_event" in trade_data and not isinstance(trade_data["raw_event"], str):
            import json
            trade_data["raw_event"] = json.dumps(trade_data["raw_event"])
        session.execute(sql, trade_data)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database error saving trade (raw): {e}", exc_info=True)
    finally:
        session.close()

class WebSocketConnectionManager:
    """Manages WebSocket connections for multiple trading accounts."""
    
    def __init__(self):
        self._active_connections: Dict[str, Dict[str, Any]] = {}
        self._transfer_threshold = Decimal('5.00')  # Minimum amount for transfers
        self._safety_buffer = Decimal('0.95')  # 5% safety margin for transfers
    
    @property
    def active_connections(self) -> Dict[str, Dict[str, Any]]:
        """Get active connections dictionary."""
        return self._active_connections
    
    def is_connected(self, subaccount_name: str) -> bool:
        """Check if a subaccount has an active WebSocket connection."""
        connection = self._active_connections.get(subaccount_name, {})
        return connection.get("connected", False)
    
    def get_credentials(self, subaccount_name: str) -> Optional[Dict[str, str]]:
        """Get API credentials for a subaccount."""
        connection = self._active_connections.get(subaccount_name)
        if not connection:
            return None
        
        return {
            "api_key": connection.get("api_key"),
            "api_secret": connection.get("api_secret")
        }


class TransferManager:
    """Handles fund transfers between subaccounts."""
    
    def __init__(self, connection_manager: WebSocketConnectionManager):
        self.connection_manager = connection_manager
    
    def perform_internal_transfer(
        self, 
        from_subaccount: str, 
        to_subaccount: str, 
        amount: Decimal, 
        coin: str = "USDT"
    ) -> str:
        """
        Performs an internal transfer between subaccounts.
        
        Args:
            from_subaccount: Source subaccount name
            to_subaccount: Destination subaccount name
            amount: Amount to transfer
            coin: Cryptocurrency symbol
            
        Returns:
            Transfer status string
        """
        try:
            # Validate amount
            if amount <= 0:
                logger.warning(f"Invalid transfer amount: {amount}. Transfer aborted.")
                return "INVALID_AMOUNT"
            
            # Get credentials
            from_creds = self.connection_manager.get_credentials(from_subaccount)
            to_creds = self.connection_manager.get_credentials(to_subaccount)
            
            if not from_creds or not to_creds:
                logger.error(f"Missing credentials for subaccounts: {from_subaccount} or {to_subaccount}")
                return "MISSING_CREDENTIALS"
            
            if not all([from_creds.get("api_key"), from_creds.get("api_secret"),
                       to_creds.get("api_key"), to_creds.get("api_secret")]):
                logger.error("Incomplete credentials found")
                return "INCOMPLETE_CREDENTIALS"
            
            # Initialize clients
            from_client = BybitClient(
                api_key=from_creds["api_key"], 
                api_secret=from_creds["api_secret"]
            )
            to_client = BybitClient(
                api_key=to_creds["api_key"], 
                api_secret=to_creds["api_secret"]
            )
            
            # Get UIDs
            from_uid = from_client.get_acc_uid()
            to_uid = to_client.get_acc_uid()
            
            if not from_uid or not to_uid:
                logger.error(f"Failed to fetch UIDs for subaccounts: {from_subaccount} or {to_subaccount}")
                return "UID_FETCH_FAILED"
            
            # Perform transfer
            logger.info(
                f"Initiating transfer of {amount} {coin} from {from_subaccount} "
                f"(UID: {from_uid}) to {to_subaccount} (UID: {to_uid})"
            )
            
            transfer_status = from_client.transfer_funds(
                from_uid=from_uid, 
                to_uid=to_uid, 
                amount=float(amount), 
                coin=coin
            )
            
            if transfer_status == "SUCCESS":
                logger.info(
                    f"✅ Transfer of {amount} {coin} from {from_subaccount} "
                    f"to {to_subaccount} completed successfully"
                )
            else:
                logger.error(f"❌ Transfer failed with status: {transfer_status}")
            
            return transfer_status
            
        except Exception as e:
            logger.error(f"❌ Error during internal transfer: {e}", exc_info=True)
            return "TRANSFER_FAILED"


class MessageHandler:
    """Handles WebSocket message processing."""
    
    def __init__(self, connection_manager: WebSocketConnectionManager, transfer_manager: TransferManager):
        self.connection_manager = connection_manager
        self.transfer_manager = transfer_manager
    
    def _safe_decimal_conversion(self, value: Any, default: Decimal = Decimal('0')) -> Decimal:
        """Safely convert a value to Decimal."""
        if value in (None, '', 'null'):
            logger.warning(f"Empty or invalid Decimal input: '{value}', using default {default}")
            return default
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            logger.warning(f"Could not convert '{value}' to Decimal, using default {default}")
            return default

    def _safe_float_conversion(self, value: Any) -> Optional[float]:
        """Safely convert a value to float."""
        if value in (None, '', 'null'):
            logger.warning(f"Empty or invalid float input: '{value}'")
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            logger.warning(f"Could not convert '{value}' to float")
            return None


    
    def handle_wallet_message(self, message: Dict[str, Any], subaccount_name: str) -> None:
        """
        Process wallet update messages and handle fund transfers.
        
        Args:
            message: WebSocket message containing wallet data
            subaccount_name: Name of the subaccount
        """
        try:
            logger.info(f"Wallet message received for {subaccount_name}")
            
            # Skip main account processing
            if subaccount_name == MAIN_ACCOUNT:
                logger.debug("Skipping wallet message processing for main account")
                return
            
            # Validate message structure
            if not self._validate_wallet_message(message):
                logger.warning(f"Invalid wallet message structure for {subaccount_name}")
                return
            
            wallet_data = message["data"][0]
            
            # Extract wallet information
            total_available_balance = self._safe_decimal_conversion(
                wallet_data.get("totalAvailableBalance")
            )
            total_initial_margin = self._safe_decimal_conversion(
                wallet_data.get("totalInitialMargin")
            )
            total_perp_upl = self._safe_decimal_conversion(
                wallet_data.get("totalPerpUPL")
            )
            
            logger.info(
                f"Subaccount {subaccount_name}: Available Balance={total_available_balance}, "
                f"Initial Margin={total_initial_margin}, Unrealized PnL={total_perp_upl}"
            )
            
            # Get transferable amount
            transferable_balance = self._get_transferable_balance(subaccount_name)
            if transferable_balance is None:
                return
            
            # Calculate transfer amount
            amount_to_transfer = self._calculate_transfer_amount(
                transferable_balance, total_perp_upl
            )
            
            # Execute transfer if amount exceeds threshold
            if amount_to_transfer > self.transfer_manager.connection_manager._transfer_threshold:
                self._execute_transfer_to_main(subaccount_name, amount_to_transfer)
            else:
                logger.info(
                    f"No eligible balance transfer needed for {subaccount_name}. "
                    f"Transferable balance: {amount_to_transfer} USDT"
                )
                
        except Exception as e:
            logger.error(f"❌ Error processing wallet message for {subaccount_name}: {e}", exc_info=True)
    
    def _validate_wallet_message(self, message: Dict[str, Any]) -> bool:
        """Validate wallet message structure."""
        return (
            message and 
            "data" in message and 
            isinstance(message["data"], list) and 
            len(message["data"]) > 0
        )
    
    def _get_transferable_balance(self, subaccount_name: str) -> Optional[Decimal]:
        """Get transferable balance for a subaccount."""
        try:
            credentials = self.connection_manager.get_credentials(subaccount_name)
            if not credentials:
                logger.error(f"No credentials found for {subaccount_name}")
                return None
            
            bybit_client = BybitClient(
                api_key=credentials["api_key"],
                api_secret=credentials["api_secret"]
            )
            
            transferable_amounts = bybit_client.get_transferable_amount(["USDT"])
            transferable_balance = self._safe_decimal_conversion(
                transferable_amounts.get("USDT", 0)
            )
            
            logger.info(f"Transferable balance for {subaccount_name}: {transferable_balance} USDT")
            return transferable_balance
            
        except Exception as e:
            logger.error(f"Error getting transferable balance for {subaccount_name}: {e}")
            return None
    
    def _calculate_transfer_amount(
        self, 
        transferable_balance: Decimal, 
        total_perp_upl: Decimal
    ) -> Decimal:
        """Calculate the amount to transfer based on unrealized PnL."""
        if total_perp_upl == 0:
            logger.info("TotalPerpUPL is 0. Transferring full transferable balance.")
            return transferable_balance
        else:
            logger.info("TotalPerpUPL is not 0. Applying safety buffer to transferable balance.")
            return max(Decimal('0'), transferable_balance * self.transfer_manager.connection_manager._safety_buffer)
    
    def _execute_transfer_to_main(self, subaccount_name: str, amount: Decimal) -> None:
        """Execute transfer to main account."""
        logger.info(
            f"🎯 Transferable balance detected in {subaccount_name}: {amount} USDT. "
            f"Initiating transfer to main account"
        )
        
        transfer_status = self.transfer_manager.perform_internal_transfer(
            from_subaccount=subaccount_name,
            to_subaccount=MAIN_ACCOUNT,
            amount=amount
        )
        
        if transfer_status == "SUCCESS":
            logger.info(f"✅ Successfully transferred {amount} USDT from {subaccount_name} to main account")
        else:
            logger.error(
                f"❌ Failed to transfer {amount} USDT from {subaccount_name} to main account. "
                f"Status: {transfer_status}"
            )
    


    def handle_private_orders_message(self, order_data: Dict[str, Any], account_name: str) -> None:
        """
        Process private order messages and update database.
        """
        logger.info(f"Processing private order message for orderId: {order_data}")
        try:
            order_id = order_data.get("orderId")
            if not order_id:
                logger.warning("Received order message without orderId")
                return

            trade_data = self._prepare_trade_data(order_data, account_name)
            trade_data["order_id"] = order_id  # Ensure order_id is present

            insert_trade_raw(trade_data)
            logger.info(f"Inserted/updated trade for order {order_id}")

        except Exception as e:
            logger.error(f"Error saving trade: {e}", exc_info=True)

    # def handle_private_orders_message(self, order_data: Dict[str, Any],account_name: str) -> None:
    #     """
    #     Process private order messages and update database.
        
    #     Args:
    #         order_data: Order data from WebSocket message
    #     """
    #     logger.info(f"Processing private order message for orderId: {order_data}")
    #     session = SessionLocal()
    #     try:
    #         order_id = order_data.get("orderId")
    #         if not order_id:
    #             logger.warning("Received order message without orderId")
    #             return
            
    #         # Get existing trade or create new one
    #         trade = session.query(Trade).filter_by(order_id=order_id).first()
            
    #         # Prepare trade data
    #         trade_data = self._prepare_trade_data(order_data,account_name)
            
    #         if trade:
    #             # Update existing trade
    #             for key, value in trade_data.items():
    #                 setattr(trade, key, value)
    #             logger.info(f"Updated existing trade for order {order_id}")
    #         else:
    #             # Create new trade
    #             trade = Trade(order_id=order_id, **trade_data)
    #             session.add(trade)
    #             logger.info(f"Created new trade for order {order_id}")
            
    #         session.commit()
            
    #     except SQLAlchemyError as e:
    #         logger.error(f"Database error saving trade: {e}")
    #         session.rollback()
    #     except Exception as e:
    #         logger.error(f"Error saving trade: {e}", exc_info=True)
    #         session.rollback()
    #     finally:
    #         session.close()
    
    def _prepare_trade_data(self, order_data: Dict[str, Any], account_name: str) -> Dict[str, Any]:
        """Prepare trade data for database insertion/update."""
        return {
            "account_name": account_name,  # Add this line
            "symbol": order_data.get("symbol"),
            "side": order_data.get("side"),
            "order_type": order_data.get("orderType"),
            "price": self._safe_float_conversion(order_data.get("price")),
            "qty": self._safe_float_conversion(order_data.get("qty")),
            "status": order_data.get("orderStatus"),
            "avg_price": self._safe_float_conversion(order_data.get("avgPrice")),
            "cum_exec_qty": self._safe_float_conversion(order_data.get("cumExecQty")),
            "cum_exec_value": self._safe_float_conversion(order_data.get("cumExecValue")),
            "cum_exec_fee": self._safe_float_conversion(order_data.get("cumExecFee")),
            "closed_pnl": self._safe_float_conversion(order_data.get("closedPnl")),
            "category": order_data.get("category"),
            "created_time": self._convert_timestamp(order_data.get("createdTime")),
            "updated_time": self._convert_timestamp(order_data.get("updatedTime")),
            "raw_event": order_data,
        }
    
    def _convert_timestamp(self, timestamp: Optional[str]) -> Optional[datetime]:
        """Convert timestamp string to datetime object."""
        if not timestamp:
            return None
        
        try:
            return datetime.fromtimestamp(int(timestamp) / 1000)
        except (ValueError, TypeError, OverflowError):
            logger.warning(f"Could not convert timestamp {timestamp}")
            return None


# Initialize global managers
connection_manager = WebSocketConnectionManager()
transfer_manager = TransferManager(connection_manager)
message_handler = MessageHandler(connection_manager, transfer_manager)


@celery_app.task(name="tasks.connect_websocket")
def connect_websocket_task(accounts_data: Dict[str, Dict[str, str]]) -> None:
    """
    Celery task to establish WebSocket connections for all trading accounts.
    
    Args:
        accounts_data: Dictionary mapping subaccount names to their credentials
    """
    successful_connections = 0
    total_accounts = len(accounts_data)
    
    logger.info(f"Starting WebSocket connections for {total_accounts} accounts")
    
    for subaccount_name, credentials in accounts_data.items():
        try:
            if _establish_connection(subaccount_name, credentials):
                successful_connections += 1
        except Exception as e:
            logger.error(f"Failed to process account {subaccount_name}: {e}", exc_info=True)
    
    logger.info(
        f"WebSocket connection setup complete: {successful_connections}/{total_accounts} "
        f"accounts connected successfully"
    )
    
    # Keep the worker running to maintain connections
    _maintain_connections()


def _establish_connection(subaccount_name: str, credentials: Dict[str, str]) -> bool:
    """
    Establish WebSocket connection for a single subaccount.
    
    Args:
        subaccount_name: Name of the subaccount
        credentials: API credentials dictionary
        
    Returns:
        True if connection was established successfully, False otherwise
    """
    api_key = credentials.get("api_key")
    api_secret = credentials.get("api_secret")
    
    if not api_key or not api_secret:
        logger.error(f"Missing API credentials for subaccount: {subaccount_name}")
        return False
    
    # Check if already connected
    if connection_manager.is_connected(subaccount_name):
        logger.info(f"WebSocket already connected for subaccount: {subaccount_name}")
        return True
    
    try:
        logger.info(f"Establishing WebSocket connection for subaccount: {subaccount_name}")
        
        # Create WebSocket connection
        ws = WebSocket(
            testnet=True,  # Set to False for production
            channel_type="private",
            api_key=api_key,
            api_secret=api_secret,
        )
        
        # Create callback functions with proper closures
        def wallet_callback(message):
            message_handler.handle_wallet_message(message, subaccount_name)
        
        def order_callback(message):
            # message["data"] is a list of order dicts
            for order in message.get("data", []):
                message_handler.handle_private_orders_message(order, account_name=subaccount_name)  # Pass account_name
        
        # Subscribe to streams
        ws.wallet_stream(callback=wallet_callback)
        ws.order_stream(callback=order_callback)
        
        # Store connection
        connection_manager.active_connections[subaccount_name] = {
            "ws": ws,
            "connected": True,
            "api_key": api_key,
            "api_secret": api_secret
        }
        
        logger.info(f"✅ WebSocket connection established for subaccount: {subaccount_name}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to establish WebSocket connection for {subaccount_name}: {e}", exc_info=True)
        connection_manager.active_connections[subaccount_name] = {
            "ws": None,
            "connected": False,
            "api_key": api_key,
            "api_secret": api_secret
        }
        return False


def _maintain_connections() -> None:
    """Keep the worker running to maintain WebSocket connections."""
    logger.info("Starting connection maintenance loop")
    
    try:
        while True:
            sleep(30)  # Check every 30 seconds instead of every second
            # Here you could add connection health checks if needed
            
    except KeyboardInterrupt:
        logger.info("Connection maintenance loop interrupted")
    except Exception as e:
        logger.error(f"Error in connection maintenance loop: {e}", exc_info=True)


# Legacy function wrappers for backward compatibility
def handle_wallet_message(message: Dict[str, Any], subaccount_name: str) -> None:
    """Legacy wrapper for wallet message handling."""
    message_handler.handle_wallet_message(message, subaccount_name)


def handle_private_orders_message(order_data: Dict[str, Any]) -> None:
    """Legacy wrapper for private orders message handling."""
    message_handler.handle_private_orders_message(order_data)


def perform_internal_transfer(
    from_subaccount: str, 
    to_subaccount: str, 
    amount: float, 
    coin: str = "USDT"
) -> str:
    """Legacy wrapper for internal transfer functionality."""
    return transfer_manager.perform_internal_transfer(
        from_subaccount, to_subaccount, Decimal(str(amount)), coin
    )