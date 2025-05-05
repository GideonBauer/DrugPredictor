import tkinter as tk
from functools import partial

class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.resizable(False, False)        # window can't be stretched
        self._make_display()
        self._make_buttons()

    # ---------- UI pieces ----------
    def _make_display(self):
        self.expr = tk.StringVar()
        entry = tk.Entry(self, textvariable=self.expr, font=("Segoe UI", 20), bd=5,
                         relief=tk.RIDGE, justify="right", width=14)
        entry.grid(row=0, column=0, columnspan=4, padx=8, pady=8)

    def _make_buttons(self):
        buttons = [
            ("7","8","9","/"),
            ("4","5","6","*"),
            ("1","2","3","-"),
            ("0",".","=","+"),
        ]
        for r, row in enumerate(buttons, start=1):
            for c, char in enumerate(row):
                action = self._on_equal if char == "=" else partial(self._on_press, char)
                tk.Button(self, text=char, width=4, height=2,
                          font=("Segoe UI", 18), command=action
                ).grid(row=r, column=c, padx=4, pady=4)

        tk.Button(self, text="C", width=4, height=2, font=("Segoe UI", 18),
                  command=self._on_clear
        ).grid(row=5, column=0, columnspan=4, sticky="we", padx=4, pady=4)

    # ---------- callbacks ----------
    def _on_press(self, char):
        self.expr.set(self.expr.get() + char)

    def _on_clear(self):
        self.expr.set("")

    def _on_equal(self):
        try:
            result = eval(self.expr.get())
            self.expr.set(str(result))
        except Exception:
            self.expr.set("Error")

if __name__ == "__main__":
    Calculator().mainloop()
