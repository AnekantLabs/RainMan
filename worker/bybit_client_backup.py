
import uuid
from pybit.unified_trading import HTTP
import logging

from redis_client import save_order_to_redis

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


    def get_transferable_amount(self, coins):
        """
        Fetches the transferable amount for specific coins in the Unified wallet.
        
        Args:
            coins (list): List of coin names (e.g., ["BTC", "USDT", "ETH"]).
        
        Returns:
            dict: A dictionary containing the transferable amounts for each coin.
                  Example: {"BTC": "4.54549050", "USDT": "100.00000000"}
        """
        try:
            # Convert the list of coins to a comma-separated string
            coin_names = ",".join([coin.upper() for coin in coins])
            logger.info(f"Fetching transferable amounts for coins: {coin_names}")

            # Make the API request
            response = self.session.get_transferable_amount(coinName=coin_names)

            # Check for a successful response
            if response.get("retCode") == 0:
                transferable_map = response.get("result", {}).get("availableWithdrawalMap", {})
                logger.info(f"✅ Transferable amounts fetched successfully: {transferable_map}")
                return transferable_map
            else:
                logger.error(f"❌ Error fetching transferable amounts: {response.get('retMsg', 'Unknown error')}")
                return {}
        except Exception as e:
            logger.error(f"❌ Exception while fetching transferable amounts: {e}")
            return {}
        

    def transfer_funds(self, from_uid, to_uid, amount, coin="USDT", max_retries=3):
        """
        Transfers funds between Unified accounts under the same UID via the internal transfer API.
        Retries up to max_retries times, reducing the transfer amount by 0.5% on each failure.

        Args:
            from_uid (str): The UID of the source account.
            to_uid (str): The UID of the destination account.
            amount (float): The amount to transfer.
            coin (str): The coin to transfer (default: "USDT").
            max_retries (int): Maximum number of retries for the transfer.

        Returns:
            str: The final transfer status.
        """
        transfer_id = str(uuid.uuid4())
        retries = 0
        while retries < max_retries:
            try:
                # Round the amount to 2 decimal places
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
                if transfer_status == "SUCCESS":
                    print(f"✅ Transfer successful: {amount} {coin} from {from_uid} → {to_uid}")
                    logger.info(f"✅ Transfer successful: {amount} {coin} from {from_uid} → {to_uid}")
                    return transfer_status
                else:
                    error_message = response.get("retMsg", "Unknown error")
                    logger.warning(f"❌ Transfer failed: {error_message}")
                    raise ValueError(f"Transfer failed: {error_message}")
            
            except Exception as e:
                retries += 1
                logger.error(f"❌ Transfer attempt {retries} failed: {e}")
                print(f"❌ Transfer attempt {retries} failed: {e}")
                
                if retries < max_retries:
                    # Reduce the transfer amount by 0.5% for the next attempt
                    amount *= 0.995
                    print(f"Retrying transfer with reduced amount: {amount:.2f} {coin}")
                    logger.info(f"Retrying transfer with reduced amount: {amount:.2f} {coin}")
                else:
                    print(f"❌ Transfer failed after {max_retries} attempts.")
                    logger.error(f"❌ Transfer failed after {max_retries} attempts.")
                    return "TRANSFER_FAILED"

    def amend_stop_loss(self, category, symbol, order_id=None, order_link_id=None, stop_loss=None):
        """
        Amends the stop-loss for an existing order.

        Args:
            category (str): The category of the market (e.g., "linear", "spot").
            symbol (str): The trading pair (e.g., BTCUSDT).
            order_id (str, optional): The order ID to modify. Either order_id or order_link_id is required.
            order_link_id (str, optional): The user-defined order link ID. Either order_id or order_link_id is required.
            stop_loss (float): The new stop-loss price.

        Returns:
            dict: The response from the Bybit API.
        """
        try:
            if not stop_loss:
                raise ValueError("Stop-loss price is required to amend the order.")

            logger.info(f"Amending stop-loss for orderId {order_id} {symbol} to {stop_loss} (category: {category})")
            response = self.session.amend_order(
                category=category,
                symbol=symbol,
                orderId=order_id,
                orderLinkId=order_link_id,
                stopLoss=str(stop_loss)
            )
            if response.get("retCode") == 0:
                logger.info(f"✅ Stop-loss amended successfully: {response}")
                return response
            else:
                error_message = response.get("retMsg", "Unknown error")
                logger.error(f"❌ Failed to amend stop-loss: {error_message}")
                raise ValueError(f"Error amending stop-loss: {error_message}")
        except Exception as e:
            logger.error(f"❌ Error amending stop-loss for {symbol}: {e}")
            raise

    def place_order(self, category, symbol, side, order_type, qty, stop_loss=None):
        """
        Places an order on Bybit.

        Args:
            category (str): The category of the market (e.g., "linear", "spot").
            symbol (str): The trading pair (e.g., BTCUSDT).
            side (str): The side of the order ("Buy" or "Sell").
            order_type (str): The type of the order (e.g., "Market", "Limit").
            qty (float): The quantity of the order.
            stop_loss (float, optional): The stop loss price.

        Returns:
            dict: The response from the Bybit API.
        """
        try:
            logger.info(f"Placing {side} order for {symbol} with qty={qty} and stop_loss={stop_loss}")
            response = self.session.place_order(
                category=category,
                symbol=symbol,
                side=side,
                order_type=order_type,
                qty=str(qty),
                timeInForce="GTC",
            )
            if response.get("retCode") == 0:
                order_id = response['result'].get('orderId')  # Use 'orderId' as returned by the API
                logger.info(f"✅ Order placed successfully: {response}")
                return {"status": "success", "order_id": order_id}
            else:
                error_message = response.get("retMsg", "Unknown error")
                logger.error(f"❌ Failed to place order: {error_message}")
                raise ValueError(f"Error placing order: {error_message}")
        except Exception as e:
            logger.error(f"❌ Error placing order for {symbol}: {e}")
            raise ValueError(f"Error placing order: {e}")
        
    def place_entry_and_tp_orders(self, category, symbol, side, order_type, qty, stop_loss=None, tps=None, tp_sizes=None):
        """
        Places an entry market order and optional batch take-profit orders, and stores them in Redis.
        """
        try:
            # Step 1: Place the entry market order
            qty = round(float(qty), 2)  # Round to 2 decimal places for quantity
            qty = str(qty)  # Convert to string for API compatibility
            logger.info(f"Placing {side} order for {symbol} with qty={qty} and stop_loss={stop_loss}")

            entry_response = self.session.place_order(
                category=category,
                symbol=symbol,
                side=side,
                # isLeverage=1,
                order_type=order_type,
                qty=qty,
                timeInForce="GTC",
                marketUnit="baseCoin",
                stopLoss=stop_loss,  # Set stop loss if provided
            )
            entry_order_id = entry_response['result']['orderId']
            logger.info(f"✅ Entry order placed successfully: {entry_response}")

            # Save entry order to Redis
            entry_order_data = {
                "category": category,
                "symbol": symbol,
                "side": side,
                "order_type": order_type,
                "qty": qty,
                "stop_loss": stop_loss,
                "status": "opened",
                "response": entry_response
            }

            # # Step 2: Place a separate stop-loss order if provided
            # stop_loss_order_id = None
            # if stop_loss:
            #     logger.info(f"Placing stop-loss order for {symbol} at price {stop_loss}")
            #     stop_loss_response = self.session.place_order(
            #         category=category,
            #         symbol=symbol,
            #         side="Sell" if side.lower() == "buy" else "Buy",  # Opposite side for stop-loss
            #         order_type="Limit",
            #         qty=qty,
            #         price=str(stop_loss),
            #         timeInForce="GTC",
            #         marketUnit="baseCoin"
            #     )
            #     stop_loss_order_id = stop_loss_response['result']['orderId']
            #     logger.info(f"✅ Stop-loss order placed successfully: {stop_loss_response}")

            # save_order_to_redis(entry_order_id, entry_order_data)

            # Step 2: Check if TP orders are provided
            if tps and tp_sizes and len(tps) == len(tp_sizes):
                logger.info(f"Placing batch TP orders for {symbol}")
                tp_orders = []
                for tp_price, tp_size in zip(tps, tp_sizes):
                    tp_qty = str(round(float(qty) * (float(tp_size) / 100), 5))
                    tp_orders.append({
                        "symbol": symbol,
                        "side": "Sell" if side.lower() == "buy" else "Buy",  # Opposite side for TP
                        "orderType": "Limit",
                        "qty": tp_qty,
                        # "isLeverage": 1,
                        "price": str(tp_price),
                        "timeInForce": "GTC",
                        "reduceOnly": True,  # Ensure it only reduces the position
                        "marketUnit": "baseCoin",
                    })

                logger.info(f"TP orders: {tp_orders}")

                # Place batch TP orders
                batch_response = self.session.place_batch_order(category=category, request=tp_orders)
                logger.info(f"✅ Batch TP orders placed successfully: {batch_response}")

                # Save TP orders to Redis
                # for tp_order in batch_response.get("result", {}).get("list", []):
                #     tp_order_id = tp_order.get("orderId")
                #     tp_order_data = {
                #         "category": category,
                #         "symbol": symbol,
                #         "side": tp_order["side"],
                #         "order_type": tp_order["orderType"],
                #         "qty": tp_order["qty"],
                #         "price": tp_order["price"],
                #         "status": "opened",
                #         "response": tp_order
                #     }
                    # save_order_to_redis(tp_order_id, tp_order_data)

                return {"entry_response": entry_response, "tp_response": batch_response}

            # If no TP orders, return only the entry response
            return {"entry_response": entry_response}

        except Exception as e:
            logger.error(f"❌ Error placing entry and TP orders: {e}")
            raise

    def cancel_all_orders(self, symbol, category="linear"):
        """
        Cancels all open orders for a specific symbol and category.
        
        Args:
            symbol (str): The trading pair (e.g., BTCUSDT).
            category (str): The category of the market (e.g., "linear", "spot").
        
        Returns:
            dict: The response from the Bybit API.
        """
        try:
            logger.info(f"Canceling all open orders for {symbol} in category {category}...")
            response = self.session.cancel_all_orders(
                category=category,
                symbol=symbol
            )
            if response.get("retCode") == 0:
                logger.info(f"✅ Successfully canceled all orders for {symbol}: {response}")
            else:
                logger.error(f"❌ Failed to cancel orders for {symbol}: {response.get('retMsg', 'Unknown error')}")
            return response
        except Exception as e:
            logger.error(f"❌ Error canceling orders for {symbol}: {e}")
            raise


    def get_position_info(self, symbol, category="linear"):
        """
        Fetches the open position information for a specific symbol.

        Args:
            symbol (str): The trading pair (e.g., BTCUSDT).
            category (str): The category of the market (e.g., "linear", "spot").

        Returns:
            dict: A dictionary containing position details, or an empty dictionary if no position is found.
        """
        try:
            logger.info(f"Fetching position info for {symbol} in category {category}...")
            response = self.session.get_positions(
                category=category,
                symbol=symbol
            )
            if response.get("retCode") == 0:
                positions = response.get("result", {}).get("list", [])
                if positions:
                    # Assuming the first position in the list is the relevant one
                    position = positions[0]
                    logger.info(f"✅ Position info for {symbol}: {position}")
                    return position
                else:
                    logger.info(f"ℹ️ No open position found for {symbol}.")
                    return {}
            else:
                logger.error(f"❌ Failed to fetch position info for {symbol}: {response.get('retMsg', 'Unknown error')}")
                return {}
        except Exception as e:
            logger.error(f"❌ Error fetching position info for {symbol}: {e}")
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