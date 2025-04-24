from celery_app import app
from bybit_client import BybitClient
import traceback
import json

# Initialize Bybit client
# bybit_client = BybitClient(api_key="your_api_key", api_main_secret="your_api_main_secret")

import logging

# Set up logging (add this near the top of your file)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.task(name="tasks.process_alert")
def process_alert(alert):
    """
    Processes a TradingView alert, rebalances funds, and places an order.
    """
    print("Processing alert...")
    try:
        alert = json.loads(alert)
        account = alert["account"]
        action = alert["action"]
        symbol = alert["symbol"]
        main_apikey = alert.get("main_api_key")
        main_secret = alert.get("main_api_secret")
        tps = alert.get("tps", [])
        tp_sizes = alert.get("tp_sizes", [])
        
        coin = "USDT"  # hardcoded for now, can make dynamic
        logger.info(f"Alert details: account={account}, action={action}, symbol={symbol}, main_apikey={main_apikey}, main_secret={main_secret} , symbol={symbol}")
        bybit_client = BybitClient(api_key=str(main_apikey), api_secret=str(main_secret))       # Initialize BybitClient with main account credentials
        
        # fetch the member ID of the main-account
        main_account_id = bybit_client.get_acc_uid()

        # get the instrument details for the symbol
        instrument_details = bybit_client.get_instrument_info(symbol=symbol)
        if not instrument_details:
            raise ValueError(f"Failed to fetch instrument details for {symbol}")
        print(f"Instrument details: {instrument_details}")

        # bybit client for sub-account
        if account != "main":
            # create a new BybitClient instance for the sub-account
            sub_apikey = alert.get("api_key")
            sub_secret = alert.get("api_secret")
            bybit_client_sub_account = BybitClient(api_key=str(sub_apikey), api_secret=str(sub_secret))
            sub_account_id = bybit_client_sub_account.get_acc_uid()
            print(f"Sub-account client initialized {account} with subaccount ID {sub_account_id}")
        
        if action.upper() == "SELL":
            print(f"🛑 Sell alert received for {symbol} on {account}")
            token = symbol.replace("USDT", "")  # e.g., BTC if symbol is BTCUSDT
            
            if account != "main":
                # Fetch wallet balance before selling to determine how much to sell (e.g., spot token balance)
                token_balance = bybit_client_sub_account.get_wallet_balance(coin=token)
                
                if token_balance > 0:
                    # Step 1: Close the position (market sell)
                    response = bybit_client_sub_account.place_entry_and_tp_orders(
                        category="spot",
                        symbol=symbol,
                        side="Sell",
                        order_type="Market",
                        qty=token_balance,
                        stop_loss=None,  # No stop loss for market sell
                        tps=tps,
                        tp_sizes=tp_sizes
                    )
                    print(f"✅ Closed position on {account}: Sold {token_balance} {token}")
                else:
                    print(f"⚠️ No {token} balance in {account} to sell. In sub-account.")
                
                # Step 2: Transfer all USDT back to main
                usdt_balance = bybit_client_sub_account.get_wallet_balance(coin="USDT")
                if account != "main" and usdt_balance > 0:
                    transfer_status = bybit_client_sub_account.transfer_funds(
                        from_uid=sub_account_id,
                        to_uid=main_account_id,
                        amount=usdt_balance,
                        coin="USDT"
                    )
                    print(f"🔁 Transferred {usdt_balance} USDT from {account} back to main: {transfer_status}")
                else:
                    print(f"ℹ️ No USDT available to return from {account}.")
            
            else:
                # Fetch wallet balance before selling to determine how much to sell (e.g., spot token balance)
                token_balance = bybit_client.get_wallet_balance(coin=token)

                if token_balance > 0:
                    # Step 1: Close the position (market sell)
                    response = bybit_client.place_entry_and_tp_orders(
                        category="spot",
                        symbol=symbol,
                        side="Sell",
                        order_type="Market",
                        qty=token_balance,
                        stop_loss=None,  # No stop loss for market sell
                        tps=tps,
                        tp_sizes=tp_sizes
                    )
                    print(f"✅ Closed position on {account}: Sold {token_balance} {token}")
                else:
                    print(f"⚠️ No {token} balance in {account} to sell. In main account.")

        else:
            # BUY/OPEN Logic
            risk_percentage = alert.get("risk_percentage", 1)
            leverage = alert.get("leverage", 1)
            entry_price = alert.get("entry_price")
            stop_loss = alert.get("stop_loss")
            commission_percentage = alert.get("commission_percentage", 0.00055)  # Example commission percentage

            stop_loss_distance = abs(float(entry_price) - float(stop_loss)) / float(entry_price)
            total_balance = bybit_client.get_wallet_balance(coin="USDT")
            
            position_size = calculate_position_size(
                total_balance, risk_percentage, stop_loss_distance, leverage, commission_percentage
            )
            
            print(f"Calculated position size: {position_size} USDT")

            # place order from sub-account if not main account
            if account != "main":
                # transfer_status = bybit_client.transfer_funds("main", account, position_size, coin="USDT")
                transfer_status = bybit_client.transfer_funds(main_account_id, sub_account_id, position_size, coin="USDT")
                if transfer_status != "SUCCESS":
                    raise ValueError(f"Transfer failed: {transfer_status}")
                print(f"✅ Transferred {position_size} USDT to {account}")

                # Place BUY order
                qty = position_size / float(entry_price)
                response = bybit_client_sub_account.place_entry_and_tp_orders(
                    category="linear",
                    symbol=symbol,
                    side="Buy",
                    order_type="Market",
                    qty=qty,
                    stop_loss=stop_loss,
                    tps=tps,
                    tp_sizes=tp_sizes
                )
                print(f"✅ Market Order placed successfully: {response} from Sub account {account}")
            # place order from main account
            else:
                # Place BUY order on main account
                qty = position_size / float(entry_price)
                response = bybit_client.place_entry_and_tp_orders(
                    category="spot",
                    symbol=symbol,
                    side="Buy",
                    order_type="Market",
                    qty=qty,
                    stop_loss=stop_loss,
                    tps=tps,
                    tp_sizes=tp_sizes
                )
                print(f"✅ Market Order placed successfully: {response} from Main account {account}") 

    except Exception as e:
        print(f"Error processing alert: {str(e)}")
        print(traceback.format_exc())


def calculate_position_size(balance, risk_percentage, stop_loss_distance, leverage, commission_percentage):
    """
    Calculates the position size based on risk parameters.
    """
    # commission_percentage = 0.00055  # Example commission percentage
    return (balance * (risk_percentage / 100)) / ((stop_loss_distance + commission_percentage) * leverage)