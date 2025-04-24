
import uuid
from pybit.unified_trading import HTTP
import logging

# Set up logging (add this near the top of your file)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

    def get_wallet_balance(self, coin="USDT"):
        """
        Fetches the available wallet balance for a given coin (default: USDT) from a UNIFIED account.
        Returns the available balance as a float.
        """
        try:
            logger.info(f"Fetching wallet balance for {coin.upper()}...")
            response = self.session.get_wallet_balance(
                accountType="UNIFIED",
                coin=coin.upper()
            )
            wallet_list = response.get("result", {}).get("list", [])
            if not wallet_list:
                print("❌ No wallet data returned.")
                return 0.0

            coin_list = wallet_list[0].get("coin", [])
            for c in coin_list:
                if c["coin"] == coin.upper():
                    balance = float(c["walletBalance"])
                    print(f"✅ Available {coin.upper()} Balance: {balance}")
                    return balance
            return 0.0
        except Exception as e:
            print(f"❌ Error fetching wallet balance: {e}")
            return 0.0

    def transfer_funds(self, from_uid, to_uid, amount, coin="USDT"):
        """
        Transfers funds between Unified accounts under same UID via internal transfer API.
        """
        transfer_id = str(uuid.uuid4())
        try:
            # Round the amount to 6 decimal places
            amount = round(amount, 2)
            print(f"Initiating transfer of {amount} {coin} from {from_uid} → {to_uid}")
            logger.info(f"Transfer ID: {transfer_id}. Initiating transfer of {amount} {coin} from {from_uid} → {to_uid}")
            response = self.session.create_universal_transfer(
                transferId=transfer_id,
                coin=coin,
                amount=str(amount),
                fromMemberId=from_uid,
                toMemberId=to_uid,
                fromAccountType="UNIFIED",
                toAccountType="UNIFIED"
            )
            transfer_status = response.get("result", {}).get("status", "UNKNOWN")
            print(f"[{transfer_status}] Transfer ID: {transfer_id}")
            return transfer_status
        except Exception as e:
            print(f"❌ Transfer failed: {e}")
            raise

    def place_order(self, category, market_pair, side, order_type, amount, stop_loss=None):
        """
        Places an order on Bybit.
        """
        
        # to place a market order on BYBIT
        try:
            amount = float(amount)
            response = self.session.place_order(
                category=category,
                symbol=market_pair,
                side=side,
                order_type=order_type,
                qty=amount,
                timeInForce="GTC",
                stopLoss=stop_loss,
            )
            print(f"Order placed successfully: {response}")
            return {"status": "success", "order_id": response['result']['order_id']}
        except Exception as e:
            raise ValueError(f"Error placing order:{e} Stack trace: {e.__traceback__}")
        
    def place_entry_and_tp_orders(self, category, symbol, side, order_type, qty, stop_loss=None, tps=None, tp_sizes=None):
        """
        Places an entry market order and optional batch take-profit orders.

        :param symbol: Trading pair (e.g., "ETHUSDT").
        :param side: "Buy" or "Sell" for the entry order.
        :param order_type: Type of the entry order (e.g., "Market").
        :param qty: Quantity for the entry order.
        :param stop_loss: Stop-loss price for the entry order (optional).
        :param tps: List of take-profit prices (optional).
        :param tp_sizes: List of percentages for each take-profit level (optional).
        :return: Response from the entry order and TP orders (if applicable).
        """
        try:
            # Step 1: Place the entry market order
            qty = round(float(qty), 2)  # Round to 2 decimal places for quantity
            qty = str(qty)  # Convert to string for API compatibility
            print(f"Placing {side} order for {symbol} with qty={qty} and stop_loss={stop_loss}")
            
            entry_response = self.session.place_order(
                category=category,
                symbol=symbol,
                side=side,
                order_type=order_type,
                qty=qty,
                # timeInForce="IOC",
                timeInForce="GTC",
                # stopLoss=stop_loss,
                marketUnit="baseCoin"
            )
            print(f"✅ Entry order placed successfully: {entry_response}")
            
            # STOPLOSS ORDER CANT BE PLACED WTIH SPOT CATEGORY, CURRENTLY WE ARE USING SPOT CATEGORY
            
            # Step 2: Check if TP orders are provided
            if tps and tp_sizes and len(tps) == len(tp_sizes):
                print(f"Placing batch TP orders for {symbol}")
                tp_orders = []
                for tp_price, tp_size in zip(tps, tp_sizes):
                    tp_qty = str(round(float(qty) * (float(tp_size) / 100), 5))
                    tp_orders.append({
                        "symbol": symbol,
                        "side": "Sell" if side.lower() == "buy" else "Buy",  # Opposite side for TP
                        "orderType": "Limit",
                        "qty": tp_qty,
                        "price": str(tp_price),
                        "timeInForce": "GTC",
                        # "reduceOnly": True,  # Ensure it only reduces the position
                        "marketUnit": "baseCoin",
                    })

                
                print(f"TP orders: {tp_orders}")
                
                # Place batch TP orders
                batch_response = self.session.place_batch_order(category=category, request=tp_orders)
                print(f"✅ Batch TP orders placed successfully: {batch_response}")
                return {"entry_response": entry_response, "tp_response": batch_response}

            # If no TP orders, return only the entry response
            return {"entry_response": entry_response}

        except Exception as e:
            print(f"❌ Error placing entry and TP orders: {e}")
            raise
        
    # function to fetch the UID of the main account
    def get_acc_uid(self):
        """
        Fetches the UID of the main account.
        """
        try:
            response = self.session.get_uid_wallet_type(accountType="UNIFIED")
            main_uid = response.get("result", {}).get("accounts", [{}])[0].get("uid")
            print(f"account UIDDD: {main_uid}")
            return main_uid
        except Exception as e:
            print(f"❌ Error fetching main UID: {e}")
            return None
        

    
    def get_instrument_info(self, symbol, category="spot"):
        """
        Fetches instrument information for a given symbol.
        """
        try:
            response = self.session.get_instruments_info(symbol=symbol, category=category)
            if response.get("result"):
                return response["result"]
            else:
                print(f"❌ Error fetching instrument info: {response.get('ret_msg', 'Unknown error')}")
                return None
        except Exception as e:
            print(f"❌ Error fetching instrument info: {e}")
            return None