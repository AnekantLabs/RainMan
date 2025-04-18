
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

    def place_order(self, category, market_pair, side, order_type, amount):
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
            )
            print(f"Order placed successfully: {response}")
            return {"status": "success", "order_id": response['result']['order_id']}
        except Exception as e:
            raise ValueError(f"Error placing order:{e} Stack trace: {e.__traceback__}")
        
        # Example API call to place an order
        
    # function to fetch the UID of the main account
    def main_acc_uid(self):
        """
        Fetches the UID of the main account.
        """
        try:
            response = self.session.get_uid_wallet_type(accountType="UNIFIED")
            main_uid = response.get("result", {}).get("accounts", [{}])[0].get("uid")
            return main_uid
        except Exception as e:
            print(f"❌ Error fetching main UID: {e}")
            return None
        
    # function to fetch the UID of the sub account
    def sub_acc_uid(self, username):
        """
        Fetches the UID of the sub account.
        """
        try:
            response = self.session.get_sub_uid_list()
            print(f"Sub account list: {response}")
            sub_accounts = response.get("result", {}).get("subMembers", [{}])
            if not sub_accounts:
                print("❌ No sub accounts found.")
                return None
            for account in sub_accounts:
                if account.get("username") == username:
                    return account.get("uid")
            return None
        except Exception as e:
            print(f"❌ Error fetching sub account UID: {e}")
            return None
    