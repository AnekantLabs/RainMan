from celery_app import app
from bybit_client import BybitClient
import traceback
import json

# Initialize Bybit client
# bybit_client = BybitClient(api_key="your_api_key", api_secret="your_api_secret")

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
        apikey = alert.get("api_key")
        secret = alert.get("api_secret")
        coin = "USDT"  # hardcoded for now, can make dynamic
        logger.info(f"Alert details: account={account}, action={action}, symbol={symbol}, apikey={apikey}, secret={secret} , symbol={symbol}")
        bybit_client = BybitClient(api_key=str(apikey), api_secret=str(secret))

        if action.upper() == "SELL":
            print(f"🛑 Sell alert received for {symbol} on {account}")
            
            # Fetch wallet balance before selling to determine how much to sell (e.g., spot token balance)
            token = symbol.replace("USDT", "")  # e.g., BTC if symbol is BTCUSDT
            token_balance = bybit_client.get_wallet_balance(coin=token)

            if token_balance > 0:
                # Step 1: Close the position (market sell)
                response = bybit_client.place_order(
                    category="spot",
                    market_pair=symbol,
                    side="Sell",
                    order_type="Market",
                    amount=token_balance
                )
                print(f"✅ Closed position on {account}: Sold {token_balance} {token}")
            else:
                print(f"⚠️ No {token} balance in {account} to sell.")

            # Step 2: Transfer all USDT back to main
            usdt_balance = bybit_client.get_wallet_balance(coin="USDT")
            if account != "main" and usdt_balance > 0:
                transfer_status = bybit_client.transfer_funds(
                    from_uid=account,
                    to_uid="main",
                    amount=usdt_balance,
                    coin="USDT"
                )
                print(f"🔁 Transferred {usdt_balance} USDT from {account} back to main: {transfer_status}")
            else:
                print(f"ℹ️ No USDT available to return from {account}.")

        else:
            # BUY/OPEN Logic
            risk_percentage = alert.get("risk_percentage", 1)
            leverage = alert.get("leverage", 1)
            entry_price = alert.get("entry_price")
            stop_loss = alert.get("stop_loss")

            stop_loss_distance = abs(float(entry_price) - float(stop_loss)) / float(entry_price)
            total_balance = bybit_client.get_wallet_balance(coin="USDT")
            position_size = calculate_position_size(
                total_balance, risk_percentage, stop_loss_distance, leverage
            )
            print(f"Calculated position size: {position_size} USDT")

            if account != "main":
                transfer_status = bybit_client.transfer_funds("main", account, position_size, coin="USDT")
                if transfer_status != "SUCCESS":
                    raise ValueError(f"Transfer failed: {transfer_status}")
                print(f"✅ Transferred {position_size} USDT to {account}")

            # Place BUY order
            qty = position_size / float(entry_price)
            response = bybit_client.place_order(
                category="spot",
                market_pair=symbol,
                side="Buy",
                order_type="Market",
                amount=qty
            )
            print(f"✅ Order placed successfully: {response}")

    except Exception as e:
        print(f"Error processing alert: {str(e)}")
        print(traceback.format_exc())


def calculate_position_size(balance, risk_percentage, stop_loss_distance, leverage):
    """
    Calculates the position size based on risk parameters.
    """
    commission_percentage = 0.00055  # Example commission percentage
    return (balance * (risk_percentage / 100)) / ((stop_loss_distance + commission_percentage) * leverage)