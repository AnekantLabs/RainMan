import json
from celery import Celery
from pybit.unified_trading import WebSocket
from time import sleep
import logging
from celery_app import celery_app
from bybit_client import BybitClient
from tasks.constants import MAIN_ACCOUNT
from models import SessionLocal, Trade
from datetime import datetime

logger = logging.getLogger(__name__)


# Dictionary to track active WebSocket connections
active_connections = {}


def handle_message(message, subaccount_name):
    """
    Callback to handle WebSocket messages.
    Processes order streams, updates Redis, and transfers funds if necessary.
    """
    try:
        logger.info(f"Message received for {subaccount_name}: {message}")

        # Check if the message contains order information
        # if "orderId" in message.get("result", {}):
        #     order_id = message["result"]["orderId"]
        #     order_status = message["result"].get("orderStatus", "")

        #     # If the order status is "Filled", update the order in Redis
        #     if order_status.lower() == "filled":
        #         logger.info(f"Order {order_id} is filled for subaccount: {subaccount_name}")

        #         # Retrieve the order data from Redis
        #         redis_key = f"order:{order_id}"
        #         order_data = redis_client.get(redis_key)
        #         if order_data:
        #             order_data = json.loads(order_data)
        #             order_data["status"] = "filled"
        #             order_data["filled_at"] = time.time()
        #             redis_client.set(redis_key, json.dumps(order_data))
        #             logger.info(f"✅ Updated order {order_id} status to 'filled' in Redis.")
        #         else:
        #             logger.warning(f"⚠️ Order {order_id} not found in Redis.")

        #         # Check if the order is closing a long or short position
        #         side = message["result"].get("side", "").lower()
        #         if side in ["sell", "buy"]:
        #             logger.info(f"Order {order_id} is closing a {'long' if side == 'sell' else 'short'} position.")

        #             # Make an API call to check the balance in the account
        #             bybit_client = BybitClient(api_key=active_connections[subaccount_name]["api_key"],
        #                                        api_secret=active_connections[subaccount_name]["api_secret"])
        #             balance = bybit_client.get_wallet_balance(coin="USDT")

        #             # If the balance is greater than 0, transfer it to the main account
        #             if balance > 0:
        #                 logger.info(f"Balance in subaccount {subaccount_name} is {balance}. Initiating transfer to main account.")
        #                 main_account_id = bybit_client.get_acc_uid()  # Fetch the main account UID
        #                 transfer_status = bybit_client.transfer_funds(
        #                     from_uid=subaccount_name,
        #                     to_uid=main_account_id,
        #                     amount=balance,
        #                     coin="USDT"
        #                 )
        #                 if transfer_status == "SUCCESS":
        #                     logger.info(f"✅ Transferred {balance} USDT from {subaccount_name} to main account.")
        #                 else:
        #                     logger.error(f"❌ Failed to transfer {balance} USDT from {subaccount_name} to main account: {transfer_status}")
        #             else:
        #                 logger.info(f"ℹ️ No balance available in subaccount {subaccount_name} to transfer.")

    except Exception as e:
        logger.error(f"❌ Error processing message for {subaccount_name}: {e}")


