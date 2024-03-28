import tkinter as tk
from typing import Dict
from models import *
from database import WorkspaceData

BOLD_FONT = ("corbel", 10, "bold")
FONT = ("corbel", 10, "normal")


class WatchList(tk.Frame):
    def __init__(self,left_frame, binance_contracts: Dict[str, Contract], bitmex_contracts: Dict[str, Contract],
                 *args, **kwargs):

        self.bg: str = kwargs.pop('bg_color')
        self.fg: str = kwargs.pop('fg_color')

        super().__init__(*args, **kwargs)

        self.config(bg=self.bg)
        self.binance_keys = list(binance_contracts.keys())
        self.bitmex_keys = list(bitmex_contracts.keys())

        self.db = WorkspaceData()

        self.frame = tk.Frame(self, bg=self.bg)
        self.frame.pack(side=tk.TOP)

        self.table = tk.Frame(self, bg=self.bg)
        self.table.pack(side=tk.TOP)

        self.label_binance = tk.Label(self.frame, text="Binance", fg=self.fg, bg=self.bg, font=BOLD_FONT)
        self.label_bitmex = tk.Label(self.frame, text="Bitmex", fg=self.fg, bg=self.bg, font=BOLD_FONT)

        self.label_binance.grid(row=0, column=2)
        self.label_bitmex.grid(row=0, column=3)

        self.binance_entry = self.create_entry(self, parent=self.frame, column=2)
        self.bitmex_entry = self.create_entry(self, parent=self.frame, column=3)

        self.widgets = dict()
        self.headers = ["symbol", "exchange", "ask", "bid", "Delete"]

        self.body_index = 3

        self.bitmex_entry.bind("<Return>",  self.add_bitmex_symbol)
        self.binance_entry.bind("<Return>", self.add_binance_symbol)

        for index, i in enumerate(self.headers):
            if i != "Delete":
                tmp = tk.Label(self.frame, text=i, fg=self.fg, bg= self.bg, font=BOLD_FONT)
                tmp.grid(row=2, column=1+index)
            else:
                tmp = tk.Label(self.frame, text=i, fg=self.fg, bg="red4", font=BOLD_FONT)
                tmp.grid(row=2, column=index+1)

        self.all_labels=[]
        self.create_header_labels(self)

        for i in self.headers:
            self.widgets[i] = dict()
            if i in ["bid", "ask"]:
                self.widgets[f"var_{i}"] = dict()

        self.labels_info = [
            ('symbol',  str, 1),
            ('exchange', str, 2),
            ('bid', str, 3),
            ('ask', str, 4),
        ]

        saved_symbols = self.db.get("watchlist")

        for s in saved_symbols:
            self.add_symbol(s['symbol'], s['exchange'])

    @staticmethod
    def create_entry(self, parent, column: int):
        entry = tk.Entry(parent, bg=self.fg, fg=self.bg, justify=tk.CENTER, insertbackground="midnight blue")
        entry.grid(row=1, column=column)
        return entry

    @staticmethod
    def create_header_labels(self):
        for index, header in enumerate(self.headers):
            tmp_bg = "red4" if header == "Delete" else "Black"
            tmp = tk.Label(self.frame, text=header, fg=self.fg, bg=tmp_bg, font=BOLD_FONT)
            tmp.grid(row=2, column=index + 1)
            if header != "Delete":
                self.all_labels.append(tmp)

    def add_symbol(self, symbol: str, exchange: str):
        index = self.body_index

        self.widgets['var_bid'][index] = tk.StringVar()
        self.widgets['var_ask'][index] = tk.StringVar()

        labels_info = [
            ('symbol', symbol, 1),
            ('exchange', exchange, 2),
            ('bid', self.widgets['var_bid'][index], 3),
            ('ask', self.widgets['var_ask'][index], 4),
        ]

        for name, value, col in labels_info:
            label = tk.Label(self.frame, text=value if isinstance(value, str) else "",
                             textvariable=self.widgets['var_bid'][index] if not isinstance(value, str) else ""
                             ,font=FONT, fg=self.fg, bg=self.bg)
            label.grid(row=index, column=col)
            self.widgets[name][index] = label
            self.all_labels.append(label)

        delete_button = tk.Button(self.frame, command=lambda: self.delete_symbol(index),
                                  font=BOLD_FONT, fg="white", bg="red4", text="X")
        delete_button.grid(row=index, column=5)
        self.widgets['Delete'][index] = delete_button

        self.body_index += 1

    def add_binance_symbol(self, event):
        symbol = self.binance_entry.get()
        if symbol in self.binance_keys:
            self.add_symbol(symbol, "Binance")
            self.binance_entry.delete(0, tk.END)

    def add_bitmex_symbol(self, event):
        symbol = self.bitmex_entry.get()
        if symbol in self.bitmex_keys:
            self.add_symbol(symbol, "Bitmex")
            self.bitmex_entry.delete(0, tk.END)

    def delete_symbol(self, index :int):
        #print("in delete_symbol")
        #print(index)
        for i in self.headers:
            self.widgets[i][index].grid_forget()
            del self.widgets[i][index]

    def update_color(self, new_bg_color: str, new_fg_color: str):
        self.bg = new_bg_color
        self.fg = new_fg_color
        self.config(bg=self.bg)
        self.frame.config(bg=self.bg)
        self.table.config(bg=self.bg)
        self.label_binance.config(bg=self.bg, fg=self.fg)
        self.label_bitmex.config(bg=self.bg, fg=self.fg)
        #self.binance_entry.config(bg=self.fg, fg=self.bg)
       # self.bitmex_entry.config(bg=self.fg, fg=self.bg)

        for i in range (len(self.all_labels)):
            self.all_labels[i].config(bg=self.bg, fg=self.fg)



"""""""""
if __name__ == "__main__":
    root = tk.Tk()
    app = WatchList({}, {})
    app.pack()
    root.mainloop()
"""""""""