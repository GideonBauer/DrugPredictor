import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from typing import List, Tuple
import random

# -----------------------------
# Domain layer (stubbed logic)
# -----------------------------

@dataclass
class DrugDescriptor:
    phenol_rings: int
    benzene_rings: int
    halogens: int
    tpsa: float  # Topological Polar Surface Area


def predict_bacteria(drug: DrugDescriptor) -> List[Tuple[str, float]]:
    """Return a list of (bacterium, % inhibition).
    This is a placeholder – replace with your real model.
    """
    candidates = ["X", "Y", "Z", "A", "B", "C"]
    random.shuffle(candidates)
    return [(name, round(random.uniform(10, 90), 1)) for name in candidates[:3]]


def predict_regions(drug: DrugDescriptor) -> Tuple[Tuple[str, int], Tuple[str, int]]:
    """Return (most_affected_region, least_affected_region) as (name, score).
    Placeholder implementation.
    """
    regions = ["Europe", "North America", "Asia", "Africa", "South America"]
    scores = {r: random.randint(0, 100) for r in regions}
    most = max(scores.items(), key=lambda x: x[1])
    least = min(scores.items(), key=lambda x: x[1])
    return most, least

# -----------------------------
# GUI layer
# -----------------------------

class DrugPredictorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Drug Effect Predictor")
        self.configure(bg="#cbd5e1")  # light bluish background
        self._build_layout()

    # ---------- UI construction ----------

    def _build_layout(self):
        # Use a single row, three columns grid
        self.columnconfigure(0, weight=1, uniform="col")
        self.columnconfigure(1, weight=1, uniform="col")
        self.columnconfigure(2, weight=1, uniform="col")

        self._build_left_panel()
        self._build_middle_panel()
        self._build_right_panel()

    def _build_left_panel(self):
        left = ttk.Frame(self, padding=10)
        left.grid(row=0, column=0, sticky="nsew")

        ttk.Label(left, text="Chemical traits", style="Heading.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")

        # Spinboxes and entry
        self.spn_phenol = self._labeled_spinbox(left, "Phenol rings", 1)
        self.spn_benzene = self._labeled_spinbox(left, "Benzene rings", 2)
        self.spn_halogens = self._labeled_spinbox(left, "Halogens", 3)

        ttk.Label(left, text="TPSA").grid(row=4, column=0, sticky="w")
        self.ent_tpsa = ttk.Entry(left, width=8)
        self.ent_tpsa.grid(row=4, column=1, sticky="w", pady=4)
        self.ent_tpsa.insert(0, "15")

        # Enter button
        ttk.Button(left, text="Enter", command=self._on_enter).grid(row=5, column=0, columnspan=2, pady=(15, 0))

    def _labeled_spinbox(self, parent, label_text, row):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky="w")
        spin = ttk.Spinbox(parent, from_=0, to=10, width=5)
        spin.set(0)
        spin.grid(row=row, column=1, sticky="w", pady=4)
        return spin

    def _build_middle_panel(self):
        mid = ttk.Frame(self, padding=10)
        mid.grid(row=0, column=1, sticky="nsew")

        ttk.Label(mid, text="Bacteria inhibited", style="Heading.TLabel").pack(anchor="w", pady=(0, 10))

        self.lbl_bacteria = ttk.Label(mid, text="–", justify="left")
        self.lbl_bacteria.pack(anchor="w")

    def _build_right_panel(self):
        right = ttk.Frame(self, padding=10)
        right.grid(row=0, column=2, sticky="nsew")

        ttk.Label(right, text="Most affected", style="Heading.TLabel").pack(anchor="w", pady=(0, 4))
        self.lbl_most = ttk.Label(right, text="–")
        self.lbl_most.pack(anchor="w", pady=(0, 10))

        ttk.Label(right, text="Least affected", style="Heading.TLabel").pack(anchor="w", pady=(0, 4))
        self.lbl_least = ttk.Label(right, text="–")
        self.lbl_least.pack(anchor="w")

    # ---------- Event handlers ----------

    def _on_enter(self):
        # Collect input values
        try:
            drug = DrugDescriptor(
                phenol_rings=int(self.spn_phenol.get()),
                benzene_rings=int(self.spn_benzene.get()),
                halogens=int(self.spn_halogens.get()),
                tpsa=float(self.ent_tpsa.get())
            )
        except ValueError:
            tk.messagebox.showerror("Input error", "Please enter numeric values only.")
            return

        # "Run" predictions (stubbed)
        bacteria = predict_bacteria(drug)
        most, least = predict_regions(drug)

        # Update UI
        self.lbl_bacteria.config(text="\n".join(f"{name} – {pct}%" for name, pct in bacteria))
        self.lbl_most.config(text=f"{most[0]} – {most[1]}")
        self.lbl_least.config(text=f"{least[0]} – {least[1]}")

# -------------- Styling -----------------

def _setup_styles():
    style = ttk.Style()
    # Use the system default theme, then tweak
    style.configure("Heading.TLabel", font=("Segoe UI", 12, "bold"))

# -------------- Entrypoint --------------

if __name__ == "__main__":
    _setup_styles()
    app = DrugPredictorApp()
    app.mainloop()
