import uuid
from pybit.unified_trading import HTTP, WebSocket
from redis_client import save_order_to_redis
from logging_event import get_logger
logger = get_logger()
# Set up logging (add this near the top of your file)
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

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
        self.ws = WebSocket(
            testnet=self.testnet,
            channel_type="private",
            api_key=self.api_key,
            api_secret=self.api_secret
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

    def set_leverage(self, leverage, symbol, category="linear"):
        """
        Sets the leverage for a specific symbol.
        
        Args:
            leverage (int/str): The leverage value to set (must be within allowed range)
            symbol (str): The trading pair (e.g., BTCUSDT)
            category (str): The category of the market (e.g., "linear", "inverse")
            
        Returns:
            dict: The response from the Bybit API
        """
        try:
            leverage_str = str(leverage)
            logger.info(f"Setting leverage for {symbol} to {leverage_str}...")
            
            response = self.session.set_leverage(
                category=category,
                symbol=symbol.upper(),
                buyLeverage=leverage_str,
                sellLeverage=leverage_str
            )
            print(response," Leverageee response")
            if response.get("retCode") == 0:
                logger.info(f"✅ Successfully set leverage for {symbol} to {leverage_str}")
                return {"status": "success", "message": f"Leverage set to {leverage_str}"}
            else:
                error_message = response.get("retMsg", "Unknown error")
                logger.error(f"❌ Failed to set leverage: {error_message}")
                raise ValueError(f"Error setting leverage: {error_message}")
        except Exception as e:
            logger.error(f"❌ Error setting leverage for {symbol}: {e}")
            raise ValueError(f"Error setting leverage: {e}")

    def set_margin_mode(self, margin_type, symbol, category="linear"):
        """
        Switches between cross and isolated margin mode for a specific symbol.
        
        Args:
            margin_type (str): "cross" or "isolated"
            symbol (str): The trading pair (e.g., BTCUSDT)
            category (str): The category of the market (e.g., "linear", "inverse")
            
        Returns:
            dict: The response from the Bybit API
        """
        try:
            # Convert margin_type string to integer (0 for cross, 1 for isolated)
            if margin_type.lower() not in ["cross", "isolated"]:
                raise ValueError("Margin type must be either 'cross' or 'isolated'")
                
            trade_mode = 0 if margin_type.lower() == "cross" else 1
            
            # Get current leverage to maintain it when switching margin modes
            position_info = self.get_position_info(symbol, category)
            leverage = position_info.get("leverage", "10")  # Default to 10 if not found
            
            logger.info(f"Setting {symbol} margin mode to {margin_type} (tradeMode={trade_mode})...")
            
            response = self.session.switch_margin_mode(
                category=category,
                symbol=symbol.upper(),
                tradeMode=trade_mode,
                buyLeverage=leverage,
                sellLeverage=leverage
            )
            
            if response.get("retCode") == 0:
                logger.info(f"✅ Successfully set margin mode for {symbol} to {margin_type}")
                return {"status": "success", "message": f"Margin mode set to {margin_type}"}
            else:
                error_message = response.get("retMsg", "Unknown error")
                logger.error(f"❌ Failed to set margin mode: {error_message}")
                raise ValueError(f"Error setting margin mode: {error_message}")
        except Exception as e:
            logger.error(f"❌ Error setting margin mode for {symbol}: {e}")
            raise ValueError(f"Error setting margin mode: {e}")

    def get_current_price(self, symbol):
        """
        Gets the current price for a specific symbol.
        
        Args:
            symbol (str): The trading pair (e.g., BTCUSDT)
            
        Returns:
            float: The current price of the symbol
        """
        try:
            logger.info(f"Getting current price for {symbol}...")
            response = self.session.get_tickers(
                category="linear",
                symbol=symbol.upper()
            )
            
            if response.get("retCode") == 0:
                price_data = response.get("result", {}).get("list", [])
                if price_data:
                    # Get the last price from the first result
                    current_price = float(price_data[0].get("lastPrice", 0))
                    logger.info(f"Current price for {symbol}: {current_price}")
                    return current_price
                else:
                    logger.error(f"❌ No price data found for {symbol}")
                    return 0
            else:
                error_message = response.get("retMsg", "Unknown error")
                logger.error(f"❌ Failed to get current price: {error_message}")
                return 0
        except Exception as e:
            logger.error(f"❌ Error getting current price for {symbol}: {e}")
            return 0

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

    def place_order(self, category, symbol, side, order_type, qty, stop_loss=None,reduce_only=False):
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
                reduceOnly=reduce_only,  # Set reduceOnly if specified
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

    def cancel_all_orders(self, symbol, category="linear", settleCoin="USDT"):
        """
        Cancels all open orders for a specific symbol or across all symbols in a category.

        Args:
            symbol (str | None): Trading pair (e.g., BTCUSDT) or None to cancel all.
            category (str): Market category (e.g., "linear", "spot").
            settleCoin (str): Coin used to settle trades (e.g., "USDT").

        Returns:
            dict: Response from the Bybit API.
        """
        settle_coin = settleCoin.upper()

        if not symbol or not symbol.strip():
            symbol = None
            logger.info(f"⚠️ No symbol provided. Will cancel *all* open orders in category '{category}' and settleCoin '{settle_coin}'")
        else:
            logger.info(f"🔁 Canceling all open orders for symbol '{symbol}' in category '{category}' and settleCoin '{settle_coin}'")

        try:
            response = self.session.cancel_all_orders(
                category=category,
                symbol=symbol,
                settle_coin=settle_coin
            )

            if response.get("retCode") == 0:
                action_scope = f"symbol '{symbol}'" if symbol else "all symbols"
                logger.info(f"✅ Successfully canceled open orders for {action_scope}: {response}")
            else:
                logger.error(f"❌ Failed to cancel orders for symbol '{symbol or 'ALL'}': {response.get('retMsg', 'Unknown error')}")

            return response

        except Exception as e:
            logger.error(f"❌ Exception occurred while canceling orders for symbol '{symbol or 'ALL'}': {e}")
            raise


    def get_position_info(self, symbol, category="linear", settleCoin="USDT"):
        """
        Fetches the open position information for a specific symbol.

        Args:
            symbol (str): The trading pair (e.g., BTCUSDT).
            category (str): The category of the market (e.g., "linear", "spot").

        Returns:
            dict: A dictionary containing position details, or an empty dictionary if no position is found.
        """
        if symbol is None or not symbol.strip():
            symbol = None

        settle_coin = settleCoin.upper()

        try:
            logger.info(f"Fetching position info for {symbol} in category {category}...")
            response = self.session.get_positions(
                category=category,
                symbol=symbol,
                settleCoin=settle_coin
            )
            if response.get("retCode") == 0:
                positions = response.get("result", {}).get("list", [])
                if positions:
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
        
    # def connect_private_orders_ws(self):
        