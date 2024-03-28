import tkinter as tk

from connectors.bitmex import BitmexClient
from connectors.binance import BinanceClient
from UI.ui_trade import TradingFrame
from UI.ui_log import LogFrame
#from UI.ui_watchlist import WatchList
from UI.ui_strategy import StrategyFrame
class interface(tk.Tk):
    def __init__(self, bitmex: BitmexClient, binance: BinanceClient):
            super().__init__()

            self.bitmex = bitmex
            self.binance = binance

            self.bg_color = "Black"
            self.fg_color = "White"
            self.color_button_text = "Light Mode"
            self.title("trading")
            self.config(bg=self.bg_color)

            # Configure row weights
            self.grid_rowconfigure(0, weight=9)  # Top row takes 9/10 of the space
            self.grid_rowconfigure(1, weight=1)  # Bottom row takes 1/10 of the space

            # Configure column weights
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)

            self.top_frame = tk.Frame(self, bg=self.bg_color)
            self.top_frame.grid(row=0, column=1, sticky="nsew")

            self.Strategy_frame = StrategyFrame(self, self.top_frame, bitmex=self.bitmex, binance=self.binance,
                                                bg_color=self.bg_color, fg_color=self.fg_color)
            self.Strategy_frame.grid(row=0, column=0, sticky="nsew")  # Updated row index to 0

            self.trade_frame = TradingFrame(self.top_frame, bg_color=self.bg_color, fg_color=self.fg_color, )
            self.trade_frame.grid(row=1, column=0, sticky="nsew")  # Updated row index to 1

            self.top_frame.grid_rowconfigure(0, weight=1)
            self.top_frame.grid_rowconfigure(1, weight=1)  # Added row configuration for index 1
            self.top_frame.grid_columnconfigure(0, weight=1)  # Updated column index to 0

            self.bottom_frame = tk.Frame(self, bg=self.bg_color)
            self.bottom_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

            self.log_frame = LogFrame(self,self.bottom_frame, bg_color=self.bg_color, fg_color=self.fg_color,
                                      color_button_text= self.color_button_text)
            self.log_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")

            self.bottom_frame.grid_rowconfigure(0, weight=1)
            self.bottom_frame.grid_columnconfigure(0, weight=1)

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
        self.top_frame.config(bg=self.bg_color)
        self.bottom_frame.config(bg=self.bg_color)
        self.Strategy_frame.config(bg=self.bg_color)
        self.trade_frame.config(bg=self.bg_color)
        self.log_frame.update_color(new_bg_color=self.bg_color, new_fg_color=self.fg_color,
                                       new_button_text=self.color_button_text)
        self.Strategy_frame.update_color(new_bg_color=self.bg_color, new_fg_color=self.fg_color)
        self.trade_frame.update_color(new_bg_color=self.bg_color, new_fg_color=self.fg_color)