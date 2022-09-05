from decimal import Decimal
import decimal
from hummingbot.client.config.config_var import ConfigVar
from hummingbot.client.config.config_validators import (
    validate_exchange,
    validate_connector,
    validate_market_trading_pair,
    validate_bool,
    validate_decimal,
    validate_int
)
from hummingbot.client.settings import (
    required_exchanges,
    AllConnectorSettings,
)
from typing import Optional


def maker_trading_pair_prompt():
    exchange = pure_market_making_config_map.get("exchange").value
    example = AllConnectorSettings.get_example_pairs().get(exchange)
    return "Enter the token trading pair you would like to trade on %s%s >>> " \
           % (exchange, f" (e.g. {example})" if example else "")


# strategy specific validators
def validate_exchange_trading_pair(value: str) -> Optional[str]:
    exchange = pure_market_making_config_map.get("exchange").value
    return validate_market_trading_pair(exchange, value)


def order_amount_prompt() -> str:
    trading_pair = pure_market_making_config_map["market"].value
    base_asset, quote_asset = trading_pair.split("-")
    return f"What is the amount of {base_asset} per order? >>> "


def validate_price_source(value: str) -> Optional[str]:
    if value not in {"current_market", "external_market", "custom_api"}:
        return "Invalid price source type."


def on_validate_price_source(value: str):
    if value != "external_market":
        pure_market_making_config_map["price_source_exchange"].value = None
        pure_market_making_config_map["price_source_market"].value = None
        pure_market_making_config_map["take_if_crossed"].value = None
    if value != "custom_api":
        pure_market_making_config_map["price_source_custom_api"].value = None
    else:
        pure_market_making_config_map["price_type"].value = "custom"


def price_source_market_prompt() -> str:
    external_market = pure_market_making_config_map.get(
        "price_source_exchange").value
    return f'Enter the token trading pair on {external_market} >>> '


def validate_price_source_exchange(value: str) -> Optional[str]:
    if value == pure_market_making_config_map.get("exchange").value:
        return "Price source exchange cannot be the same as maker exchange."
    return validate_connector(value)


def on_validated_price_source_exchange(value: str):
    if value is None:
        pure_market_making_config_map["price_source_market"].value = None


def validate_price_source_market(value: str) -> Optional[str]:
    market = pure_market_making_config_map.get("price_source_exchange").value
    return validate_market_trading_pair(market, value)


def validate_price_floor_ceiling(value: str) -> Optional[str]:
    try:
        decimal_value = Decimal(value)
    except Exception:
        return f"{value} is not in decimal format."
    if not (decimal_value == Decimal("-1") or decimal_value > Decimal("0")):
        return "Value must be more than 0 or -1 to disable this feature."


def validate_price_type(value: str) -> Optional[str]:
    error = None
    price_source = pure_market_making_config_map.get("price_source").value
    if price_source != "custom_api":
        valid_values = {"mid_price",
                        "last_price",
                        "last_own_trade_price",
                        "best_bid",
                        "best_ask",
                        "inventory_cost",
                        }
        if value not in valid_values:
            error = "Invalid price type."
    elif value != "custom":
        error = "Invalid price type."
    return error


def on_validated_price_type(value: str):
    if value == 'inventory_cost':
        pure_market_making_config_map["inventory_price"].value = None


def exchange_on_validated(value: str):
    required_exchanges.add(value)


def validate_decimal_list(value: str) -> Optional[str]:
    decimal_list = list(value.split(","))
    for number in decimal_list:
        try:
            validate_result = validate_decimal(
                Decimal(number), 0, 100, inclusive=False)
        except decimal.InvalidOperation:
            return "Please enter valid decimal numbers"
        if validate_result is not None:
            return validate_result


