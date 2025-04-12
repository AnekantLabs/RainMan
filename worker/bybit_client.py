
from pybit.unified_trading import HTTP

class BybitClient:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.bybit.com"
        self.testnet = True     # True means your API keys were generated on testnet.bybit.com
        self.session = HTTP(
            api_key=self.api_key,
            api_secret=self.api_secret,
            testnet=self.testnet,
        )

    def get_balance(self, account):
        """
        Fetches the balance of the specified account.
        """
        # Example API call to fetch balance
        print(f"Fetching balance for account: {account}")
        return 10000  # Mock balance for demonstration

    def transfer_funds(self, from_account, to_account, amount):
        """
        Transfers funds between accounts.
        """
        print(f"Transferring {amount} USDT from {from_account} to {to_account}")
        # Example API call to transfer funds
        return {"status": "success", "amount": amount}

    def place_order(self, market_pair, side, order_type, amount, leverage, stop_loss, take_profits, tp_sizes):
        """
        Places an order on Bybit.
        """
        
        # to place a market order on BYBIT
        try:
            amount = float(amount)
            response = self.session.place_order(
                symbol=market_pair,
                side=side,
                order_type=order_type,
                qty=amount,
                leverage=leverage,
                stop_loss=stop_loss,
                take_profits=take_profits,
                tp_sizes=tp_sizes
            )
            print(f"Order placed successfully: {response}")
            return {"status": "success", "order_id": response['result']['order_id']}
        except Exception as e:
            raise ValueError(f"Error placing order:{e} Stack trace: {e.__traceback__}")
        
        # Example API call to place an order