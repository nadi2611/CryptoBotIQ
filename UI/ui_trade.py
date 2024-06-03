import tkinter as tk
from models import Trade
from UI.ui_scroll_frame import ScrollFrame
import datetime

BOLD_FONT = ("Calibri", 16, "bold")
FONT = ("corbel", 12, "normal")
WIDTH = 12

class TradingFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        self.bg: str = kwargs.pop('bg_color')
        self.fg: str = kwargs.pop('fg_color')
        super().__init__(*args, **kwargs)

        self.body_widgets = dict()
        self.headers = ["time", "symbol", "exchange", "strategy", "side", "size", "status", "pnl"]

        self.table_frame = tk.Frame(self, bg=self.bg)
        self.table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.headers_frame = tk.Frame(self.table_frame, bg=self.bg)
        self.headers_frame.pack(side=tk.TOP, fill=tk.X)

        self.all_labels = []
        for idx, h in enumerate(self.headers):
            header = tk.Label(self.headers_frame, text=h.capitalize(), bg=self.bg,
                              fg=self.fg, font=FONT, width=WIDTH)
            header.pack(side=tk.LEFT)
            self.all_labels.append(header)

#header = tk.Label(self.headers_frame, text="", bg=self.bg,
 #                         fg=self.fg, font=FONT, width=2)
 #       header.pack(side=tk.LEFT)
 #       self.all_labels.append(header)

        self.body_frame = ScrollFrame(self, bg=self.bg, height=250)
        self.body_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        for h in self.headers:
            self.body_widgets[h] = dict()
            if h in ["status", "pnl", "size"]:
                self.body_widgets[h + "_var"] = dict()

        self.body_index = 0

    def add_trade(self, trade: Trade):
        index = self.body_index
        t_index = trade.time  # Assuming trade.time is the unique identifier

        # Data for labels
        labels_data = [
            ('time', datetime.datetime.fromtimestamp(trade.time / 1000).strftime("%b %d %H:%M"), 13),
            ('symbol', trade.contract.symbol, 13),
            ('exchange', trade.contract.exchange.capitalize(), 13),
            ('strategy', trade.strategy, 13),
            ('side', trade.side.capitalize(), 12),
        ]

        for col, (key, value , width) in enumerate(labels_data):
            label = tk.Label(self.body_frame.frame, text=value, bg=self.bg, fg=self.fg, font=FONT,
                             width=width, anchor="w")
            label.grid(row=index, column=col+1, sticky="nsew")
            self.body_widgets[key][t_index] = label
            self.all_labels.append(label)

        self.body_widgets['size_var'][
            t_index] = tk.StringVar()  # Variable because the order is not always filled immediately
        self.body_widgets['size'][t_index] = tk.Label(self.body_frame.frame,
                                                          textvariable=self.body_widgets['size_var'][t_index],
                                                          bg=self.bg, fg=self.fg, font=FONT, width=WIDTH, anchor="w")

        self.body_widgets['size'][t_index].grid(row=index, column=6, sticky="nsew")
        self.all_labels.append(self.body_widgets['size'][t_index])

        # Status

        self.body_widgets['status_var'][t_index] = tk.StringVar()
        self.body_widgets['status'][t_index] = tk.Label(self.body_frame.frame,
                                                        textvariable=self.body_widgets['status_var'][t_index],
                                                        bg=self.bg, fg=self.fg, font=FONT, width=WIDTH, anchor="w")
        self.body_widgets['status'][t_index].grid(row=index, column=7, sticky="nsew")
        self.all_labels.append(self.body_widgets['status'][t_index])

        # PNL

        self.body_widgets['pnl_var'][t_index] = tk.StringVar()
        self.body_widgets['pnl'][t_index] = tk.Label(self.body_frame.frame,
                                                     textvariable=self.body_widgets['pnl_var'][t_index], bg=self.bg,
                                                     fg=self.fg, font=FONT, width=WIDTH, anchor="w")
        self.body_widgets['pnl'][t_index].grid(row=index, column=8, sticky="nsew")
        self.all_labels.append(self.body_widgets['pnl'][t_index])
        self.body_index += 1

    def update_color(self, new_bg_color: str, new_fg_color: str):
        self.bg = new_bg_color
        self.fg = new_fg_color
        self.config(bg=self.bg)
        self.headers_frame.config(bg=self.bg)
        self.table_frame.config(bg=self.bg)
        self.body_frame.config(bg=self.bg)

        for label in self.all_labels:
            label.config(bg=self.bg, fg=self.fg)

        self.body_frame.change_background_color(color=self.bg)