pure_market_making_config_map = {
    "strategy":
        ConfigVar(key="strategy",
                  prompt=None,
                  default="pure_market_making"),
    "exchange":
        ConfigVar(key="exchange",
                  prompt="Enter your maker spot connector >>> ",
                  validator=validate_exchange,
                  on_validated=exchange_on_validated,
                  prompt_on_new=True),

    "strategy_identifier":
        ConfigVar(key="strategy_identifier",
                  prompt="how do you want to identify this strategy? Format: strategy_exchange_base-quote_type e.g. PMM_kucoin_AVAX-USDT_S2 or XEMM_kucoin-binance_AVAX-USDT-general >>> ",
                  type_str="str",
                  prompt_on_new=True),
    "market":
        ConfigVar(key="market",
                  prompt=maker_trading_pair_prompt,
                  validator=validate_exchange_trading_pair,
                  prompt_on_new=True),
    "bid_spread":
        ConfigVar(key="bid_spread",
                  prompt="How far away from the mid price do you want to place the "
                         "first bid order? (Enter 1 to indicate 1%) >>> ",
                  type_str="decimal",
                  validator=lambda v: validate_decimal(
                      v, 0, 100, inclusive=False),
                  prompt_on_new=True),
    "ask_spread":
        ConfigVar(key="ask_spread",
                  prompt="How far away from the mid price do you want to place the "
                         "first ask order? (Enter 1 to indicate 1%) >>> ",
                  type_str="decimal",
                  validator=lambda v: validate_decimal(
                      v, 0, 100, inclusive=False),
                  prompt_on_new=True),
    "minimum_spread":
        ConfigVar(key="minimum_spread",
                  prompt="At what minimum spread should the bot automatically cancel orders? (Enter 1 for 1%) >>> ",
                  required_if=lambda: False,
                  type_str="decimal",
                  default=Decimal(-100),
                  validator=lambda v: validate_decimal(v, -100, 100, True)),
    "order_refresh_time":
        ConfigVar(key="order_refresh_time",
                  prompt="How often do you want to cancel and replace bids and asks "
                         "(in seconds)? >>> ",
                  type_str="float",
                  validator=lambda v: validate_decimal(v, 0, inclusive=False),
                  prompt_on_new=True),
    "max_order_age":
        ConfigVar(key="max_order_age",
                  prompt="How long do you want to cancel and replace bids and asks "
                         "with the same price (in seconds)? >>> ",
                  type_str="float",
                  default=Decimal("15"),
                  validator=lambda v: validate_decimal(v, 0, inclusive=False)),
    "order_refresh_tolerance_pct":
        ConfigVar(key="order_refresh_tolerance_pct",
                  prompt="Enter the percent change in price needed to refresh orders at each cycle "
                         "(Enter 1 to indicate 1%) >>> ",
                  type_str="decimal",
                  default=Decimal("0"),
                  validator=lambda v: validate_decimal(v, -10, 10, inclusive=True)),
    "order_amount":
        ConfigVar(key="order_amount",
                  prompt=order_amount_prompt,
                  type_str="decimal",
                  validator=lambda v: validate_decimal(
                      v, min_value=Decimal("0"), inclusive=False),
                  prompt_on_new=True),
    "price_ceiling":
        ConfigVar(key="price_ceiling",
                  prompt="Enter the price point above which only sell orders will be placed "
                         "(Enter -1 to deactivate this feature) >>> ",
                  type_str="decimal",
                  default=Decimal("-1"),
                  validator=validate_price_floor_ceiling),
    "price_floor":
        ConfigVar(key="price_floor",
                  prompt="Enter the price below which only buy orders will be placed "
                         "(Enter -1 to deactivate this feature) >>> ",
                  type_str="decimal",
                  default=Decimal("-1"),
                  validator=validate_price_floor_ceiling),
    "moving_price_band_enabled":
        ConfigVar(key="moving_price_band_enabled",
                  prompt="Would you like to enable moving price floor and ceiling? (Yes/No) >>> ",
                  type_str="bool",
                  default=True,
                  validator=validate_bool),
    "price_ceiling_pct":
        ConfigVar(key="price_ceiling_pct",
                  prompt="Enter a percentage to the current price that sets the price ceiling. Above this price, only sell orders will be placed >>> ",
                  type_str="decimal",
                  default=Decimal("1.25"),
                  required_if=lambda: pure_market_making_config_map.get(
                      "moving_price_band_enabled").value,
                  validator=validate_decimal),
    "price_floor_pct":
        ConfigVar(key="price_floor_pct",
                  prompt="Enter a percentage to the current price that sets the price floor. Below this price, only buy orders will be placed >>> ",
                  type_str="decimal",
                  default=Decimal("-1.25"),
                  required_if=lambda: pure_market_making_config_map.get(
                      "moving_price_band_enabled").value,
                  validator=validate_decimal),
    "price_band_refresh_time":
        ConfigVar(key="price_band_refresh_time",
                  prompt="After this amount of time (in seconds), the price bands are reset based on the current price >>> ",
                  type_str="float",
                  default=900,
                  required_if=lambda: pure_market_making_config_map.get(
                      "moving_price_band_enabled").value,
                  validator=validate_decimal),

    "price_band_above_adjustment":
        ConfigVar(key="price_band_above_adjustment",
                  prompt="If price exceeds the upper price band, by what percentage do you want to increase the spread (e.g. 20 for adding 20% to the current spread) >>> ",
                  type_str="decimal",
                  default=Decimal("20"),
                  required_if=lambda: pure_market_making_config_map.get(
                      "moving_price_band_enabled").value,
                  validator=validate_decimal),

    "price_band_below_adjustment":
        ConfigVar(key="price_band_below_adjustment",
                  prompt="If price exceeds the lower price band, by what percentage do you want to increase the spread (e.g. 20 for adding 20% to the current spread) >>> ",
                  type_str="decimal",
                  default=Decimal("20"),
                  required_if=lambda: pure_market_making_config_map.get(
                      "moving_price_band_enabled").value,
                  validator=validate_decimal),

    "ema_timeframe":
        ConfigVar(key="ema_timeframe",
                  prompt="What timeframe do you want to use to compute the ema value for the price ceiling and floor? >>> ",
                  type_str="str",
                  default="30m",
                  required_if=lambda: pure_market_making_config_map.get(
                      "moving_price_band_enabled").value),

    "ema_length":
        ConfigVar(key="ema_length",
                  prompt="What is the length to compute the ema value for the price ceiling and floor? >>> ",
                  type_str="int",
                  default=int(25),
                  required_if=lambda: pure_market_making_config_map.get(
                      "moving_price_band_enabled").value),

    "ema_limit":
        ConfigVar(key="ema_limit",
                  prompt="How much data do you want to fetch to compute the ema value for the price ceiling and floor? >>> ",
                  type_str="int",
                  default=int(30),
                  required_if=lambda: pure_market_making_config_map.get(
                      "moving_price_band_enabled").value),

    "ping_pong_enabled":
        ConfigVar(key="ping_pong_enabled",
                  prompt="Would you like to use the ping pong feature and alternate between buy and sell orders after fills? (Yes/No) >>> ",
                  type_str="bool",
                  default=False,
                  prompt_on_new=True,
                  validator=validate_bool),
    "order_levels":
        ConfigVar(key="order_levels",
                  prompt="How many orders do you want to place on both sides? >>> ",
                  type_str="int",
                  validator=lambda v: validate_int(
                      v, min_value=-1, inclusive=False),
                  default=1),
    "order_level_amount":
        ConfigVar(key="order_level_amount",
                  prompt="How much do you want to increase or decrease the order size for each "
                         "additional order? (decrease < 0 > increase) >>> ",
                  required_if=lambda: pure_market_making_config_map.get(
                      "order_levels").value > 1,
                  type_str="decimal",
                  validator=lambda v: validate_decimal(v),
                  default=0),
    "order_level_spread":
        ConfigVar(key="order_level_spread",
                  prompt="Enter the price increments (as percentage) for subsequent "
                         "orders? (Enter 1 to indicate 1%) >>> ",
                  required_if=lambda: pure_market_making_config_map.get(
                      "order_levels").value > 1,
                  type_str="decimal",
                  validator=lambda v: validate_decimal(
                      v, 0, 100, inclusive=False),
                  default=Decimal("1")),
    "inventory_skew_enabled":
        ConfigVar(key="inventory_skew_enabled",
                  prompt="Would you like to enable inventory skew? (Yes/No) >>> ",
                  type_str="bool",
                  default=False,
                  validator=validate_bool),
    "inventory_target_base_pct":
        ConfigVar(key="inventory_target_base_pct",
                  prompt="What is your target base asset percentage? Enter 50 for 50% >>> ",
                  required_if=lambda: pure_market_making_config_map.get(
                      "inventory_skew_enabled").value,
                  type_str="decimal",
                  validator=lambda v: validate_decimal(v, 0, 100),
                  default=Decimal("50")),
    "inventory_range_multiplier":
        ConfigVar(key="inventory_range_multiplier",
                  prompt="What is your tolerable range of inventory around the target, "
                         "expressed in multiples of your total order size? ",
                  required_if=lambda: pure_market_making_config_map.get(
                      "inventory_skew_enabled").value,
                  type_str="decimal",
                  validator=lambda v: validate_decimal(
                      v, min_value=0, inclusive=False),
                  default=Decimal("1")),
    "inventory_price":
        ConfigVar(key="inventory_price",
                  prompt="What is the price of your base asset inventory? ",
                  type_str="decimal",
                  validator=lambda v: validate_decimal(
                      v, min_value=Decimal("0"), inclusive=True),
                  required_if=lambda: pure_market_making_config_map.get(
                      "price_type").value == "inventory_cost",
                  default=Decimal("1"),
                  ),
    "filled_order_delay":
        ConfigVar(key="filled_order_delay",
                  prompt="How long do you want to wait before placing the next order "
                         "if your order gets filled (in seconds)? >>> ",
                  type_str="float",
                  validator=lambda v: validate_decimal(
                      v, min_value=0, inclusive=False),
                  default=60),

    "volatility_adjustment":
        ConfigVar(key="volatility_adjustment",
                  prompt="Do you want to adjust your bid_ask spread based on volatility? True/False >>> ",
                  type_str="bool",
                  default=False,
                  validator=validate_bool,
                  prompt_on_new=True),

    "volatility_adjustment_multiplier":
        ConfigVar(key="volatility_adjustment_multiplier",
                  prompt="By what factor do you want to adjust for volatility. Generally, volatility ranges between 0.01%-0.07%. A factor of 2 means that the order would be placed 2 times volatility% further from the mid-price >>> ",
                  type_str="decimal",
                  default=Decimal(1),
                  prompt_on_new=True),

    "max_volatility_spread":
        ConfigVar(key="max_volatility_spread",
                  prompt="What is the maximum spread of the first bid and ask after volatility adjustment (e.g. 0.2, max spread is 0.2%) >>> ",
                  type_str="decimal",
                  default=Decimal(2.0),
                  prompt_on_new=True
                  ),

    #create a validate that promots this question when the volatility_adjustment is true
    "volatility_buffer_size":
        ConfigVar(key="volatility_buffer_size",
                  prompt="Enter amount of ticks that will be stored to calculate volatility average >>> ",
                  type_str="int",
                  default=200
                  ),

    "volatility_processing_length":
        ConfigVar(key="volatility_processing_length",
                  prompt="Enter amount of periods to smooth the slow volatility indicator >>> ",
                  type_str="int",
                  default=15),

    "inventory_management":
        ConfigVar(key="inventory_management",
                  prompt="Do you want to adjust your bid_ask spread on invenroy skew? True/False >>> ",
                  type_str="bool",
                  default=False,
                  validator=validate_bool,
                  prompt_on_new=True),

    "inventory_management_multiplier":
        ConfigVar(key="inventory_management_multiplier",
                  prompt="What multiplier do you want to use to adjust bid/ask spread based on inventory skew? genarlly invenory skew ranges between -0.5 and 0.5 >>> ",
                  type_str="decimal",
                  default=Decimal(1.0),
                  prompt_on_new=True
                  ),

    "max_inventory_management_spread":
        ConfigVar(key="max_inventory_management_spread",
                  prompt="What is the maximum spread of the first bid and ask after inventory management adjustment (e.g. 0.2, max spread is 0.2%) >>> ",
                  type_str="decimal",
                  default=Decimal(2.0),
                  prompt_on_new=True
                  ),

    "hanging_orders_enabled":
        ConfigVar(key="hanging_orders_enabled",
                  prompt="Do you want to enable hanging orders? (Yes/No) >>> ",
                  type_str="bool",
                  default=False,
                  validator=validate_bool),

    "hanging_orders_cancel_pct":
        ConfigVar(key="hanging_orders_cancel_pct",
                  prompt="At what spread percentage (from mid price) will hanging orders be canceled? "
                         "(Enter 1 to indicate 1%) >>> ",
                  required_if=lambda: pure_market_making_config_map.get(
                      "hanging_orders_enabled").value,
                  type_str="decimal",
                  default=Decimal("10"),
                  validator=lambda v: validate_decimal(v, 0, 100, inclusive=False)),

    "hanging_orders_enabled_other":
        ConfigVar(key="hanging_orders_enabled_other",
                  prompt="hanging_orders_enabled_other (Yes/No) >>> ",
                  type_str="bool",
                  default=False,
                  validator=validate_bool,
                  prompt_on_new=True),

    "min_profitability":
        ConfigVar(key="min_profitability",
                  prompt="What is the min_profitability on your hanging order_other? (e.g. 0.5 for 0.50%) >>> ",
                  type_str="decimal",
                  default=Decimal(0.5),
                  prompt_on_new=True
                  ),

    "hanging_inventory_management_range":
        ConfigVar(key="hanging_inventory_management_range",
                  prompt="If inventoy management and hanging orders enabled, at what inventory management skew would you not place a hanging order (e.g. 0.3) >>> ",
                  type_str="decimal",
                  default=Decimal(0.375),
                  prompt_on_new=True
                  ),

    "target_balance_spread_reducer_temp":
    ConfigVar(key="target_balance_spread_reducer_temp",
              prompt="target_balance_spread_reducer_temp(e.g. 0.99 = 99%) >>> ",
              type_str="decimal",
              validator=lambda v: validate_decimal(v),
              prompt_on_new=True,
              default=0.9),

    "order_optimization_enabled":
        ConfigVar(key="order_optimization_enabled",
                  prompt="Do you want to enable best bid ask jumping? (Yes/No) >>> ",
                  type_str="bool",
                  default=True,
                  validator=validate_bool),
    "ask_order_optimization_depth":
        ConfigVar(key="ask_order_optimization_depth",
                  prompt="How deep do you want to go into the order book for calculating "
                         "the top ask, ignoring dust orders on the top "
                         "(expressed in base asset amount)? >>> ",
                  required_if=lambda: pure_market_making_config_map.get(
                      "order_optimization_enabled").value,
                  type_str="decimal",
                  validator=lambda v: validate_decimal(v, min_value=0),
                  default=0),
    "bid_order_optimization_depth":
        ConfigVar(key="bid_order_optimization_depth",
                  prompt="How deep do you want to go into the order book for calculating "
                         "the top bid, ignoring dust orders on the top "
                         "(expressed in base asset amount)? >>> ",
                  required_if=lambda: pure_market_making_config_map.get(
                      "order_optimization_enabled").value,
                  type_str="decimal",
                  validator=lambda v: validate_decimal(v, min_value=0),
                  default=0),
    "add_transaction_costs":
        ConfigVar(key="add_transaction_costs",
                  prompt="Do you want to add transaction costs automatically to order prices? (Yes/No) >>> ",
                  type_str="bool",
                  default=False,
                  validator=validate_bool),
    "price_source":
        ConfigVar(key="price_source",
                  prompt="Which price source to use? (current_market/external_market/custom_api) >>> ",
                  type_str="str",
                  default="current_market",
                  validator=validate_price_source,
                  on_validated=on_validate_price_source),

    "conversion_data_source":
        ConfigVar(key="conversion_data_source",
                  prompt="conversion_data_source use (Yes/No) >>> ",
                  type_str="bool",
                  default=False,
                  validator=validate_bool),

    "conversion_exchange":
        ConfigVar(key="conversion_exchange",
                  prompt="Enter conversion_exchange exchange name >>> ",
                  default='binance',
                  type_str="str"),

    "conversion_trading_pair":
        ConfigVar(key="conversion_trading_pair",
                  prompt="Enter conversion_trading_pair name >>> ",
                  required_if=lambda: pure_market_making_config_map.get(
                      "price_source").value == "external_market",
                  type_str="str"),

    "micro_price_price_source":
        ConfigVar(key="micro_price_price_source",
                  prompt="For Micro_price calculation, do you want to use the external price source >>> ",
                  type_str="bool",
                  default=False),

    "price_type":
        ConfigVar(key="price_type",
                  prompt="Which price type to use? ("
                         "mid_price/last_price/last_own_trade_price/best_bid/best_ask/inventory_cost) >>> ",
                  type_str="str",
                  required_if=lambda: pure_market_making_config_map.get(
                      "price_source").value != "custom_api",
                  default="mid_price",
                  on_validated=on_validated_price_type,
                  validator=validate_price_type),
    "price_source_exchange":
        ConfigVar(key="price_source_exchange",
                  prompt="Enter external price source exchange name >>> ",
                  required_if=lambda: pure_market_making_config_map.get(
                      "price_source").value == "external_market",
                  type_str="str",
                  validator=validate_price_source_exchange,
                  on_validated=on_validated_price_source_exchange),
    "price_source_market":
        ConfigVar(key="price_source_market",
                  prompt=price_source_market_prompt,
                  required_if=lambda: pure_market_making_config_map.get(
                      "price_source").value == "external_market",
                  type_str="str",
                  validator=validate_price_source_market),
    "take_if_crossed":
        ConfigVar(key="take_if_crossed",
                  prompt="Do you want to take the best order if orders cross the orderbook? ((Yes/No) >>> ",
                  required_if=lambda: pure_market_making_config_map.get(
                      "price_source").value == "external_market",
                  type_str="bool",
                  validator=validate_bool),
    "price_source_custom_api":
        ConfigVar(key="price_source_custom_api",
                  prompt="Enter pricing API URL >>> ",
                  required_if=lambda: pure_market_making_config_map.get(
                      "price_source").value == "custom_api",
                  type_str="str"),
    "custom_api_update_interval":
        ConfigVar(key="custom_api_update_interval",
                  prompt="Enter custom API update interval in second (default: 5.0, min: 0.5) >>> ",
                  required_if=lambda: False,
                  default=float(5),
                  type_str="float",
                  validator=lambda v: validate_decimal(v, Decimal("0.5"))),
    "order_override":
        ConfigVar(key="order_override",
                  prompt=None,
                  required_if=lambda: False,
                  default=None,
                  type_str="json"),
    "should_wait_order_cancel_confirmation":
        ConfigVar(key="should_wait_order_cancel_confirmation",
                  prompt="Should the strategy wait to receive a confirmation for orders cancellation "
                         "before creating a new set of orders? "
                         "(Not waiting requires enough available balance) (Yes/No) >>> ",
                  type_str="bool",
                  default=True,
                  validator=validate_bool),
    "split_order_levels_enabled":
        ConfigVar(key="split_order_levels_enabled",
                  prompt="Do you want bid and ask orders to be placed at multiple defined spread and amount? "
                         "This acts as an overrides which replaces order_amount, order_spreads, "
                         "order_level_amount, order_level_spreads (Yes/No) >>> ",
                  default=False,
                  type_str="bool",
                  validator=validate_bool),
    "bid_order_level_spreads":
        ConfigVar(key="bid_order_level_spreads",
                  prompt="Enter the spreads (as percentage) for all bid spreads "
                         "e.g 1,2,3,4 to represent 1%,2%,3%,4%. "
                         "The number of levels set will be equal to the "
                         "minimum length of bid_order_level_spreads and bid_order_level_amounts >>> ",
                  default=None,
                  type_str="str",
                  required_if=lambda: pure_market_making_config_map.get(
                      "split_order_levels_enabled").value,
                  validator=validate_decimal_list),
    "ask_order_level_spreads":
        ConfigVar(key="ask_order_level_spreads",
                  prompt="Enter the spreads (as percentage) for all ask spreads "
                         "e.g 1,2,3,4 to represent 1%,2%,3%,4%. "
                         "The number of levels set will be equal to the "
                         "minimum length of bid_order_level_spreads and bid_order_level_amounts >>> ",
                  default=None,
                  type_str="str",
                  required_if=lambda: pure_market_making_config_map.get(
                      "split_order_levels_enabled").value,
                  validator=validate_decimal_list),
    "bid_order_level_amounts":
        ConfigVar(key="bid_order_level_amounts",
                  prompt="Enter the amount for all bid amounts. "
                         "e.g 1,2,3,4. "
                         "The number of levels set will be equal to the "
                         "minimum length of bid_order_level_spreads and bid_order_level_amounts >>> ",
                  default=None,
                  type_str="str",
                  required_if=lambda: pure_market_making_config_map.get(
                      "split_order_levels_enabled").value,
                  validator=validate_decimal_list),

    "keep_target_balance":
    ConfigVar(key="keep_target_balance",
              prompt="do you want to keep a target balance? >>> ",
              type_str="bool",
              default=False,
              prompt_on_new=True),

    "target_base_balance":
    ConfigVar(key="target_base_balance",
              prompt="what is your target base balance? >>> ",
              type_str="decimal",
              validator=lambda v: validate_decimal(v),
              prompt_on_new=True,
              default=0),

    "target_balance_spread_reducer":
    ConfigVar(key="target_balance_spread_reducer",
              prompt="To restore balance, how much in percentage do you want to decrease your spread(e.g. 0.99 = 99%) >>> ",
              type_str="decimal",
              validator=lambda v: validate_decimal(v),
              prompt_on_new=True,
              default=0.9),

    "use_micro_price":
    ConfigVar(key="use_micro_price",
              prompt="do you want to use the micro-price instead of the other price sources >>> ",
              type_str="bool",
              default=True,
              prompt_on_new=True),

    "micro_price_percentage_depth":
    ConfigVar(key="micro_price_percentage_depth",
              prompt="for the micro-price volume calculation, how much depth in % would you like to use on the bid and ask side (e.g. 0.2% = 0.002) >>> ",
              type_str="decimal",
              validator=lambda v: validate_decimal(v),
              prompt_on_new=True,
              default=0.0035),

    "micro_price_effect":
    ConfigVar(key="micro_price_effect",
              prompt="Do you want to fully use the micro-price 0.9 = 90% micro-price usage >>> ",
              type_str="decimal",
              validator=lambda v: validate_decimal(v),
              prompt_on_new=True,
              default=0.9),

    "max_deviation":
    ConfigVar(key="max_deviation",
              prompt="what is the max deviation for the target base balance >>> ",
              type_str="decimal",
              validator=lambda v: validate_decimal(v),
              prompt_on_new=True,
              default=0),

    "filled_order_delay_target_balance":
    ConfigVar(key="filled_order_delay_target_balance",
              prompt="Hanging order other cancel time >>> ",
              type_str="float",
              validator=lambda v: validate_decimal(v),
              prompt_on_new=True,
              default=60),

    "ask_order_level_amounts":
        ConfigVar(key="ask_order_level_amounts",
                  prompt="Enter the amount for all ask amounts. "
                         "e.g 1,2,3,4. "
                         "The number of levels set will be equal to the "
                         "minimum length of bid_order_level_spreads and bid_order_level_amounts >>> ",
                  default=None,
                  required_if=lambda: pure_market_making_config_map.get(
                      "split_order_levels_enabled").value,
                  type_str="str",
                  validator=validate_decimal_list),
    "dump_variables":
    ConfigVar(key="dump_variables",
              prompt="dump_variables >>> ",
              type_str="bool",
              default=False
              ),


}
