import logging
import typing
from typing import *

from threading import Timer
import pandas as pd # work with timeframes and timeseries
import time
from models import *
logger = logging.getLogger()

if TYPE_CHECKING:
    from connectors.bitmex import BitmexClient
    from connectors.binance_futures import BinanceFuturesClient

TF_EQUIV = {"1m": 60, "5m": 300, "15m": 900, "30m": 1800, "1h": 3600, "4h": 14400}

class Startegy:
    def __init__(self, client: Union["BitmexClient", "BinanceFuturesClient"], contract: Contract, exchange: str,
                 timeframe: str, balance_pct: float, take_profit: float, stop_loss: float, strat_name):

        self.client = client

        self.contract = contract
        self.exchange = exchange
        self.tf = timeframe
        self.tf_equiv = TF_EQUIV[timeframe] * 100
        self.balance_pct = balance_pct
        self.take_profit = take_profit
        self.stop_loss = stop_loss

        self.strat_name = strat_name

        self.active_position = False

        self.candles: typing.List[Candle] = []
        self.log_messages = []
        self.trades: List[Trade] = []

    def _add_log(self, msg: str):
        logger.info("%s", msg)
        self.log_messages.append({"log": msg, "displayed": False})

    def parse_trades(self, price: float, size: float, timestamp: int) -> str:


        timestamp_diff = int(time.time() * 1000) - timestamp

        if timestamp_diff >= 2000:
            logger.warning("%s $s: %s ms of difference between the current time and the trade time, it means that there is overload", self.exchange, self.contract.symbol, timestamp_diff)
        last_candle = self.candles[-1]

        # Same Candle

        if timestamp < last_candle.timestamp + self.tf_equiv:

            last_candle.close = price
            last_candle.volume += size

            if price > last_candle.high:
                last_candle.high = price
            elif price < last_candle.low:
                last_candle.low = price

            return "same_candle"
        # Missing candles

        if timestamp >= last_candle.timestamp + 2 * self.tf_equiv:
            missing_candles = int((timestamp - last_candle.timestamp) / self.tf_equiv) - 1

            logger.info("%s Missing %s candles for %s %s (%s %s)", self.exchange, missing_candles, self.contract.symbol
                        , self.tf, timestamp, last_candle.timestamp)

            for missing in range(missing_candles):
                new_ts = last_candle.timestamp + self.tf_equiv
                candle_info = {'ts': new_ts, 'open': last_candle.close, 'high': last_candle.close, 'low': last_candle.close
                    , 'close': last_candle.close, 'volume': 0}

                new_candle = Candle(candle_info, self.tf, "parse_trade")

                self.candles.append(new_candle)

                last_candle = new_candle

            new_ts = last_candle.timestamp + self.tf_equiv
            candle_info = {'ts': new_ts, 'open': price, 'high': price, 'low': price, 'close': price, 'volume': size}
            new_candle = Candle(candle_info, self.tf, "parse_trade")

            self.candles.append(new_candle)

            return "new_candle"
        # New Candle arrived

        elif timestamp >= last_candle.timestamp + self.tf_equiv:
            new_ts = last_candle.timestamp + self.tf_equiv
            candle_info = {'ts': new_ts, 'open': price, 'high': price, 'low': price, 'close': price, 'volume': size}
            new_candle = Candle(candle_info, self.tf, "parse_trade")

            self.candles.append(new_candle)

            logger.info("%s New candle for  %s %s", self.exchange, self.contract.symbol, self.tf)

            return "new_candle"

    def _check_order_status(self, order_id):

        order_status = self.client.get_order_status(self.contract, order_id)

        if order_status is not None:

            logger.info("%s order status: %s", self.exchange, order_status.status)

            if order_status.status == "filled":
                for trade in self.trades:
                    if trade.order_id == order_id:
                        trade.entry_price = order_status.avg_price
                        break

                return

        t = Timer(2.0, lambda: self._check_order_status(order_id))
        t.start()

    def _open_position(self, signal_result: int):

        trade_size = self.client.get_trade_size(self.contract, self.candles[-1].close, self.balance_pct)

        if trade_size in None:
            return

        order_side = "buy" if signal_result == 1 else "sell"
        position_side = "long" if signal_result == 1 else "short"

        self._add_log(f"{position_side} signal on {self.contract.symbol} {self.tf}")

        order_status = self.client.place_order(self.contract, "MARKET", trade_size, order_side)

        if order_status is not None:
            self._add_log(f"{order_side.capitalize()} order placed on {self.exchange} | Status: {order_status.status}")

            self.active_position = True

            avg_fill_price = None
            if order_status.status == "filled":
                avg_fill_price = order_status.avg_price
            else:
                t = Timer(2.0, lambda: self._check_order_status(order_status.order_id))
                t.start()

            new_trade = Trade({"time": int(time.time() * 1000), "entry_price": avg_fill_price,
                               "contract": self.contract, "strategy": self.strat_name, "side": position_side,
                               "status": "open", "pnl": 0, "quantity": trade_size, "entry_id": order_status.order_id})

            self.trades.append(new_trade)


