import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass
from typing import List, Tuple
import joblib
import numpy as np

# -----------------------------
# Load trained Random‑Forest pipeline
# -----------------------------

# Path is relative to this script; adjust if you keep the model elsewhere.
MODEL_PATH = "rf_multi_bacteria.joblib"
try:
    _rf_pipeline = joblib.load(MODEL_PATH)
except FileNotFoundError:
    _rf_pipeline = None            # fallback for first‑time runs

# For display purposes – list your 40 bacteria column names in the same order
BACTERIA_COLUMNS = [f"inh_Bac{i+1}" for i in range(40)]

# -----------------------------
# Domain layer helpers
# -----------------------------

@dataclass
class DrugDescriptor:
    aca_class: str
    complexity: float
    mol_weight: float
    tpsa: float
    volume: float
    hydrophobicity: float

    def to_dataframe(self):
        """Return a 1‑row pandas DataFrame matching the training schema."""
        import pandas as pd
        return pd.DataFrame([{  # keys must match feature_cols used in training
            "ACA_class": self.aca_class,
            "complexity": self.complexity,
            "mol_weight": self.mol_weight,
            "TPSA": self.tpsa,
            "volume": self.volume,
            "hydrophobicity": self.hydrophobicity,
        }])


def predict_inhibition(drug: DrugDescriptor) -> np.ndarray:
    """Return a 40‑length vector of predicted % inhibition for the bacteria."""
    if _rf_pipeline is None:
        raise RuntimeError("Model file not found – train the model and save it as rf_multi_bacteria.joblib in the same folder.")
    return _rf_pipeline.predict(drug.to_dataframe())[0]   # shape (40,)


def summarize_bacteria(inhib_vec: np.ndarray, top_n: int = 3) -> List[Tuple[str, float]]:
    """Return the top‑n (bacterium, inhibition%) sorted descending."""
    idx_sorted = np.argsort(inhib_vec)[::-1]  # descending
    return [(BACTERIA_COLUMNS[i], float(round(inhib_vec[i], 1))) for i in idx_sorted[:top_n]]


def summarize_regions(inhib_vec: np.ndarray) -> Tuple[Tuple[str, float], Tuple[str, float]]:
    """Dummy stub – replace with real geo model if you have one.
    Uses average inhibition as a placeholder mapping to regions.
    """
    avg = inhib_vec.mean()
    # very naive mapping
    if avg > 70:
        most = ("Global", avg)
        least = ("None", 0.0)
    elif avg > 40:
        most = ("Europe", avg)
        least = ("Africa", avg * 0.3)
    else:
        most = ("N/A", avg)
        least = ("N/A", avg)
    return most, least

# -----------------------------
# GUI layer
# -----------------------------

class DrugPredictorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Drug Effect Predictor")
        self.configure(bg="#cbd5e1")
        self._build_layout()

    # ---------- UI construction ----------

    def _build_layout(self):
        self.columnconfigure((0,1,2), weight=1, uniform="col")
        self._build_left_panel()
        self._build_middle_panel()
        self._build_right_panel()

    def _build_left_panel(self):
        left = ttk.Frame(self, padding=10)
        left.grid(row=0, column=0, sticky="nsew")

        ttk.Label(left, text="Chemical traits", style="Heading.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")

        self.cmb_aca = ttk.Combobox(left, values=["Type‑I", "Type‑II", "Type‑III"], state="readonly")
        self._labeled_widget(left, "ACA class", self.cmb_aca, 1)
        self.cmb_aca.current(0)

        self.spn_complex = self._labeled_spinbox(left, "Complexity", 2)
        self.spn_mw      = self._labeled_spinbox(left, "Mol. weight", 3)
        self.spn_tpsa    = self._labeled_spinbox(left, "TPSA", 4)
        self.spn_volume  = self._labeled_spinbox(left, "Volume", 5)
        self.spn_logp    = self._labeled_spinbox(left, "Hydrophobicity", 6)

        ttk.Button(left, text="Predict", command=self._on_predict).grid(row=7, column=0, columnspan=2, pady=(15, 0))

    def _labeled_spinbox(self, parent, label_text, row):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky="w")
        spin = ttk.Spinbox(parent, from_=0, to=1000, width=8)
        spin.set(0)
        spin.grid(row=row, column=1, sticky="w", pady=4)
        return spin

    def _labeled_widget(self, parent, label_text, widget, row):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky="w")
        widget.grid(row=row, column=1, sticky="w", pady=4)

    def _build_middle_panel(self):
        mid = ttk.Frame(self, padding=10)
        mid.grid(row=0, column=1, sticky="nsew")
        ttk.Label(mid, text="Top inhibited bacteria", style="Heading.TLabel").pack(anchor="w", pady=(0, 10))
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

    def _on_predict(self):
        try:
            drug = DrugDescriptor(
                aca_class=self.cmb_aca.get(),
                complexity=float(self.spn_complex.get()),
                mol_weight=float(self.spn_mw.get()),
                tpsa=float(self.spn_tpsa.get()),
                volume=float(self.spn_volume.get()),
                hydrophobicity=float(self.spn_logp.get())
            )
        except ValueError:
            messagebox.showerror("Input error", "Please enter numeric values only.")
            return

        try:
            inhib_vec = predict_inhibition(drug)
        except RuntimeError as e:
            messagebox.showerror("Model not found", str(e))
            return

        top_bac = summarize_bacteria(inhib_vec)
        most, least = summarize_regions(inhib_vec)

        self.lbl_bacteria.config(text="\n".join(f"{b} – {v:.1f}%" for b, v in top_bac))
        self.lbl_most.config(text=f"{most[0]} – {most[1]:.1f}%")
        self.lbl_least.config(text=f"{least[0]} – {least[1]:.1f}%")

# -------------- Styling -----------------

def _setup_styles():
    style = ttk.Style()
    style.configure("Heading.TLabel", font=("Segoe UI", 12, "bold"))

# -------------- Entrypoint --------------

if __name__ == "__main__":
    _setup_styles()
    app = DrugPredictorApp()
    app.mainloop()
