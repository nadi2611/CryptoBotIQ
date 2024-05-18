import tkinter as tk
import time
from UI.ui_watch_list import WatchList
import threading

FONT = ("Calibri", 12, "normal")

""""""""""
*args -to pass arguments without specifing it name
**kwargs - to pass key words arguments - like bg
"""""""""

class Login(tk.Frame):
    def __init__(self, main_interface, *args, **kwargs):
        self.bg: str = kwargs.pop('bg_color')
        self.fg :str= kwargs.pop('fg_color')
        self.button_text :str = kwargs.pop('color_button_text')

        super().__init__(*args, **kwargs)

        self.log_text = tk.Text(self, bg=self.bg, fg=self.fg, font=FONT, height=5, width=5, state=tk.DISABLED)
        self.log_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.add_color_button = tk.Button(self, command=lambda: self.change_color_button(main_interface),
                                          font=FONT, fg=self.fg, bg=self.bg, text=self.button_text)

        self.watch_list_button = tk.Button(self, command=lambda: self.open_watch_list(main_interface),
                                          font=FONT, fg=self.fg, bg=self.bg, text="Watch List")

        # Use anchor and justify to align the button to the top right corner
        # anchor=tk.NE to make the button anchor to the top-right corner
        self.add_color_button.place(relx=1.0, rely=0.0, anchor=tk.NE)

        # Place the Watch List button right under the Change Color button
        self.watch_list_button.place(relx=1.0, rely=0.0, anchor=tk.NE, x=-85)

        self.binance = main_interface.binance
        self.watch_list_opend = False

        self.run_timer()


    def change_color_button(self, main_interface):
        main_interface.update_color()

    def open_watch_list(self, main_interface):
        self.watch_list_opend = True
        self.watch_list_button.config(stat=tk.DISABLED)
        self.open_temp_frame(main_interface)

    def update_color(self, new_bg_color: str, new_fg_color: str,
                                       new_button_text: str):
        self.bg = new_bg_color
        self.fg = new_fg_color
        self.button_text = new_button_text
        self.config(bg=self.bg)
        self.log_text.config(bg=self.bg)
        self.add_color_button.config(bg=self.bg, fg=self.fg, text=self.button_text)
        self.watch_list_button.config(bg=self.bg, fg=self.fg)
        if self.watch_list_opend:
            self.watch_list.update_color(new_bg_color= self.bg , new_fg_color=self.fg  )
            self.watch_list.config(background= self.bg)

    def add_log_message(self, message: str):
        self.log_text.config(state=tk.NORMAL, bg=self.bg, fg="red4")

        current_time_seconds = time.time()

        # Convert the time to a struct_time object
        current_time_struct = time.gmtime(current_time_seconds)

        # the first argument ("1.0") indicates the message will be added in the beginning
        self.log_text.insert("1.0", time.strftime("%Y-%m-%d %H:%M:%S - ", current_time_struct) + message + "\n")
        self.log_text.config(state=tk.DISABLED)

    def update_logs(self):
        if (self.watch_list_opend):
            self.update_exchange_logs(self.binance)

            for key, value in self.watch_list.widgets['symbol'].items():
                symbol = self.watch_list.widgets['symbol'][key].cget("text")
                exchange = self.watch_list.widgets['exchange'][key].cget("text")

                if exchange == "Binance" and symbol in self.binance.contracts:
                    self.update_watch_list_prices(symbol, self.binance, key)

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

        # Logs
        for log in self.binance.logs:
            if not log['displayed']:
                self.log_in_frame.add_log_message(log['log'])
                log['displayed'] = True

        # Trades and Logs
        for client in [self.binance]:

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
                            precision = 8

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

    def open_temp_frame(self, main_interface: tk.Frame, on_close=None):
        def on_window_close():
            main_interface.log_in_frame.watch_list_button.config(stat=tk.NORMAL)
            self.watch_list_opend = False
            if on_close:
                on_close()
            window.destroy()

        window = tk.Toplevel(main_interface)
        window.config(bg=self.bg)
        window.protocol("WM_DELETE_WINDOW", on_window_close)
        # Disable window resizing (both width and height)
        window.resizable(width=False, height=False)

        self.watch_list = WatchList(window, binance_contracts=self.binance.contracts,
                                   bg_color=self.bg,
                                    fg_color=self.fg)
        self.watch_list.grid(row=0, column=0, sticky="nsew")
        self.watch_list.lift()  # Raise the WatchList widget to the top

        self.update_logs()

    def run_timer(self):

        self.timer = threading.Timer(10, self.run_timer)
        self.timer.start()
        if self.watch_list_opend:
            # Call your function
            self.save_workspace()

    def save_workspace(self):
        watchlist_symbols = []

        for key, value in self.watch_list.widgets['symbol'].items():
            symbol = value.cget("text")
            exchange = self.watch_list.widgets['exchange'][key].cget("text")

            watchlist_symbols.append((symbol, exchange,))

        self.watch_list.db.save("watchlist", watchlist_symbols)