def perform_internal_transfer(from_subaccount, to_subaccount, amount, coin="USDT"):
    """
    Performs an internal transfer of funds between subaccounts.
    Includes enhanced error handling and logging.
    """
    try:
        # Validate the amount
        if amount <= 0:
            logger.warning(f"Invalid transfer amount: {amount}. Transfer aborted.")
            return "INVALID_AMOUNT"

        # Fetch API keys for the subaccounts
        from_credentials = active_connections.get(from_subaccount)
        to_credentials = active_connections.get(to_subaccount)

        if not from_credentials or not to_credentials:
            logger.error(f"Missing credentials for subaccounts: {from_subaccount} or {to_subaccount}.")
            return "MISSING_CREDENTIALS"

        # Initialize Bybit clients for both subaccounts
        from_client = BybitClient(api_key=from_credentials["api_key"], api_secret=from_credentials["api_secret"])
        to_client = BybitClient(api_key=to_credentials["api_key"], api_secret=to_credentials["api_secret"])

        # Fetch UIDs for the subaccounts
        from_uid = from_client.get_acc_uid()
        to_uid = to_client.get_acc_uid()

        if not from_uid or not to_uid:
            logger.error(f"Failed to fetch UIDs for subaccounts: {from_subaccount} or {to_subaccount}.")
            return "UID_FETCH_FAILED"

        # Perform the transfer
        logger.info(f"Initiating transfer of {amount} {coin} from {from_subaccount} (UID: {from_uid}) to {to_subaccount} (UID: {to_uid})...")
        transfer_status = from_client.transfer_funds(from_uid=from_uid, to_uid=to_uid, amount=amount, coin=coin)

        if transfer_status == "SUCCESS":
            logger.info(f"✅ Transfer of {amount} {coin} from {from_subaccount} to {to_subaccount} completed successfully.")
        else:
            logger.error(f"❌ Transfer failed with status: {transfer_status}")

        return transfer_status

    except Exception as e:
        logger.error(f"❌ Error during internal transfer: {e}")
        return "TRANSFER_FAILED"
    
def handle_wallet_message(message, subaccount_name):
    """
    Callback to handle WebSocket messages related to wallet updates.
    Processes wallet streams and updates Redis.
    Calls get_transferable_amount for non-main accounts and transfers funds if available.
    """
    try:
        logger.info(f"Wallet message received for {subaccount_name}: {message}")

        # Skip processing for the main account
        if subaccount_name == MAIN_ACCOUNT:
            logger.info(f"Skipping wallet message processing for main account.")
            return

        # 1. Check if the message has 'data' and the correct structure
        if not message or "data" not in message or not isinstance(message["data"], list):
            logger.warning(f"Skipping invalid wallet message for {subaccount_name}")
            return

        wallet_data = message["data"][0]  # usually one wallet update at a time

        # Safely convert fields to float, defaulting to 0.0 if invalid
        total_available_balance = float(wallet_data.get("totalAvailableBalance", 0) or 0)
        total_initial_margin = float(wallet_data.get("totalInitialMargin", 0) or 0)
        total_perp_upl = float(wallet_data.get("totalPerpUPL", 0) or 0)

        logger.info(f"Subaccount {subaccount_name}: Available Balance={total_available_balance}, Initial Margin={total_initial_margin}, Unrealized PnL={total_perp_upl}")

        # 2. Call get_transferable_amount to fetch the transferable balance
        bybit_client = BybitClient(
            api_key=active_connections[subaccount_name]["api_key"],
            api_secret=active_connections[subaccount_name]["api_secret"]
        )
        transferable_amounts = bybit_client.get_transferable_amount(["USDT"])

        # Check if there is a transferable amount for USDT
        transferable_balance = float(transferable_amounts.get("USDT", 0) or 0)
        logger.info(f"Transferable balance for {subaccount_name}: {transferable_balance} USDT")

        # 3. Adjust transferable amount based on totalPerpUPL
        if total_perp_upl == 0:
            logger.info(f"TotalPerpUPL is 0 for {subaccount_name}. Transferring full transferable balance.")
            amount_to_transfer = transferable_balance
        else:
            logger.info(f"TotalPerpUPL is not 0 for {subaccount_name}. Deducting $5 from transferable balance.")
            amount_to_transfer = max(0, transferable_balance * 0.95)  # Ensure the amount is not negative

        # 4. Decide when balance is 'free' and transfer it to the main account
        if amount_to_transfer > 5:  # Set threshold (example: $5)
            logger.info(f"🎯 Transferable balance detected in {subaccount_name}: {amount_to_transfer} USDT. Initiating transfer to main account.")

            # Perform internal transfer
            transfer_status = perform_internal_transfer(
                from_subaccount=subaccount_name,
                to_subaccount=MAIN_ACCOUNT,
                amount=amount_to_transfer
            )

            if transfer_status == "SUCCESS":
                logger.info(f"✅ Successfully transferred {amount_to_transfer} USDT from {subaccount_name} to main account.")
            else:
                logger.error(f"❌ Failed to transfer {amount_to_transfer} USDT from {subaccount_name} to main account. Status: {transfer_status}")
        else:
            logger.info(f"No eligible balance transfer needed for {subaccount_name}. Transferable balance: {amount_to_transfer} USDT.")

    except Exception as e:
        logger.error(f"❌ Error processing wallet message for {subaccount_name}: {e}")
    


