# distutils: language=c++

from libc.stdint cimport int64_t

from hummingbot.strategy.strategy_base cimport StrategyBase


cdef class PureMarketMakingStrategy(StrategyBase):
    cdef:
        object _market_info
        object _strategy_identifier
        object _strategy
        object _second_market
        object _bid_spread
        object _ask_spread
        object _minimum_spread
        object _order_amount
        object _avg_vol
        int _order_levels
        int _buy_levels
        int _sell_levels
        object _split_order_levels_enabled
        object _bid_order_level_spreads
        object _ask_order_level_spreads
        object _order_level_spread
        object _micro_price_price_source
        object _order_level_amount
        double _order_refresh_time
        object _keep_target_balance
        object _target_base_balance
        object _use_micro_price
        object _micro_price_percentage_depth
        object _max_deviation
        object _micro_price_effect
        double _max_order_age
        object _order_refresh_tolerance_pct
        double _filled_order_delay
        object _filled_order_delay_target_balance
        bint _inventory_skew_enabled
        object _inventory_target_base_pct
        object _inventory_range_multiplier
        bint _hanging_orders_enabled
        object _hanging_orders_tracker
        bint _order_optimization_enabled
        object _ask_order_optimization_depth
        object _bid_order_optimization_depth
        bint _add_transaction_costs_to_orders
        object _asset_price_delegate
        object _inventory_cost_price_delegate
        object _price_type
        object _target_balance_spread_reducer_temp
        object _buy_order_fill
        object _sell_order_fill
        object _hanging_orders_enabled_other
        object _target_balance_spread_reducer
        bint _take_if_crossed
        object _price_ceiling
        object _price_floor
        object _price_band_above_adjustment
        object _price_band_below_adjustment
        object _ema_timeframe
        object _ema_limit
        object _ema_length
        object _price_band_refresh_time
        object _moving_price_band_update_timestamp
        bint _ping_pong_enabled
        list _ping_pong_warning_lines
        bint _hb_app_notification
        object _order_override

        double _cancel_timestamp
        double _create_timestamp
        object _balance_fixer_timestamp
        object _limit_order_type
        bint _all_markets_ready
        int _filled_buys_balance
        int _filled_sells_balance
        double _last_timestamp
        double _status_report_interval
        int64_t _logging_options
        object _last_own_trade_price
        object _last_buy_order_price
        object _last_sell_order_price
        bint _should_wait_order_cancel_confirmation
        object _volatility_adjustment
        object _min_spread_order_id

        object _volatility_buffer_size
        object _volatility_processing_length
        object _max_volatility_spread
        object _volatility_adjustment_multiplier
        object _inventory_management_multiplier
        object _inventory_management
        object _conversion_market
        object _conversion_data_source
        object _max_inventory_management_spread
        object _hanging_order_list
        object _dump_variables
        object _exchange
        object _raw_trading_pair
        object _min_profitability
        object _hanging_inventory_management_range

        object _engine
        object _connection

        object _moving_price_band

    cdef object c_get_mid_price(self)
    cdef object c_create_base_proposal(self)
    cdef tuple c_get_adjusted_available_balance(self, list orders)
    cdef c_apply_order_levels_modifiers(self, object proposal)
    cdef c_apply_ping_pong(self, object proposal)
    cdef c_apply_order_price_modifiers(self, object proposal)
    cdef c_apply_order_size_modifiers(self, object proposal)
    cdef c_apply_inventory_skew(self, object proposal)
    cdef c_apply_budget_constraint(self, object proposal)

    cdef c_filter_out_takers(self, object proposal)
    cdef c_cancel_all_orders(self)
    cdef c_check_imbalance(self)
    cdef c_weighted_mid_price(self)
    cdef c_apply_order_optimization(self, object proposal)
    cdef c_apply_add_transaction_costs(self, object proposal)
    cdef bint c_is_within_tolerance(self, list current_prices, list proposal_prices)
    cdef c_cancel_active_orders(self, object proposal)
    cdef c_cancel_orders_below_min_spread(self)
    cdef c_cancel_active_orders_on_max_age_limit(self)
    cdef bint c_to_create_orders(self, object proposal)
    cdef c_execute_orders_proposal(self, object proposal)
    cdef set_timers(self)
    cdef c_apply_moving_price_band(self, object proposal)
    cdef c_collect_market_variables(self, double timestamp)
    cdef c_apply_inventory_spread_management(self, object proposal)
    cdef c_dump_debug_variables(self)
    cdef c_apply_vol_adjustment(self, object proposal)
