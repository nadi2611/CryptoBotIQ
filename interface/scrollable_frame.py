import tkinter as tk

class ScrollFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.canvas = tk.Canvas(self, highlightthickness=0, **kwargs)
        self.vsb = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.frame = tk.Frame(self.canvas, **kwargs)

        self.frame.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.frame.bind("<Enter>", lambda event: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.frame.bind("<Leave>", lambda event: self.canvas.unbind_all("<MouseWheel>"))

        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def change_background_color(self, color):
        self.frame.config(background=color)
        self.canvas.configure(background=color)
        self.config(bg=color)