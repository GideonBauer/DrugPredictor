import pandas as pd

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
import joblib

from sklearn.impute import SimpleImputer

df = pd.read_csv("chem_bact_inhibition.csv")     # or your file
feature_cols = ["ACA_class", "complexity", "mol_weight",
                "TPSA", "volume", "hydrophobicity"]

target_cols  = [c for c in df.columns if c.startswith("inh_")]  # 40 cols
X = df[feature_cols]
Y = df[target_cols]            # shape (1000, 40)


categorical = ["ACA_class"]
numeric     = ["complexity", "mol_weight", "TPSA", "volume", "hydrophobicity"]


preprocess = ColumnTransformer([
    # ---- categorical branch ----
    ("cat", Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ]), categorical),

    # ---- numeric branch ----
    ("num", Pipeline([
        ("impute", SimpleImputer(strategy="mean")),
        ("scale",  StandardScaler())
    ]), numeric)
])


na_counts = df[target_cols].isna().sum().sort_values(ascending=False)
print(na_counts.head(10))          # see the worst offenders
print("Total rows with ≥1 NaN in Y:", df[target_cols].isna().any(axis=1).sum())


rf = RandomForestRegressor(
        n_estimators=400,      # number of trees
        max_depth=None,        # let trees grow; tune if you over‑fit
        n_jobs=-1,             # use all CPU cores
        random_state=42
)

model = Pipeline([
    ("prep", preprocess),
    ("rf",   rf)
])


X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size=0.2, random_state=1
)

model.fit(X_train, Y_train)

cv_r2 = cross_val_score(model, X, Y, cv=5, scoring="r2")
print("5‑fold mean R²:", cv_r2.mean(), "±", cv_r2.std())


Y_pred = model.predict(X_test)                 # shape (n_test, 40)

# Overall metrics (uniform average across outputs)
print("R² :", r2_score(Y_test, Y_pred, multioutput="uniform_average"))
print("MAE:", mean_absolute_error(Y_test, Y_pred, multioutput="uniform_average"))

# Per‑bacterium R² (optional detail)
r2_each = r2_score(Y_test, Y_pred, multioutput="raw_values")
for name, r2 in zip(target_cols, r2_each):
    print(f"{name:12s}  R² = {r2:5.2f}")

joblib.dump(model, "rf_multi_bacteria.joblib")
# ...
loaded = joblib.load("rf_multi_bacteria.joblib")
new_pred = loaded.predict(X_new)   # X_new must have same feature schema


new_drug = pd.DataFrame([{
    "ACA_class": "Type‑III",
    "complexity": 450,
    "mol_weight": 310.4,
    "TPSA": 75.0,
    "volume": 287.0,
    "hydrophobicity": 2.3
}])

predicted_inhib = loaded.predict(new_drug)[0]   # length‑40 vector
profile = dict(zip(target_cols, predicted_inhib))