def handle_private_orders_message(order_data):
    session = SessionLocal()
    try:
        order_id = order_data.get("orderId")
        if not order_id:
            return

        trade = session.query(Trade).filter_by(order_id=order_id).first()
        # Parse and convert fields as needed
        def to_float(val):
            try:
                return float(val)
            except Exception:
                return None

        trade_data = {
            "symbol": order_data.get("symbol"),
            "side": order_data.get("side"),
            "order_type": order_data.get("orderType"),
            "price": to_float(order_data.get("price")),
            "qty": to_float(order_data.get("qty")),
            "status": order_data.get("orderStatus"),
            "avg_price": to_float(order_data.get("avgPrice")),
            "cum_exec_qty": to_float(order_data.get("cumExecQty")),
            "cum_exec_value": to_float(order_data.get("cumExecValue")),
            "cum_exec_fee": to_float(order_data.get("cumExecFee")),
            "closed_pnl": to_float(order_data.get("closedPnl")),
            "category": order_data.get("category"),
            "created_time": datetime.fromtimestamp(int(order_data.get("createdTime", 0)) / 1000) if order_data.get("createdTime") else None,
            "updated_time": datetime.fromtimestamp(int(order_data.get("updatedTime", 0)) / 1000) if order_data.get("updatedTime") else None,
            "raw_event": order_data,
        }

        if trade:
            for k, v in trade_data.items():
                setattr(trade, k, v)
        else:
            trade = Trade(order_id=order_id, **trade_data)
            session.add(trade)
        session.commit()
    except Exception as e:
        print(f"Error saving trade: {e}")
        session.rollback()
    finally:
        session.close()

@celery_app.task(name="tasks.connect_websocket")
def connect_websocket_task(accounts_data):
    """
    Celery task to ensure all accounts have active WebSocket connections.
    """
    for subaccount_name, credentials in accounts_data.items():
        api_key = credentials["api_key"]
        api_secret = credentials["api_secret"]

        # Check if the account already has an active connection
        if subaccount_name in active_connections and active_connections[subaccount_name]["connected"]:
            logger.info(f"WebSocket already connected for subaccount: {subaccount_name}")
            continue

        # Establish a new WebSocket connection
        try:
            logger.info(f"Establishing WebSocket connection for subaccount: {subaccount_name}")
            ws = WebSocket(
                testnet=True,  # Set to False for production
                channel_type="private",
                api_key=api_key,
                api_secret=api_secret,
            )
            # Attach subaccount name in the callback properly
            def callback_with_account(message, subaccount_name=subaccount_name):
                # Here you attach account info
                handle_wallet_message(message,subaccount_name)

            # Subscribe with the custom callback
            ws.wallet_stream(callback=callback_with_account)
            ws.order_stream(callback=lambda message: handle_private_orders_message(message, subaccount_name))
            # Store the connection in the active_connections dictionary
            active_connections[subaccount_name] = {"ws": ws, "connected": True, "api_key": api_key, "api_secret": api_secret}
            logger.info(f"WebSocket connection established for subaccount: {subaccount_name}")
        except Exception as e:
            logger.error(f"Failed to establish WebSocket connection for subaccount {subaccount_name}: {e}")
            active_connections[subaccount_name] = {"ws": None, "connected": False}

    # Keep the worker running to maintain WebSocket connections
    while True:
        sleep(1)


