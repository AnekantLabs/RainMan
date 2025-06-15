import asyncio
from decimal import Decimal
from typing import Dict, List, Literal, Optional

from nautilus_trader.adapters.bybit.common.enums import BybitProductType
from nautilus_trader.adapters.bybit.config import BybitDataClientConfig
from nautilus_trader.adapters.bybit.factories import BybitLiveDataClientFactory
from nautilus_trader.adapters.sandbox.config import SandboxExecutionClientConfig
from nautilus_trader.adapters.sandbox.factory import SandboxLiveExecClientFactory
from nautilus_trader.config import InstrumentProviderConfig, LoggingConfig, StrategyConfig
from nautilus_trader.core.nautilus_pyo3 import ClientOrderId
from nautilus_trader.live.config import TradingNodeConfig
from nautilus_trader.live.node import TradingNode
from nautilus_trader.model.data import Bar, BarType, TradeTick
from nautilus_trader.model.enums import OrderSide, PositionSide
from nautilus_trader.model.events import OrderFilled
from nautilus_trader.model.identifiers import InstrumentId, TraderId
from nautilus_trader.model.instruments import Instrument
from nautilus_trader.model.objects import Price, Quantity
from nautilus_trader.model.orders import LimitOrder, MarketOrder, StopMarketOrder
from nautilus_trader.model.position import Position
from nautilus_trader.trading.strategy import Strategy
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model import Money
from nautilus_trader.model.orders.base import Order
from nautilus_trader.model.enums import PriceType
from nautilus_trader.model.enums import OrderStatus

class PyramidPositionConfig(StrategyConfig, frozen=True, kw_only=True):
    """
    Configuration for the PyramidPosition strategy.
    
    Attributes
    ----------
    instrument_id : InstrumentId
        The instrument ID to trade.
    bar_type : BarType
        The bar type for data subscription.
    strategy_mode : Literal["Automatic", "Manual"]
        The strategy execution mode.
    initial_position_size : Decimal
        The initial position size for automatic mode.
    trade_size : Decimal
        The trade size for manual orders.
    stop_loss_type : Literal["fixed_price", "percentage"]
        The type of stop-loss calculation.
    stop_loss_value : Decimal
        The stop-loss value (price or percentage).
    stop_loss_order_type : Literal["MARKET"]
        The order type for stop-loss orders.
    take_profit_enabled : bool
        Whether take-profit orders are enabled.
    take_profit_type : Literal["fixed_price", "percentage"]
        The type of take-profit calculation.
    take_profit_value : Decimal
        The take-profit value (price or percentage).
    take_profit_order_type : Literal["LIMIT", "MARKET"]
        The order type for take-profit orders.
    grid_count : int
        The number of grid levels.
    price_range : Decimal
        The total price range for the grid.
    reserve_amount : Decimal
        The amount to keep as reserve.
    position_distribution_type : Literal["static", "linear", "exponential"]
        The type of position size distribution.
    distribution_factor : Decimal
        The factor controlling position size growth rate.
    """
    
    # Instrument Details
    instrument_id: InstrumentId
    bar_type: BarType
    
    # Strategy Mode
    strategy_mode: Literal["Automatic", "Manual"]
    trade_size: Decimal = Decimal("0.01")

    # Exit Configuration
    stop_loss_type: Literal["fixed_price", "percentage"]
    stop_loss_value: Decimal
    stop_loss_order_type: Literal["MARKET"]
    take_profit_enabled: bool
    take_profit_type: Literal["fixed_price", "percentage"]
    take_profit_value: Decimal
    take_profit_order_type: Literal["LIMIT", "MARKET"]
    
    # Grid Configuration
    grid_count: int = 100
    price_range: Decimal = Decimal("5000.0")
    
    # Capital Management
    reserve_amount: Decimal = Decimal("10000.0")
    position_distribution_type: Literal["static", "linear", "exponential"]
    distribution_factor: Decimal = Decimal("1.5")


