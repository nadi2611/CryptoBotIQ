import tkinter as tk
import threading
from tkinter.messagebox import askquestion
from connectors.bitmex import BitmexClient
from connectors.binance import BinanceClient
from UI.ui_trade import TradingFrame
from UI.ui_log import Login
from UI.ui_strategy import StrategyFrame
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

        self.run_timer()
        self.update_ui()

    def _proper_close(self):
        result = askquestion("Confirmation", "Do you really want to exit the application?")
        if result == "yes":
            self.binance.reconnect = False  # Avoids the infinite reconnect loop in _start_ws()
            self.bitmex.reconnect = False
            self.binance.ws.close()
            self.bitmex.ws.close()

            self.stop_timer()

            self.destroy()  # Destroys the UI and terminates the program as no other thread is running
    def run_timer(self):

        self.timer = threading.Timer(10, self.run_timer).start()
        # Call your function
        self.save_workspace()

    def stop_timer(self):
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

    def save_workspace(self):
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
            if strategy_type != "pick":
                for param in self.Strategy_frame.extra_params_dict[strategy_type]:
                    code_name = param['code_name']
                    extra_params[code_name] = self.Strategy_frame.additional_parameters[b_index][code_name]

            strategies.append((strategy_type, contract, timeframe, balance_pct, take_profit, stop_loss,
                               json.dumps(extra_params),))

            self.Strategy_frame.db.save("strategies", strategies)
            self.log_in_frame.add_log_message("Workspace saved")

    def update_ui(self):
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
        self.after(1500, self.update_ui)
