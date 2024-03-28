import tkinter as tk
import threading
from tkinter.messagebox import askquestion

from connectors.bitmex import BitmexClient
from connectors.binance import BinanceClient
from interface.Trading import TradingFrame
from interface.login import Login
from interface.strategy import StrategyFrame
import json

class interface(tk.Tk):
    def __init__(self, bitmex: BitmexClient, binance: BinanceClient):
            super().__init__()

            self.bitmex = bitmex
            self.binance = binance

            self.bg_color = "Black"
            self.fg_color = "White"
            self.color_button_text = "Light Mode"

            self.title("Trading Bot")
            self.protocol("WM_DELETE_WINDOW", self._proper_close)

            self.config(bg=self.bg_color)

            # Configure row weights
            self.grid_rowconfigure(0, weight=9)  # Top row takes 9/10 of the space
            self.grid_rowconfigure(1, weight=1)  # Bottom row takes 1/10 of the space

            # Configure column weights
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)

            self.right_frame = tk.Frame(self, bg=self.bg_color)
            self.right_frame.grid(row=0, column=1, sticky="nsew")

            self.Strategy_frame = StrategyFrame(self, self.right_frame, bitmex=self.bitmex, binance=self.binance,
                                                bg_color=self.bg_color, fg_color=self.fg_color)
            self.Strategy_frame.grid(row=0, column=0, sticky="nsew")  # Updated row index to 0

            self.trade_frame = TradingFrame(self.right_frame, bg_color=self.bg_color, fg_color=self.fg_color, )
            self.trade_frame.grid(row=1, column=0, sticky="nsew")  # Updated row index to 1

            self.right_frame.grid_rowconfigure(0, weight=1)
            self.right_frame.grid_rowconfigure(1, weight=1)  # Added row configuration for index 1
            self.right_frame.grid_columnconfigure(0, weight=1)  # Updated column index to 0

            self.bottom_frame = tk.Frame(self, bg=self.bg_color)
            self.bottom_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

            self.log_in_frame = Login(self,self.bottom_frame, bg_color=self.bg_color, fg_color=self.fg_color,
                                      color_button_text= self.color_button_text)
            self.log_in_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")

            self.bottom_frame.grid_rowconfigure(0, weight=1)
            self.bottom_frame.grid_columnconfigure(0, weight=1)

            # Starts the infinite interface_old update loop

            self._run_timer()


    def _proper_close(self):

        """
        Triggered when the user click on the Close button of the interface_old.
        This lets you have control over what's happening just before closing the interface_old.
        :return:
        """

        result = askquestion("Confirmation", "Do you really want to exit the application?")
        if result == "yes":
            self.binance.reconnect = False  # Avoids the infinite reconnect loop in _start_ws()
            self.bitmex.reconnect = False
            self.binance.ws.close()
            self.bitmex.ws.close()

            self._stop_timer()

            self.destroy()  # Destroys the UI and terminates the program as no other thread is running
    def _run_timer(self):

        self.timer = threading.Timer(10, self._run_timer).start()

        # Call your function
        self._save_workspace()

    def _stop_timer(self):
        # Check if the timer is running
        if self.timer and self.timer.is_alive():
            self.timer.cancel()  # Stop the timer


    def  update_color(self):
        if self.bg_color == "Black":
            self.bg_color = "White"
        else:
            self.bg_color = "Black"

        if self.fg_color == "White":
            self.fg_color = "Black"
        else:
            self.fg_color = "White"

        if self.color_button_text == "Light Mode":
            self.color_button_text = "Dark Mode"
        else:
            self.color_button_text = "Light Mode"

        self.config(bg=self.bg_color)
        self.right_frame.config(bg=self.bg_color)
        self.bottom_frame.config(bg=self.bg_color)
        self.Strategy_frame.config(bg=self.bg_color)
        self.trade_frame.config(bg=self.bg_color)
        self.log_in_frame.update_color(new_bg_color=self.bg_color, new_fg_color=self.fg_color,
                                       new_button_text=self.color_button_text)
        self.Strategy_frame.update_color(new_bg_color=self.bg_color, new_fg_color=self.fg_color)
        self.trade_frame.update_color(new_bg_color=self.bg_color, new_fg_color=self.fg_color)

        """""""""
            # Update background color of the frame, log_in_text, and add_color_button
        self.config(bg=self.bg_color)
        self.watch_list.config(bg=self.bg_color, fg=self.fg_color)
        self.Strategy_frame.config(bg=self.bg_color, fg=self.fg_color)
        self.trade_frame.config(bg=self.bg_color, fg=self.fg)
        """""""""

    def update_logs(self):
        self.update_exchange_logs(self.binance)
        self.update_exchange_logs(self.bitmex)

        for key, value in self.watch_list.widgets['symbol'].items():
            symbol = self.watch_list.widgets['symbol'][key].cget("text")
            exchange = self.watch_list.widgets['exchange'][key].cget("text")

            if exchange == "Binance" and symbol in self.binance.contracts:
                self.update_watch_list_prices(symbol, self.binance, key)
            elif exchange == "Bitmex" and symbol in self.bitmex.contracts:
                self.update_watch_list_prices(symbol, self.bitmex, key)

        self.after(2000, self.update_logs)

    def update_exchange_logs(self, exchange_client):
        for log in exchange_client.logs:
            if not log["displayed"]:
                log["displayed"] = True
                self.log_in_frame.add_log_message(log["log"])

    def update_watch_list_prices(self, symbol, exchange_client, key):
        if symbol not in exchange_client.prices:
            exchange_client.get_bid_ask(exchange_client.contracts[symbol])
            return

        precision = exchange_client.contracts[symbol].price_decimals
        prices = exchange_client.prices[symbol]

        if prices['bid'] is not None:
            price_str = "%.*f" % (precision, prices['bid'])
            self.watch_list.widgets['var_bid'][key].set(price_str)

        if prices['ask'] is not None:
            price_str = "%.*f" % (precision, prices['ask'])
            self.watch_list.widgets['var_ask'][key].set(price_str)

    def _update_ui(self):

        """
        Called by itself every 1500 seconds. It is similar to an infinite loop but runs within the same Thread
        as .mainloop() thanks to the .after() method, thus it is "thread-safe" to update elements of the interface_old
        in this method. Do not update Tkinter elements from another Thread like the websocket thread.
        :return:
        """

        # Logs

        for log in self.bitmex.logs:
            if not log['displayed']:
                self.log_in_frame.add_log_message(log['log'])
                log['displayed'] = True

        for log in self.binance.logs:
            if not log['displayed']:
                self.log_in_frame.add_log_message(log['log'])
                log['displayed'] = True

        # Trades and Logs

        for client in [self.binance, self.bitmex]:

            try:  # try...except statement to handle the case when a dictionary is updated during the following loops

                for b_index, strat in client.strategies.items():
                    for log in strat.logs:
                        if not log['displayed']:
                            self.log_in_frame.add_log_message(log['log'])
                            log['displayed'] = True

                    # Update the Trades component (add a new trade, change status/PNL)

                    for trade in strat.trades:
                        if trade.time not in self.trade_frame.body_widgets['symbol']:
                            self.trade_frame.add_trade(trade)

                        if "binance" in trade.contract.exchange:
                            precision = trade.contract.price_decimals
                        else:
                            precision = 8  # The Bitmex PNL is always is BTC, thus 8 decimals

                        pnl_str = "{0:.{prec}f}".format(trade.pnl, prec=precision)
                        self.trade_frame.body_widgets['pnl_var'][trade.time].set(pnl_str)
                        self.trade_frame.body_widgets['status_var'][trade.time].set(trade.status.capitalize())
                        self.trade_frame.body_widgets['quantity_var'][trade.time].set(trade.quantity)

            except RuntimeError as e:
                self.log_in_frame.add_log_message("Error while looping through strategies dictionary: %s", e)

        # Watchlist prices

        try:
            for key, value in self.watch_list.widgets['symbol'].items():

                symbol = self.watch_list.widgets['symbol'][key].cget("text")
                exchange = self.watch_list.widgets['exchange'][key].cget("text")

                if exchange == "Binance":
                    if symbol not in self.binance.contracts:
                        continue

                    if symbol not in self.binance.ws_subscriptions["bookTicker"] and self.binance.ws_connected:
                        self.binance.subscribe_channel([self.binance.contracts[symbol]], "bookTicker")

                    if symbol not in self.binance.prices:
                        self.binance.get_bid_ask(self.binance.contracts[symbol])
                        continue

                    precision = self.binance.contracts[symbol].price_decimals

                    prices = self.binance.prices[symbol]

                elif exchange == "Bitmex":
                    if symbol not in self.bitmex.contracts:
                        continue

                    if symbol not in self.bitmex.prices:
                        continue

                    precision = self.bitmex.contracts[symbol].price_decimals

                    prices = self.bitmex.prices[symbol]

                else:
                    continue

                if prices['bid'] is not None:
                    price_str = "{0:.{prec}f}".format(prices['bid'], prec=precision)
                    self.watch_list.widgets['bid_var'][key].set(price_str)
                if prices['ask'] is not None:
                    price_str = "{0:.{prec}f}".format(prices['ask'], prec=precision)
                    self.watch_list.widgets['ask_var'][key].set(price_str)

        except RuntimeError as e:
            self.log_in_frame.add_log_message("Error while looping through watchlist dictionary: %s", e)

        self.after(1500, self._update_ui)
    def _save_workspace(self):

        """
        Collect the current data on the interface_old and saves it to the SQLite database to avoid setting up everything
        again everytime you open the program.
        Triggered from a Menu command.
        :return:
        """

        # Watchlist

        watchlist_symbols = []

        for key, value in self.watch_list.widgets['symbol'].items():
            symbol = value.cget("text")
            exchange = self.watch_list.widgets['exchange'][key].cget("text")

            watchlist_symbols.append((symbol, exchange,))

        self.watch_list.db.save("watchlist", watchlist_symbols)

        # Strategies

        strategies = []

        strat_widgets = self.Strategy_frame.widgets

        for b_index in strat_widgets['Contract']:  # Loops through the rows of a column (not necessarily the 'contract' one

            strategy_type = strat_widgets['var_strategy_type'][b_index].get()
            contract = strat_widgets['var_Contract'][b_index].get()
            timeframe = strat_widgets['var_Timeframe'][b_index].get()
            balance_pct = strat_widgets['balance_pct'][b_index].get()
            take_profit = strat_widgets['take_profit'][b_index].get()
            stop_loss = strat_widgets['stop_loss'][b_index].get()

            # Extra parameters are all saved in one column as a JSON string because they change based on the strategy

            extra_params = dict()

            for param in self.Strategy_frame.extra_params_dict[strategy_type]:
                code_name = param['code_name']

                extra_params[code_name] = self.Strategy_frame.additional_parameters[b_index][code_name]

            strategies.append((strategy_type, contract, timeframe, balance_pct, take_profit, stop_loss,
                               json.dumps(extra_params),))

        self.Strategy_frame.db.save("strategies", strategies)

        self.log_in_frame.add_log_message("Workspace saved")


