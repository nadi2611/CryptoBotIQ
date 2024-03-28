import tkinter as tk

from strategies import TechnicalStrategy, BreakoutStrategy
from utils import *
from UI.ui_scroll_frame import ScrollFrame
from connectors.bitmex import BitmexClient
from connectors.binance import BinanceClient

BOLD_FONT = ("Calibri", 11, "bold")
SMALL_FONT = ("corbel", 10, "bold")
FONT = ("corbel", 11, "normal")
WIDTH = 20

@staticmethod
def close_after_timeout(window):
    window.destroy()

@staticmethod
def open_temp_frame(main_interface: tk.Frame, message: str, bg_color: str):

    # Open a new frame for a limited time with message
    window = tk.Toplevel(main_interface)
    window.config(bg=bg_color)
    label = tk.Label(window, text=message,  bg=bg_color, fg="Black")
    label.pack(padx=30, pady=30)

    # Schedule the close after_timeout function to run after 2000 milliseconds (2 seconds)
    window.after(2000, lambda: close_after_timeout(window))

class StrategyFrame(tk.Frame):
    def __init__(self, main_interface, *args, **kwargs):

        bitmex = kwargs.pop('bitmex')
        binance = kwargs.pop('binance')
        self.bg: str = kwargs.pop('bg_color')
        self.fg: str = kwargs.pop('fg_color')
        super().__init__(*args, **kwargs)

        self.config(bg=self.bg)
        self.main_interface = main_interface
        self.exchanges = {"Binance": binance, "Bitmex": bitmex}
        self.all_contracts = []
        self.all_labels=[]

        #put all contarct in the same list
        for exchange, client in self.exchanges.items():
            for symbol, contract in client.contracts.items():
                self.all_contracts.append(exchange + '_' + symbol)

        self.frame = tk.Frame(self, bg="black")
        self.frame.pack(side=tk.TOP)

        self.add_strategy_button = tk.Button(self.frame, command=lambda: self.add_strategy(),
                                             font=BOLD_FONT, fg="White", bg="red4", text="Add Strategy")
        self.add_strategy_button.grid(row=0, column=0)  # Set grid position for the button

        self.table = tk.Frame(self, bg="black")
        self.table.pack(side=tk.TOP)

        self.scroll_frame = ScrollFrame(self, bg=self.bg, height=250)
        self.scroll_frame.pack(side=tk.TOP, anchor="nw", fill=tk.X)

        self.body_index = 1

        self.widgets = dict()

        self.headers = [{"name": "Contract", "width": 12}, {"name": "Strategy","width": 12},
                        {"name": "Timeframe","width": 10},{"name": "Balance [%]", "width": 10},
                        {"name": "Profit [%]", "width": 10}, { "name": "Stop Loss [%]", "width":  10}]

        self.strategies = ["Technical", "Breakout"]

        self.all_timeframes = ["1m", "5m", "15m", "30m", "1h", "2h"]

        self.params_dict = [
            {"name": "Contract", "widget": tk.OptionMenu, "data_type": str, "options": self.all_contracts,
                "width": 20},
            {"name": "strategy_type", "widget": tk.OptionMenu, "strategy_name": str,
             "options": self.strategies, "width": 15},
            {"name": "Timeframe", "widget": tk.OptionMenu, "data_type": "String", "options": self.all_timeframes,
                "width": 8},
            {"name": "Balance Percentage", "widget": tk.Entry, "data_type": float,  "width": 5},
            {"name": "Take Profit", "widget": tk.Entry, "data_type": float,  "width": 5},
            {"name": "Stop Loss", "widget": tk.Entry, "data_type": float,  "width": 5},
            {"name": "Parameters", "widget": tk.Button,  "bg":  self.bg,"text": "parameters",
             "action": self.popup, "color": "darkred"},
            {"name": "Activation", "widget": tk.Button,  "data_type": float, "action": self.switch_strategy,
                "text": "OFF", "color": "darkred"},
            {"name": "Delete", "widget": tk.Button,  "data_type": float, "action": self.delete_row,
                "text": "Delete", "color": "darkred"},
            ]

        self.extra_params_dict = {
            "Technical": [
                {"code_name": "rsi_length", "name": "RSI Periods", "widget": tk.Entry, "data_type": int},
                {"code_name": "ema_fast", "name": "MACD Fast Length", "widget": tk.Entry, "data_type": int},
                {"code_name": "ema_slow", "name": "MACD Slow Length", "widget": tk.Entry, "data_type": int},
                {"code_name": "ema_signal", "name": "MACD Signal Length", "widget": tk.Entry, "data_type": int},
            ],
            "Breakout": [
                {"code_name": "Minimum Volume", "name": "Minimum Volume", "widget": tk.Entry, "data_type": float},
            ]
        }
        self.additional_parameters = dict()
        self.extra_input = dict()

        for index, i in enumerate(self.headers):
            tmp = tk.Label(self.scroll_frame.frame, text=i["name"], bg=self.bg, fg=self.fg, font=BOLD_FONT, width=i["width"])
            tmp.grid(row=0, column=index)
            self.all_labels.append(tmp)

        for i in self.params_dict:
            self.widgets[i['name']] = dict()
            if i['name'] in ["strategy_type", "Contract", "Timeframe"]:
                    self.widgets['var_' + i['name']] = dict()

    def add_strategy(self):

        index = self.body_index

        for col, i in enumerate(self.params_dict):
            name = i['name']
            if i['widget'] == tk.OptionMenu:

                self.widgets["var_" + name][index] = tk.StringVar()

                # set the default text
                self.widgets["var_" + name][index].set("pick")

                self.widgets[name][index] = tk.OptionMenu(self.scroll_frame.frame,
                        self.widgets["var_" + name][index], *i['options'])
                self.widgets[name][index].config(width=i['width'], bg="white", fg="black")
               # self.widgets[name][index]["menu"].config(bg=self.bg, fg=self.fg)

            elif i['widget'] == tk.Entry:
                self.widgets[name][index] = tk.Entry(self.scroll_frame.frame, justify=tk.CENTER, bg="white", fg="black")

            elif i['widget'] == tk.Button:
                button_action = i.get('action', lambda _: None)
                self.widgets[name][index] = tk.Button(self.scroll_frame.frame, text=i['text'], bg="red4", fg="white",
                            command=lambda action=button_action, idx=index: action(idx))

            self.widgets[name][index].grid(row=index, column=col)

        self.additional_parameters[index] = dict()

        for startegy, params in self.extra_params_dict.items():
            for i in params:
                self.additional_parameters[index][i['code_name']] = None

        self.body_index += 1

    def delete_row(self, index: int):
        print(index)
        for i in self.params_dict:
            self.widgets[i['name']][index].grid_forget()
            del self.widgets[i['name']][index]

    def popup(self, index: int):

        #check if a strategy is picked
        if self.widgets["var_strategy_type"][index].get() == "pick":
            message = "Error: didn't pick in Statege Type "
            open_temp_frame(self.main_interface, message, bg_color="grey")
            self.main_interface.log_frame.add_log_message(message)
            return

        #the following two parametrs help us make the window next to the paramets button
        x, y = self.widgets["Parameters"][index].winfo_rootx(), self.widgets["Parameters"][index].winfo_rooty()

        self.window = tk.Toplevel(self, bg= self.bg, bd=10)
        self.window.title("Parameters")

        #window place
        self.window.geometry(f"+{x - 160}+{y + 25}")

        # Prevents interaction with other windows until this one is closed
        self.window.attributes("-topmost", True)
        self.window.grab_set()

        strategy_selected = self.widgets['var_strategy_type'][index].get()

        row = 0
        for param in self.extra_params_dict[strategy_selected]:
            code_name = param['code_name']

            temp_label = tk.Label(self.window, bg=self.bg, fg=self.fg, text=code_name, font=FONT)
            temp_label.grid(row=row, column=0)

            if param['widget'] == tk.Entry:
                entry_widget = tk.Entry(self.window, bg="white", justify=tk.CENTER, fg=self.bg,
                                        insertbackground="Black")



                default_value = self.additional_parameters[index].get(code_name)
                if default_value is not None:
                    entry_widget.insert(tk.END, str(default_value))

                self.extra_input[code_name] = entry_widget

            else:
                continue

            self.extra_input[code_name].grid(row=row, column=1)
            row += 1

        # now add the validation/add button
        add_button = tk.Button(self.window, text="add", bg="red4", fg="white",
                                      command=lambda: self.validate_parameters(index))
        add_button.grid(row=row, column=0, columnspan=2)

    def validate_parameters(self, index: int):
        strategy_selected = self.widgets['var_strategy_type'][index].get()

        for param in self.extra_params_dict[strategy_selected]:
            code_name = param['code_name']
            input_value = self.extra_input[code_name].get()

            if not input_value:
                self.additional_parameters[index][code_name] = None
            else:
                self.additional_parameters[index][code_name] = param['data_type'](input_value)

        # Close the window
        self.window.destroy()


    def switch_strategy(self, index: int):

        for i in ["var_Contract","var_strategy_type", "var_Timeframe"]:
            strategy_selected = self.widgets[i][index].get()
            if strategy_selected == "pick":
                temp_list = i.split('_')
                y: str
                if len(temp_list) == 3:
                    y = temp_list[2]

                x: str = temp_list[1]
                if len(temp_list) == 3:
                    message = f"Error: didn't pick in {x.capitalize()} {y.capitalize()}"
                    open_temp_frame(self.main_interface, message, bg_color="grey" )
                    self.main_interface.log_frame.add_log_message(message)

                else :
                    message = f"Error: didn't pick in {x.capitalize()}"
                    open_temp_frame(self.main_interface, message,  bg_color="grey")
                    self.main_interface.log_frame.add_log_message(message)

                return

        strategy_selected = self.widgets["var_strategy_type"][index].get()

        #check if all peramerters are set , if not display an error message in log
        for i in ["Balance Percentage", "Take Profit", "Stop Loss"]:
            if self.widgets[i][index].get() == "":
                self.main_interface.log_frame.add_log_message(f"Error: missing {i.lower()} parameter")
                return

            #loop throw extra parameters strategy to make sure the are all filed
            for i in self.extra_params_dict[strategy_selected]:
                if self.additional_parameters[index][i['code_name']] is None:
                    self.main_interface.log_frame.add_log_message(f"Error: missing {i['name']} parameter")
                    return

        # get the information
        tmp = self.widgets['var_Contract'][index].get().split("_")
        print(self.widgets['var_Contract'][index].get())
        symbol = tmp[1]
        exchange = tmp[0]
        print(symbol)
        print(exchange)
        timeframe = self.widgets['var_Timeframe'][index].get()
        contract = self.exchanges[exchange].contracts[symbol]
        balance_pct = float(self.widgets['Balance Percentage'][index].get())
        take_profit = float(self.widgets['Take Profit'][index].get())
        stop_loss = float(self.widgets['Stop Loss'][index].get())

        # check if the button is off Or ON
        if self.widgets['Activation'][index].cget("text") == "OFF":
            #the button was off, therefore we want to activate the strategy
            # we also want to deactivate the writing to the other entries+-

            if strategy_selected == "Technical":
                new_strategy = TechnicalStrategy(self.exchanges[exchange], contract, exchange, timeframe, balance_pct,
                                                 take_profit, stop_loss, self.additional_parameters[index])

            # strategy_selected == "Breakout":
            else:
                new_strategy = BreakoutStrategy(self.exchanges[exchange], contract, exchange, timeframe, balance_pct,
                                                take_profit, stop_loss, self.additional_parameters[index])

            # Collects historical data. It is just one API call so that is ok, but be careful not to call methods
            # that would lock the UI for too long.
            # For example don't make a query to a database containing billions of rows, your interface_old would freeze.

            new_strategy.candles = self.exchanges[exchange].get_historical_candles(contract, timeframe)

            if len(new_strategy.candles) == 0:
                self.main_interface.log_frame.add_log_message(f"There is no historical data retrieved for {contract.symbol}")
                return

            if exchange == "Binance":
                self.exchanges[exchange].subscribe_channel([contract], "aggTrade")
                self.exchanges[exchange].subscribe_channel([contract], "bookTicker")

            self.exchanges[exchange].strategies[index] = new_strategy
            for i in self.params_dict:
                name = i["name"]

                if name != "Activation" and "var_" not in name:
                    self.widgets[name][index].config(stat=tk.DISABLED)

                self.widgets["Activation"][index].config(bg="green", text="ON")

            self.widgets['Activation'][index].config(bg="darkgreen", text="ON")
            self.main_interface.log_frame.add_log_message(f"{strategy_selected} strategy on {symbol} - started")


        else:
            # The button was on, therefore we want to deactivate the strategy
            del self.exchanges[exchange].strategies[index]

            for i in self.params_dict:
                name = i["name"]

                if name != "Activation" and "var_" not in name:
                    self.widgets[name][index].config(stat=tk.NORMAL)

                self.widgets["Activation"][index].config(bg="darkred", text="OFF")
            self.main_interface.log_frame.add_log_message(f"{strategy_selected} strategy on {symbol} - stopped")

    def update_color(self, new_bg_color: str, new_fg_color: str):
        self.bg = new_bg_color
        self.fg = new_fg_color
        print("in update color")
        self.config(bg=self.bg)
        self.frame.config(bg=self.bg)
        self.table.config(bg=self.bg)
        self.scroll_frame.change_background_color(color=self.bg)

        for i in range(len(self.all_labels)):
            self.all_labels[i].config(bg=self.bg, fg=self.fg)