class TechnicalStrategy(Startegy):
    def __init__(self, client, contract: Contract, exchange: str, timeframe: str, balance_pct: float, take_profit: float,
                 stop_loss: float, other_params: Dict):

        super().__init__(client, contract, exchange, timeframe, balance_pct, take_profit, stop_loss, "Technical")

        self._ema_fast = other_params['ema_fast']
        self._ema_slow = other_params['ema_slow']
        self._ema_signal = other_params['ema_signal']

        self._rsi_periods = other_params['rsi_length']
        print("Activate strategy for ", contract.symbol)

    def _rsi(self): # Relative strength index

        close_price_list = []
        for candle in self.candles:
            close_price_list.append(candle.close)

        closes = pd.Series(close_price_list)

        delta = closes.diff().dropna()

        up, down = delta.copy(), delta.copy()

        up[up < 0] = 0
        down[down > 0] = 0

        avg_gain = up.ewm(com=(self._rsi_periods - 1), min_periods= self._rsi_periods).mean()
        avg_loss = down.abs().ewm(com=(self._rsi_periods - 1), min_periods= self._rsi_periods).mean()

        rs = avg_gain / avg_loss

        rsi = 100 - 100 / (1 + rs)
        rsi = rsi.round(2)

        return rsi.iloc[-2]


    def _macd(self) -> typing.Tuple[float, float]: # moving average convergence/divergence

        close_price_list = []
        for candle in self.candles:
            close_price_list.append(candle.close)

        closes = pd.Series(close_price_list)

        # calculate ema of closes

        ema_fast = closes.ewm(span=self._ema_fast).mean()
        ema_slow = closes.ewm(span=self._ema_slow).mean()

        macd_line_indicator = ema_fast - ema_slow
        macd_signal = macd_line_indicator.ewm(span=self._ema_signal).mean()

        return macd_line_indicator.iloc[-2], macd_signal.iloc[-2]

    def _check_indicator(self):

        macd_line_indicator, macd_signal = self._macd()
        rsi = self._rsi()

        print(rsi, macd_line_indicator, macd_signal)
        if rsi < 30 and macd_line_indicator > macd_signal: # rsi < 30 =>  oversold
            return 1
        elif rsi > 70 and macd_line_indicator < macd_signal: # rsi > 70 => overbaught
            return -1
        else:
            return 0

    def check_trade(self, tick_type: str):

        if tick_type == "new_candle" and self.active_position == False:
            signal_result = self._check_indicator()

            if signal_result in [-1,1]:
                self._open_position(signal_result)


class BreakoutStrategy(Startegy):
    def __init__(self, client, contract: Contract, exchange: str, timeframe: str, balance_pct: float, take_profit: float,
                 stop_loss: float, other_params: Dict):
        super().__init__(client, contract, exchange, timeframe, balance_pct, take_profit, stop_loss, "Breakout")

        self._min_volume = other_params['min_volume']

    def _check_indicator(self) -> int:
        if self.candles[-1].close > self.candles[-2].high and self.candles[-1].volume > self._min_volume: # The stock price getting higher so it indicates that we should start long position
            return 1
        if self.candles[-1].close < self.candles[-2].high and self.candles[-1].volume > self._min_volume: # The stock price getting lower so it indicates that we should start short position
            return -1
        else:
            return 0

    def check_trade(self, tick_type: str):

        if self.active_position == False:
            signal_result = self._check_indicator()

            if signal_result in [-1,1]:
                self._open_position(signal_result)