class PyramidPosition(Strategy):
    """
    A trading strategy that implements a pyramiding position approach.
    
    This strategy manages positions with automatic stop-loss and take-profit orders,
    and implements a grid-based re-entry strategy when stop-loss is triggered.
    
    Attributes
    ----------
    instrument : Instrument | None
        The trading instrument.
    active_grid_orders : Dict[ClientOrderId, LimitOrder]
        Dictionary of active grid orders.
    stop_loss_order : StopMarketOrder | None
        The current stop-loss order.
    take_profit_order : LimitOrder | None
        The current take-profit order.
    """
    
    def __init__(self, config: PyramidPositionConfig) -> None:
        """
        Initialize the strategy.
        
        Parameters
        ----------
        config : PyramidPositionConfig
            The strategy configuration.
        """
        super().__init__(config)
        
        # Initialize state variables
        self.instrument: Optional[Instrument] = None
        self.grid_initialized = False
        self.active_grid_orders: Dict[ClientOrderId, LimitOrder] = {}
        self.filled_grid_orders: Dict[ClientOrderId, Order] = {}
        self.buy_order: Optional[MarketOrder] = None
        self.stop_loss_order: Optional[StopMarketOrder] = None
        self.take_profit_order: Optional[LimitOrder] = None
        self.strategy_initialized = False

    def on_start(self) -> None:
        """Initialize strategy on start."""
        # Get instrument
        self.instrument = self.cache.instrument(self.config.instrument_id)
        if self.instrument is None:
            self.log.error(f"Could not find instrument {self.config.instrument_id}")
            self.stop()
            return
            
        # Subscribe to data
        self.subscribe_bars(self.config.bar_type)
        self.subscribe_trade_ticks(self.config.instrument_id)
        
        self.log.info(f"Strategy started for {self.config.instrument_id}")

    def create_and_submit_order(self, order_type: str, **kwargs) -> Optional[Order]:
        order = None
        order_type = order_type.lower()
        
        if order_type == "market":
            order = self.order_factory.market(**kwargs)
        elif order_type == "limit":
            order = self.order_factory.limit(**kwargs)
        elif order_type == "stop_market":
            order = self.order_factory.stop_market(**kwargs)
        else:
            self.log.error(f"Unknown order type: {order_type}")
            return None

        max_attempts = 3
        attempt_delay = 1  # seconds delay between attempts
        for attempt in range(1, max_attempts + 1):
            try:
                self.submit_order(order)
                self.log.info(f"Submitted {order_type} order: {order} (attempt {attempt})")
                return order
            except Exception as e:
                self.log.error(f"Order submission failed on attempt {attempt}/{max_attempts}: {e}")
                if attempt < max_attempts:
                    import time
                    time.sleep(attempt_delay)
                else:
                    self.log.error("Max attempts exceeded for order submission")
                    return None
    
    def _initialize_automatic_position(self) -> None:
        """Initialize an automatic position based on configuration."""
        positions = self.cache.positions_open(
            instrument_id=self.config.instrument_id,
            side=PositionSide.LONG
        )

        if  len(positions) > 0:
            self.log.warning("Already have an open Buy Position")
            return
        
        order = self.create_and_submit_order(
            order_type="market",
            instrument_id=self.config.instrument_id,
            order_side=OrderSide.BUY,
            quantity=self.instrument.make_qty(self.config.trade_size),
            # post_only=True,
        )
        self.buy_order = order
        self.strategy_initialized = True
        self.log.info(f"Submitted initial position order: {order}")

    def _initialize_manual_position(self) -> None:
        """Initialize the strategy for manual trading."""
        pass


    def on_trade_tick(self, tick: TradeTick) -> None:
        """
        Handle trade tick events and manage positions.
        
        Parameters
        ----------
        tick : TradeTick
            The trade tick received.
        """

        if self.config.strategy_mode == "Automatic" and self.strategy_initialized == False:
            self._initialize_automatic_position()
        else:
            self._initialize_manual_position()


    def on_bar(self, bar: Bar) -> None:
        """
        Actions to be performed when the strategy receives a bar.

        Parameters
        ----------
        bar : Bar
            The bar received.
        """
        # This method can be implemented for bar-based logic
        pass

    def get_available_capital(self) -> Optional[Money]:
        """
        Get available capital through portfolio.
        
        Returns
        -------
        Optional[Decimal]
            The available balance or None if account not found.
        """
        account = self.portfolio.account(Venue("BYBIT"))
        if account:
            quote_currency = self.instrument.quote_currency
            available_balance = account.balance_free(quote_currency)
            total_balance = account.balance_total(quote_currency)
            locked_balance = account.balance_locked(quote_currency)
            
            self.log.info(
                f"Account Balances ({quote_currency}): "
                f"Available: {available_balance}, "
                f"Total: {total_balance}, "
                f"Locked: {locked_balance}"
            )
            return available_balance
        
        self.log.warning("Account not found: BYBIT")
        return None
 
    def setup_limit_position_orders(self, event) -> None:
        """
        Setup stop-loss and take-profit orders for an existing position.
        
        Parameters
        ----------
        position : Position
            The position to set orders for.
        """

        # Get positions using cache
        order = self.cache.order(event.client_order_id)

        self.log.info(f"Order Details: {order.quantity} @ {order.avg_px}")
        if self.instrument is None:
            self.log.error("Cannot set up orders - instrument not initialized")
            return
        
        # Calculate stop-loss price
        if self.config.stop_loss_type == "percentage":
            avg_px_open = Decimal(str(order.avg_px))
            stop_price = Price(
                avg_px_open * (Decimal("1") - self.config.stop_loss_value),
                precision=self.instrument.price_precision
            )
        else:
            stop_price = Price(
                self.config.stop_loss_value,
                precision=self.instrument.price_precision
            )
            
        # Place stop-loss order
        self.stop_loss_order = self.create_and_submit_order(
            order_type="stop_market",
            instrument_id=self.config.instrument_id,
            order_side=OrderSide.SELL,
            quantity=self.instrument.make_qty(Decimal(str(order.quantity))),
            trigger_price=stop_price,
        )
        
        self.log.info(f"Submitted stop-loss order at {stop_price}: {self.stop_loss_order}")
        
        # Setup take-profit if enabled
        if self.config.take_profit_enabled:
            if self.config.take_profit_type == "percentage":
                avg_px_open = Decimal(str(order.avg_px))
                take_profit_price = Price(
                    avg_px_open * (Decimal("1") + self.config.take_profit_value),
                    precision=self.instrument.price_precision
                )
            else:
                take_profit_price = Price(
                    self.config.take_profit_value,
                    precision=self.instrument.price_precision
                )
                
            # Determine order type for take-profit and place order with helper function
            if self.config.take_profit_order_type == "LIMIT":
                self.take_profit_order = self.create_and_submit_order(
                    order_type="limit",
                    instrument_id=self.config.instrument_id,
                    order_side=OrderSide.SELL,
                    quantity=self.instrument.make_qty(Decimal(str(order.quantity))),
                    price=take_profit_price,
                )
            else:  # MARKET
                self.take_profit_order = self.create_and_submit_order(
                    order_type="stop_market",
                    instrument_id=self.config.instrument_id,
                    order_side=OrderSide.SELL,
                    quantity=self.instrument.make_qty(Decimal(str(order.quantity))),
                    trigger_price=take_profit_price,
                )       
            self.log.info(f"Submitted take-profit order at {take_profit_price}: {self.take_profit_order}")
            
    def create_grid_orders(self, start_price: Decimal) -> None:
        """
        Create grid of buy orders after stop-loss is triggered.
        
        Parameters
        ----------
        start_price : Decimal
            The starting price for the grid (usually the stop-loss execution price).
        """
        
        available_capital = self.get_available_capital()
        available_capital = available_capital.as_decimal()
        if available_capital is None or available_capital <= self.config.reserve_amount:
            self.log.error("Insufficient capital to create grid orders")
            self.stop()
            return
            
        tradeable_capital = available_capital - self.config.reserve_amount
        grid_spacing = self.config.price_range / Decimal(str(self.config.grid_count))
        
        # Calculate position sizes based on distribution type
        sizes = self.calculate_position_sizes(tradeable_capital)
        
        # Create grid orders
        for i in range(self.config.grid_count):
            price_level = start_price - (i + 1) * grid_spacing
            size = sizes[i]
            
            # Skip if size is too small
            if size < self.instrument.min_quantity:
                continue
                
            # Create a limit order at this price level
            price = Price(price_level, precision=self.instrument.price_precision)
            quantity = self.instrument.make_qty(size)
            
            order = self.create_and_submit_order(
                order_type="limit",
                instrument_id=self.config.instrument_id,
                order_side=OrderSide.BUY,
                quantity=quantity,
                price=price,
            )
            self.active_grid_orders[order.client_order_id] = order
            
            self.log.info(f"Created grid order {i+1}/{self.config.grid_count}: {size} @ {price}")
            
        self.log.info(f"Created {len(self.active_grid_orders)} grid orders")
        self.log.info(f"Grid Orders: {self.active_grid_orders}")


    def calculate_position_sizes(self, available_capital: Decimal) -> List[Decimal]:
        """
        Calculate position sizes based on distribution type.

        Parameters
        ----------
        available_capital : Decimal
            The available capital for grid orders.

        Returns
        -------
        List[Decimal]
            List of position sizes for each grid level.
        """
        base_asset_price = self.cache.price(
            instrument_id=self.config.instrument_id,
            price_type=PriceType.MID
        )

        if self.config.position_distribution_type == "static":
            # Equal distribution
            size_quote_asset = available_capital / Decimal(str(self.config.grid_count))
            size_base_asset = size_quote_asset / base_asset_price  
            return [size_base_asset] * self.config.grid_count

        elif self.config.position_distribution_type == "linear":
            # Linear distribution
            total_weight = Decimal(str(self.config.grid_count * (self.config.grid_count + 1) / 2))
            size_quote_asset = available_capital / total_weight
            base_size = size_quote_asset / base_asset_price  
            return [base_size * Decimal(str(i + 1)) for i in range(self.config.grid_count)]

        else:  # Exponential Distribution
            growth_rate = (self.config.distribution_factor - Decimal("1")) / Decimal("10")
            adjusted_growth_rate = growth_rate * (Decimal("100") / Decimal(str(self.config.grid_count)))

            # Generate raw sizes using the exponential formula
            raw_sizes = [
                Decimal("1") * (Decimal("1") + adjusted_growth_rate) ** Decimal(str(i))
                for i in range(self.config.grid_count)
            ]

            # Normalize the sizes to match the available capital
            total_weight = sum(raw_sizes)
            quote_asset_sizes = [size * available_capital / total_weight for size in raw_sizes]

            # Convert to base asset sizes
            base_asset_sizes = [size / base_asset_price for size in quote_asset_sizes]

            return base_asset_sizes



    def on_order_filled(self, event: OrderFilled) -> None:
        """
        Handle order fill events.
        
        Parameters
        ----------
        event : OrderFilled
            The order filled event.
        """
        self.log.info(f"Order filled: {event}")
        order = self.cache.order(event.client_order_id)
        if order is None:
            self.log.error(f"Order not found for event: {event}")
            return
        
        # # Check if the order is completely filled
        # if order.filled_qty < order.quantity:
        #     self.log.info(f"Order {order.client_order_id} is partially filled: "
        #                 f"{order.filled_qty}/{order.quantity}. Waiting for complete fill.")
        #     return

        if self.stop_loss_order is None and self.take_profit_order is None and self.buy_order.status == OrderStatus.FILLED and event.order_side == OrderSide.BUY:
            self.setup_limit_position_orders(order)

        # Handle stop-loss fill
        if (self.stop_loss_order is not None and self.stop_loss_order.status == OrderStatus.FILLED and
            event.client_order_id == self.stop_loss_order.client_order_id):
            self.handle_stop_loss_fill(self.stop_loss_order)

        # Handle take-profit fill
        elif (self.take_profit_order is not None and self.take_profit_order.status == OrderStatus.FILLED and
              event.client_order_id == self.take_profit_order.client_order_id):
            self.handle_take_profit_fill(self.take_profit_order)
            
        # Handle grid order fill
        elif event.client_order_id in self.active_grid_orders and order.status == OrderStatus.FILLED:
            self.handle_grid_order_fill(order)

    def handle_stop_loss_fill(self, event: Order) -> None:
        """
        Handle stop-loss order fill.
        
        Parameters
        ----------
        event : OrderFilled
            The order filled event.
        """
        self.log.info(f"Stop-loss triggered at {event.avg_px}")
        
        # Update strategy state
        self.stop_loss_order = None

        if not self.grid_initialized:
            # Create grid orders
            self.create_grid_orders(Decimal(str(event.avg_px)))
            self.grid_initialized = True
        else:
            # stop the strategy
            self.stop()  

        
    def handle_take_profit_fill(self, event: Order) -> None:
        """
        Handle take-profit order fill.
        
        Parameters
        ----------
        event : OrderFilled
            The order filled event.
        """
        self.log.info(f"Take-profit triggered at {event.avg_px}")
        
        # Cancel all remaining grid orders
        self.cancel_all_orders(self.config.instrument_id)
        
        # Clean up and prepare for termination
        self.active_grid_orders.clear()
        self.take_profit_order = None
        
        # Log final performance
        profit = self.portfolio.realized_pnl(self.config.instrument_id)
        self.log.info(f"Strategy completed with profit: {profit}")
        
        # Stop the strategy
        self.stop()

    def calculate_average_price(self, positions: List[Position]) -> Decimal:
        """
        Calculate weighted average price from all positions.
        
        Parameters
        ----------
        positions : List[Position]
            List of positions from cache.
        
        Returns
        -------
        Decimal
            Weighted average entry price across all positions.
        """
        if not positions:
            return Decimal("0")
        
        total_value = Decimal("0")
        total_quantity = Decimal("0")
        
        for position in positions:
            # Convert position price to Decimal to maintain precision
            position_price = Decimal(str(position.avg_px_open))
            position_qty = position.quantity
            
            self.log.info(
                f"Position Details: "
                f"Entry Price: {position_price}, "
                f"Quantity: {position_qty}, "
                f"Side: {position.side}"
            )
            
            total_value += position_price * position_qty
            total_quantity += position_qty
        
        # Calculate weighted average
        if total_quantity > Decimal("0"):
            weighted_avg = total_value / total_quantity
            self.log.info(f"Calculated Weighted Average Price: {weighted_avg}")
            return weighted_avg
        
        return Decimal("0")
  
    def handle_grid_order_fill(self, event: Order) -> None:
        """
        Handle grid order fill.
        
        Parameters
        ----------
        event : OrderFilled
            The order filled event.
        """
        if self.instrument is None:
            self.log.error("Cannot handle grid order fill - instrument not initialized")
            return
            
        self.log.info(f"Grid order filled at {event.avg_px}")
        self.filled_grid_orders[event.client_order_id] = event
        # Remove the filled order from active grid orders
        self.active_grid_orders.pop(event.client_order_id, None)
        
        # Get current position
        positions = self.cache.positions_open(
            instrument_id=self.config.instrument_id,
            side=PositionSide.LONG
        )
        
        if len(positions) == 0:
            self.log.error("No position found after grid order fill")
            return
            
        # Since oms is NETTED position should hold the avg_px
        # Calculate new average price
        # grid_avg_price = self.calculate_average_price(positions)
        grid_avg_price = positions[0].avg_px_open
        self.log.info(f"Grid Average Price: {grid_avg_price}")
        total_quantity = positions[0].quantity

        # Update stop-loss based on new average entry
        if self.config.stop_loss_type == "percentage":
            new_stop_price = Price(
                grid_avg_price * (Decimal("1") - self.config.stop_loss_value),
                precision=self.instrument.price_precision
            )
            
            # Cancel existing stop-loss order
            if self.stop_loss_order:
                self.cancel_order(self.stop_loss_order)
                
            # Create new stop-loss order
            self.stop_loss_order = self.create_and_submit_order(
                order_type="stop_market",
                instrument_id=self.config.instrument_id,
                order_side=OrderSide.SELL,
                quantity=total_quantity,
                trigger_price=new_stop_price,
            )
            
            self.log.info(
                f"Updated Stop-Loss: "
                f"New Average Entry: {grid_avg_price}, "
                f"New Stop Price: {new_stop_price}, "
                f"New Position Size: {total_quantity}"
            )
        
        # Update take-profit if using percentage
        if (self.config.take_profit_enabled and 
            self.config.take_profit_type == "percentage"):
            new_take_profit_price = Price(
                grid_avg_price * (Decimal("1") + self.config.take_profit_value),
                precision=self.instrument.price_precision
            )
            
            # Cancel existing take-profit order
            if self.take_profit_order:
                self.cancel_order(self.take_profit_order)

            # Create new take-profit order with updated quantity
            if self.config.take_profit_order_type == "LIMIT":
                self.take_profit_order = self.create_and_submit_order(
                    order_type="limit",
                    instrument_id=self.config.instrument_id,
                    order_side=OrderSide.SELL,
                    quantity=total_quantity,
                    price=new_take_profit_price,
                )
            else:  # MARKET
                self.take_profit_order = self.create_and_submit_order(
                    order_type="stop_market",
                    instrument_id=self.config.instrument_id,
                    order_side=OrderSide.SELL,
                    quantity=total_quantity,
                    trigger_price=new_take_profit_price,
                )
            
            self.log.info(
                f"Updated Take-Profit: "
                f"New Take-Profit Price: {new_take_profit_price}, "
                f"New Position Size: {total_quantity}"
            )
            
    def on_stop(self) -> None:
        """Handle strategy stop, close open positions, and cleanup."""
        # Cancel all pending orders
        self.cancel_all_orders(self.config.instrument_id)
        
        # Retrieve open positions (netted OMS typically aggregates to one position)
        positions = self.cache.positions_open(
            instrument_id=self.config.instrument_id,
            side=PositionSide.LONG
        )
        
        if positions:
            self.log.info(f"Strategy stopping with {len(positions)} positions remaining")
            # Close each open position using a market sell order
            for pos in positions:
                self.log.info(f"Closing position: {pos}")
                close_order = self.create_and_submit_order(
                    order_type="market",
                    instrument_id=self.config.instrument_id,
                    order_side=OrderSide.SELL,
                    quantity=self.instrument.make_qty(pos.quantity),
                )
                self.log.info(f"Submitted closing order: {close_order}")
        else:
            self.log.info("Strategy stopped with no positions remaining")
        
        # Cleanup subscriptions
        self.unsubscribe_bars(self.config.bar_type)
        self.unsubscribe_trade_ticks(self.config.instrument_id)
        
        self.log.info("Strategy stopped and resources cleaned up")

