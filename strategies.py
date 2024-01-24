import logging
import typing
from typing import *

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
        self.contract = contract
        self.exchange = exchange
        self.tf = timeframe
        self.tf_equiv = TF_EQUIV[timeframe] * 100
        self.balance_pct = balance_pct
        self.take_profit = take_profit
        self.stop_loss = stop_loss

        self.candles: typing.List[Candle] = []

    def parse_trades(self, price: float, size: float, timestamp: int) -> str:

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
        #

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


