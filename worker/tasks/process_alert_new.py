from celery_app import celery_app
from bybit_client import BybitClient
import traceback
import json
import logging
from decimal import Decimal
from typing import Dict, List, Optional, Union, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AlertProcessor:
    """Class to handle TradingView alert processing and trading operations."""
    
    def __init__(self, alert_data: Dict[str, Any]):
        """Initialize with alert data."""
        self.alert = alert_data
        self.account = alert_data.get("account")
        self.action = alert_data.get("action", "").upper()
        self.symbol = alert_data.get("symbol")
        self.side = alert_data.get("side", "").lower()  # Add side attribute (long/short)
        self.margin_type = alert_data.get("margin_type", "cross")  # Add margin type
        self.main_api_key = alert_data.get("main_api_key")
        self.main_api_secret = alert_data.get("main_api_secret")
        self.tps = alert_data.get("tps", [])
        self.tp_sizes = alert_data.get("tp_sizes", [])
        self.coin = "USDT"  # Default coin, could be made dynamic
        
        # Initialize main client
        self.main_client = BybitClient(
            api_key=str(self.main_api_key), 
            api_secret=str(self.main_api_secret)
        )
        self.main_account_id = self.main_client.get_acc_uid()
        
        # Initialize sub-account client if needed
        self.sub_client = None
        self.sub_account_id = None
        if self.account != "main":
            sub_api_key = alert_data.get("api_key")
            sub_api_secret = alert_data.get("api_secret")
            self.sub_client = BybitClient(
                api_key=str(sub_api_key), 
                api_secret=str(sub_api_secret)
            )
            self.sub_account_id = self.sub_client.get_acc_uid()
            logger.info(f"Sub-account client initialized: {self.account} with ID {self.sub_account_id}")
        
        # Get instrument details
        self.instrument_details = self.main_client.get_instrument_info(symbol=self.symbol)
        if not self.instrument_details:
            raise ValueError(f"Failed to fetch instrument details for {self.symbol}")
        logger.info(f"Instrument details retrieved for {self.symbol}")

    def get_active_client(self):
        """Return the appropriate client based on account type."""
        return self.sub_client if self.account != "main" else self.main_client
    
    def process(self):
        """Process the alert based on action type."""
        logger.info(f"Processing {self.action} alert for {self.symbol} on {self.account} account")
        
        action_handlers = {
            "OPEN": self.handle_open,   # Replace BUY with OPEN to handle both long and short
            "SELL": self.handle_sell,
            "CLOSE": self.handle_close,
            "TRAIL_SL": self.handle_trail_sl
        }
        
        handler = action_handlers.get(self.action)
        if handler:
            return handler()
        else:
            raise ValueError(f"Unsupported action: {self.action}")
    
    def handle_open(self):
        """Handle OPEN action for both long and short positions."""
        if self.side not in ["long", "short"]:
            raise ValueError(f"Invalid side: {self.side}. Must be 'long' or 'short'")
            
        risk_percentage = self.alert.get("risk_percentage", 1)
        leverage = int(self.alert.get("leverage", 1))
        entry_price = Decimal(str(self.alert.get("entry_price", 0)))
        stop_loss = Decimal(str(self.alert.get("stop_loss", 0)))
        commission_percentage = self.alert.get("commission_percentage", 0.00055)
        
        if not entry_price or not stop_loss:
            raise ValueError("Missing entry_price or stop_loss in alert data")
        
        # Calculate stop loss distance based on position side
        if self.side == "long":
            if stop_loss >= entry_price:
                raise ValueError("Stop loss must be below entry price for long positions")
            stop_loss_distance = abs(entry_price - stop_loss) / entry_price
        else:  # short
            if stop_loss <= entry_price:
                raise ValueError("Stop loss must be above entry price for short positions")
            stop_loss_distance = abs(stop_loss - entry_price) / entry_price
        
        total_balance = self.main_client.get_wallet_balance(coin=self.coin)
        
        position_size = self._calculate_position_size(
            total_balance, 
            risk_percentage, 
            float(stop_loss_distance), 
            leverage, 
            commission_percentage
        )
        
        logger.info(f"Calculated position size: {position_size} {self.coin}")
        
        # Transfer funds if using sub-account
        if self.account != "main":
            transfer_status = self.main_client.transfer_funds(
                self.main_account_id, 
                self.sub_account_id, 
                position_size, 
                coin=self.coin
            )
            if transfer_status != "SUCCESS":
                raise ValueError(f"Transfer failed: {transfer_status}")
            logger.info(f"Transferred {position_size} {self.coin} to {self.account}")
        
        # Place order
        client = self.get_active_client()
        qty = position_size / float(entry_price)
        
        # Set margin type before placing order
        client.set_margin_mode(self.margin_type, self.symbol)
        
        # Set leverage for the position
        client.set_leverage(leverage, self.symbol)
        
        # Convert position side to order side
        order_side = "Buy" if self.side == "long" else "Sell"
        
        response = client.place_entry_and_tp_orders(
            category="linear",
            symbol=self.symbol,
            side=order_side,
            order_type="Market",
            qty=qty,
            stop_loss=stop_loss,
            tps=self.tps,
            tp_sizes=self.tp_sizes
        )
        
        logger.info(f"Market {order_side} order placed on {self.account} account: {response}")
        return response
    
    def handle_sell(self):
        """Handle SELL action for spot trading."""
        token = self.symbol.replace(self.coin, "")  # E.g., BTC if symbol is BTCUSDT
        client = self.get_active_client()
        
        # Get token balance
        token_balance = client.get_wallet_balance(coin=token)
        
        if token_balance <= 0:
            logger.warning(f"No {token} balance in {self.account} account to sell")
            return {"status": "nothing_to_sell", "balance": 0}
        
        # Place sell order
        response = client.place_entry_and_tp_orders(
            category="spot",
            symbol=self.symbol,
            side="Sell",
            order_type="Market",
            qty=token_balance,
            stop_loss=None,
            tps=self.tps,
            tp_sizes=self.tp_sizes
        )
        
        logger.info(f"Sold {token_balance} {token} on {self.account} account")
        
        # Transfer USDT back to main if from sub-account
        if self.account != "main":
            usdt_balance = self.sub_client.get_wallet_balance(coin=self.coin)
            if usdt_balance > 0:
                transfer_status = self.sub_client.transfer_funds(
                    self.sub_account_id,
                    self.main_account_id,
                    usdt_balance,
                    coin=self.coin
                )
                logger.info(f"Transferred {usdt_balance} {self.coin} from {self.account} back to main: {transfer_status}")
            else:
                logger.info(f"No {self.coin} available to return from {self.account}")
        
        return response
    
    def handle_close(self):
        """Handle CLOSE action."""
        client = self.get_active_client()
        results = {}
        
        try:
            # Cancel all open orders
            cancel_response = client.cancel_all_orders(symbol=self.symbol, category="linear")
            results["cancel_orders"] = cancel_response
            logger.info(f"Canceled all open orders for {self.symbol} on {self.account} account")
            
            # Get position info and close if exists
            position_info = client.get_position_info(symbol=self.symbol)
            
            if position_info and float(position_info.get("size", 0)) > 0:
                # Determine opposite side for closing
                side = "Sell" if position_info.get("side") == "Buy" else "Buy"
                qty = float(position_info.get("size"))
                
                close_response = client.place_order(
                    "linear",
                    self.symbol,
                    side,
                    "Market",
                    qty
                )
                results["close_position"] = close_response
                logger.info(f"Closed position on {self.account} account: {close_response}")
            else:
                logger.info(f"No open position found for {self.symbol} on {self.account} account")
                results["close_position"] = "no_position_found"
        
        except Exception as e:
            logger.error(f"Error closing position: {str(e)}")
            logger.error(traceback.format_exc())
            results["error"] = str(e)
        
        return results
    
    def handle_trail_sl(self):
        """Handle TRAIL_SL action."""
        client = self.get_active_client()
        
        try:
            # Get current position data
            position_response = client.get_position_info(
                category="linear",
                symbol=self.symbol
            )
            
            # Check if position exists
            if position_response.get("size") and float(position_response["size"]) > 0:
                trailing_stop = self.alert.get("stop_loss")
                
                if not trailing_stop:
                    raise ValueError("Missing 'stop_loss' in the alert payload")
                
                # Check if stop loss makes sense for the position side
                position_side = position_response.get("side")
                current_price = float(client.get_current_price(self.symbol))
                trailing_stop_value = float(trailing_stop)
                
                if (position_side == "Buy" and trailing_stop_value >= current_price) or \
                   (position_side == "Sell" and trailing_stop_value <= current_price):
                    raise ValueError(f"Invalid stop loss ({trailing_stop}) for {position_side} position at price {current_price}")
                
                # Prepare request parameters
                params = {
                    "category": "linear",
                    "symbol": self.symbol,
                    "positionIdx": position_response.get("positionIdx", 0),
                    "tpslMode": "Full",
                    "stopLoss": str(trailing_stop)
                }
                
                # Update stop loss
                response = self._set_trading_stop(client, params)
                
                if response.get("retCode") == 0:
                    logger.info(f"Updated trailing stop-loss for {self.symbol} on {self.account} account")
                    return {"status": "success", "response": response}
                else:
                    error_msg = response.get("retMsg", "Unknown error")
                    logger.error(f"Failed to update trailing stop-loss: {error_msg}")
                    return {"status": "error", "message": error_msg}
            else:
                logger.info(f"No open position found for {self.symbol} on {self.account} account")
                return {"status": "no_position", "message": "No open position found"}
        
        except Exception as e:
            logger.error(f"Error updating trailing stop-loss: {str(e)}")
            logger.error(traceback.format_exc())
            return {"status": "error", "message": str(e)}
    
    def _set_trading_stop(self, client, params):
        """Helper method to set trading stop with proper error handling."""
        try:
            return client.session.set_trading_stop(**params)
        except AttributeError:
            # Fallback if client.session doesn't exist
            if self.account != "main":
                return self.sub_client.session.set_trading_stop(**params)
            else:
                return self.main_client.session.set_trading_stop(**params)
    
    @staticmethod
    def _calculate_position_size(
        balance: float, 
        risk_percentage: float, 
        stop_loss_distance: float, 
        leverage: float, 
        commission_percentage: float
    ) -> float:
        """
        Calculate position size based on risk parameters.
        
        Args:
            balance: Total account balance
            risk_percentage: Percentage of balance to risk (1 = 1%)
            stop_loss_distance: Distance to stop loss as decimal (price difference/entry price)
            leverage: Trading leverage multiplier
            commission_percentage: Trading fee percentage as decimal
            
        Returns:
            Position size in base currency
        """
        # Apply leverage for futures trading
        risk_amount = balance * (risk_percentage / 100)
        position_size = risk_amount / (stop_loss_distance + commission_percentage)
        
        # The position size calculation takes leverage into account for risk management
        # but doesn't multiply by leverage (as that would increase the risk)
        return position_size


@celery_app.task(name="tasks.process_alert", bind=True, max_retries=3)
def process_alert(self, alert_data):
    """
    Celery task to process a TradingView alert.
    
    Args:
        alert_data: Alert data as a JSON string or dict
    """
    logger.info("Processing alert...")
    
    try:
        # Parse alert data if it's a string
        if isinstance(alert_data, str):
            alert_data = json.loads(alert_data)
        
        # Process the alert
        processor = AlertProcessor(alert_data)
        result = processor.process()
        
        logger.info(f"Alert processing completed successfully: {result}")
        return result
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in alert data: {str(e)}")
        raise
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise
    
    except Exception as e:
        logger.error(f"Error processing alert: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Retry the task with exponential backoff for transient errors
        # Skip retrying for validation errors (e.g. ValueError)
        if not isinstance(e, ValueError):
            retry_in = 5 * (2 ** self.request.retries)  # 5, 10, 20 seconds
            self.retry(exc=e, countdown=retry_in)
        
        raise