async def main():
    """
    Run the strategy in a sandbox environment for the Bybit venue.
    """
    # Configure the instrument provider
    instrument_provider_config = InstrumentProviderConfig(load_all=True)

    # Set up the execution clients
    venues = ["BYBIT"]
    exec_clients = {}
    
    for venue in venues:
        exec_clients[venue] = SandboxExecutionClientConfig(
            venue=venue,
            starting_balances=["20_000 USDT", "10 ETH"],
            instrument_provider=instrument_provider_config,
            account_type="MARGIN",
            oms_type="NETTING",
        )

    # Configure the trading node
    config_node = TradingNodeConfig(
        trader_id=TraderId("TESTER-001"),
        logging=LoggingConfig(
            log_level="INFO",
            log_colors=True,
            use_pyo3=True,
        ),
        data_clients={
            "BYBIT": BybitDataClientConfig( 
                api_key='DPDFtZgymmpYX2ahPg',
                api_secret='Ag5Nci0JxwESBi8JkcopHHDFmaQ7fR9rdyUf',
                instrument_provider=instrument_provider_config,
                product_types=[BybitProductType.LINEAR],
                testnet=False,
            ),
        },
        exec_clients=exec_clients,
        timeout_connection=30.0,
        timeout_reconciliation=10.0,
        timeout_portfolio=10.0,
        timeout_disconnection=10.0,
        timeout_post_stop=5.0,
    )

    # Create the trading node
    node = TradingNode(config=config_node)

    # Configure the strategy
    strat_config = PyramidPositionConfig(
        # Instrument Details
        instrument_id=InstrumentId.from_str("ETHUSDT-LINEAR.BYBIT"),
        bar_type=BarType.from_str("ETHUSDT-LINEAR.BYBIT-1-MINUTE-LAST-EXTERNAL"),
        
        # Strategy Mode Configuration
        strategy_mode="Automatic",

        trade_size=Decimal("0.01"),

        # Stop Loss Configuration
        stop_loss_type="percentage",
        stop_loss_value=Decimal("0.00035"),
        stop_loss_order_type="MARKET",
        
        # Take Profit Configuration
        take_profit_enabled=True,  
        take_profit_type="fixed_price",
        take_profit_value=Decimal("136000.0"),
        take_profit_order_type="LIMIT",
        
        # Grid Configuration
        grid_count=3,
        price_range=Decimal("0.01"),
        
        # Capital Management
        reserve_amount=Decimal("10000.0"),
        position_distribution_type="static",
        distribution_factor=Decimal("2.0"),
    )
    
    # Create the strategy instance
    strategy = PyramidPosition(config=strat_config)

    # Add the strategy to the trader
    node.trader.add_strategy(strategy)

    # Register client factories with the node
    for data_client in config_node.data_clients:
        node.add_data_client_factory(data_client, BybitLiveDataClientFactory)

    for exec_client in config_node.exec_clients:
        node.add_exec_client_factory(exec_client, SandboxLiveExecClientFactory)

    # Build the node
    node.build()

    try:
        # Run the node
        await node.run_async()
    finally:
        # Cleanup
        await node.stop_async()
        await asyncio.sleep(1)
        node.dispose()


if __name__ == "__main__":
    asyncio.run(main())