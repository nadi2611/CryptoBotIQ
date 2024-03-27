import tkinter as tk
import time

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

        self.log_in_text = tk.Text(self, bg=self.bg, fg=self.fg, font=FONT, height=5, width=5, state=tk.DISABLED)
        self.log_in_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.add_color_button = tk.Button(self, command=lambda: self.change_color_button(main_interface),
                                          font=FONT, fg=self.fg, bg=self.bg, text=self.button_text)

        # Use anchor and justify to align the button to the top right corner
        # anchor=tk.NE to make the button anchor to the top-right corner
        self.add_color_button.place(relx=1.0, rely=0.0, anchor=tk.NE)
    def change_color_button(self, main_interface):
        main_interface.update_color()

    def update_color(self, new_bg_color: str, new_fg_color: str,
                                       new_button_text: str):
        self.bg = new_bg_color
        self.fg = new_fg_color
        self.button_text = new_button_text
        self.config(bg=self.bg)
        self.log_in_text.config(bg=self.bg)
        self.add_color_button.config(bg=self.bg, fg=self.fg, text=self.button_text)

    def add_log_message(self, message: str):
        self.log_in_text.config(state=tk.NORMAL, bg=self.bg, fg="red4")

        current_time_seconds = time.time()

        # Convert the time to a struct_time object
        current_time_struct = time.gmtime(current_time_seconds)

        # the first argument ("1.0") indicates the message will be added in the beginning
        self.log_in_text.insert("1.0", time.strftime("%Y-%m-%d %H:%M:%S - ", current_time_struct) + message + "\n")
        self.log_in_text.config(state=tk.DISABLED)


