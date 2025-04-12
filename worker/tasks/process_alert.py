from celery_app import app
from bybit_client import BybitClient

# Initialize Bybit client
# bybit_client = BybitClient(api_key="your_api_key", api_secret="your_api_secret")

@app.task(name="tasks.process_alert")
def process_alert(alert):
    """
    Processes a TradingView alert, rebalances funds, and places an order.
    """
    print("Processing alert...")
    try:
        print(f"Received alert: {alert}")  # Print the alert
        # Extract alert details
        account = alert["account"]
        action = alert["action"]
        symbol = alert["symbol"]
        risk_percentage = alert.get("risk_percentage", 1)  # Default risk percentage
        leverage = alert.get("leverage", 1)  # Default leverage
        entry_price = alert.get("entry_price")
        stop_loss = alert.get("stop_loss")
        tps = alert.get("tps", [])
        tp_sizes = alert.get("tp_sizes", [])

        print(f"Processing alert for account: {account}, action: {action}, symbol: {symbol}")
        
        # initialize the bybit client with the account credentials
        bybit_client = BybitClient(api_key="your_api_key", api_secret="your_api_secret")

        # Step 1: Rebalance funds
        total_balance = bybit_client.get_balance(account)
        stop_loss_distance = abs(float(entry_price) - float(stop_loss)) / float(entry_price)
        position_size = calculate_position_size(
            total_balance, risk_percentage, stop_loss_distance, leverage
        )
        print(f"Total balance: {total_balance} USDT, Stop Loss Distance: {stop_loss_distance}")
        print(f"Calculated position size: {position_size} USDT")

        # Transfer funds if necessary
        if account != "main":
            bybit_client.transfer_funds("main", account, position_size)
            print(f"Transferred {position_size} USDT to {account}")

        # Step 2: Place the order
        response = bybit_client.place_order(
            market_pair=symbol,
            side=action,
            order_type="market",
            amount=position_size / float(entry_price),  # Convert USDT to quantity
            leverage=leverage,
            stop_loss=stop_loss,
            take_profits=tps,
            tp_sizes=tp_sizes,
        )
        print(f"Order placed successfully: {response}")

    except Exception as e:
        print(f"Error processing alert: {e}")


def calculate_position_size(balance, risk_percentage, stop_loss_distance, leverage):
    """
    Calculates the position size based on risk parameters.
    """
    commission_percentage = 0.00055  # Example commission percentage
    return (balance * (risk_percentage / 100)) / ((stop_loss_distance + commission_percentage) * leverage)