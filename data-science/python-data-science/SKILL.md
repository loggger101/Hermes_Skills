---
name: python-data-science
description: "Python DS: EDA, cleaning, modeling, eval, viz."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [data-science, python, pandas, numpy, scikit-learn, EDA, modeling, visualization, experiment-tracking, reproducibility]
    category: data-science
    related_skills: [weights-and-biases, huggingface-trackio, systematic-debugging, test-driven-development]
---

# Python Data Science Workflow

A practical end-to-end guide for Python-based data science: from raw data to evaluated model, with tracking and reproducibility baked in.

## When to Use

- Exploratory data analysis on a new dataset
- Data cleaning / preprocessing pipelines
- Feature engineering and selection
- Training and evaluating ML models (scikit-learn, XGBoost, etc.)
- Comparing model variants and logging results
- Producing visualizations for reports/decks
- Setting up reproducible analysis notebooks

**Don't use** for pure engineering work (use `requesting-code-review` + `test-driven-development`) or for deep-learning training loops that need W&B sweeps (use `weights-and-biases` directly).

## Pipeline Overview

```
inspect → EDA → clean → feature eng → split → model → evaluate → compare → report
```

Each stage has a concrete deliverable. Never skip a stage because "it's obvious" — the obvious stage is where silent data bugs live.

---

## Stage 0: Environment & Imports

### Verify the environment

```bash
python -c "import pandas, numpy, sklearn, matplotlib, seaborn; print('core OK')"
python -c "import xgboost; print('xgb', xgboost.__version__)" 2>/dev/null || echo "no xgboost"
python -c "import optuna; print('optuna OK')" 2>/dev/null || echo "no optuna"
```

### Standard imports for a data science session

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

import warnings
warnings.filterwarnings('ignore')   # notebook convenience only — remove for production scripts

sns.set_theme(style="whitegrid")
```

---

## Stage 1: Inspect

Before any analysis, answer: **what is this data, where did it come from, what does each column mean?**

```python
df = pd.read_csv("data.csv")

# Shape and types
print(df.shape)
print(df.dtypes)
print(df.info())

# First and last rows
display(df.head(3))
display(df.tail(3))

# Missingness
missing = df.isna().sum().sort_values(ascending=False)
print(f"\nRows: {len(df)}, Columns: {len(df.columns)}, Missing cells: {df.isna().sum().sum()}")
print(missing[missing > 0])

# Duplicate rows
print(f"Duplicate rows: {df.duplicated().sum()}")

# Cardinality of categoricals
for col in df.select_dtypes(include=['object', 'category']).columns:
    print(f"{col}: {df[col].nunique()} unique / {len(df)} rows")
```

**Deliverable**: a 1-paragraph summary of the dataset — source, row count, column count, what each column represents, known quality issues.

---

## Stage 2: Exploratory Data Analysis (EDA)

### Univariate summaries

```python
# Numeric columns — distribution + outliers
numeric = df.select_dtypes(include=['number'])
display(numeric.describe())

# Histograms for numeric columns (adapted to column count)
numeric.hist(bins=30, figsize=(12, 8), layout=(2, 3))
plt.tight_layout()
plt.show()

# Categorical value counts
for col in df.select_dtypes(include=['object', 'category']).columns:
    print(f"\n=== {col} ===")
    print(df[col].value_counts(dropna=False).head(10))
```

### Correlation and relationships

```python
# Numeric correlation matrix
corr = numeric.corr(numeric_only=True)
display(corr)

# Heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0)
plt.title("Correlation Matrix")
plt.show()

# Pairplot for a small subset
sns.pairplot(df[['col_a', 'col_b', 'col_c', 'target']], hue='target')
plt.show()
```

### Target analysis

Always start with the target — it defines everything that follows.

```python
# Classification target
print(df['target'].value_counts(normalize=True))
sns.countplot(x='target', data=df)
plt.show()

# Regression target
print(df['target'].describe())
sns.histplot(df['target'], bins=50, kde=True)
plt.show()
```

### Grouped analysis

```python
# Mean of numeric columns by category
df.groupby('category_col')[['num_a', 'num_b']].mean()

# Pivot table
df.pivot_table(values='target', index='cat_a', columns='cat_b', aggfunc='mean')
```

**Deliverable**: notes on distributions, outliers, correlations, class imbalance, and any data-quality surprises.

---

## Stage 3: Cleaning

Document every cleaning decision. Undocumented cleaning is unreproducible cleaning.

```python
clean = df.copy()

# 1. Drop duplicates (if semantically correct)
clean = clean.drop_duplicates()

# 2. Handle missing values — decide per column, not globally
clean['num_col'] = clean['num_col'].fillna(clean['num_col'].median())
clean['cat_col'] = clean['cat_col'].fillna(clean['cat_col'].mode()[0])

# 3. Drop unusable columns
clean = clean.drop(columns=['leaky_column', 'id_column'])

# 4. Type fixes
clean['date_col'] = pd.to_datetime(clean['date_col'], errors='coerce')
clean['cat_col'] = clean['cat_col'].astype('category')

# 5. Outlier handling — clip, caps, or remove; document why
Q1, Q3 = clean['num_col'].quantile([0.25, 0.75])
IQR = Q3 - Q1
clean['num_col_clipped'] = clean['num_col'].clip(Q1 - 1.5*IQR, Q3 + 1.5*IQR)
```

**Pitfall — leakage**: any column derived from the target or from future information must be removed before splitting. Check every column: "would I have this value at prediction time for a new row?"

**Deliverable**: a clean DataFrame and a list of what was changed and why.

---

## Stage 4: Feature Engineering

### Derived features

```python
# Date features
clean['year'] = clean['date_col'].dt.year
clean['month'] = clean['date_col'].dt.month
clean['day_of_week'] = clean['date_col'].dt.dayofweek

# Ratios and interactions
clean['ratio_a_b'] = clean['num_a'] / (clean['num_b'] + 1e-9)
clean['product_ab'] = clean['num_a'] * clean['num_b']

# Binning
clean['num_binned'] = pd.cut(clean['num_col'], bins=5, labels=False)
```

### Encoding categoricals

```python
# Low cardinality → one-hot
pd.get_dummies(clean, columns=['low_card_cat'], drop_first=True)

# High cardinality → target encoding (compute on training fold only)
```

### Scaling — fit on training data only

```python
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)   # NOT fit_transform
```

**Pitfall — fit on full data**: any transform that learns parameters (scaler, encoder, imputer) must be fit on training data only and applied to validation. Doing it on the full DataFrame before splitting is leakage.

**Deliverable**: a feature set and a written list of engineered features with rationale.

---

## Stage 5: Train / Validation Split

```python
from sklearn.model_selection import train_test_split, StratifiedKFold

# Classification: stratified split
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Regression: plain split
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Time-series: split by time, never shuffle
split_idx = int(len(df) * 0.8)
train = df.iloc[:split_idx]
val = df.iloc[split_idx:]
```

**Cross-validation**:

```python
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(model, X, y, cv=cv, scoring='roc_auc')
print(f"CV ROC-AUC: {scores.mean():.3f} ± {scores.std():.3f}")
```

**Deliverable**: a split with documented rationale and a fixed `random_state`.

---

## Stage 6: Modeling

### Baseline first

Always establish a baseline before trying anything fancy.

```python
from sklearn.dummy import DummyClassifier, DummyRegressor

# Classification baseline
dummy = DummyClassifier(strategy='stratified')
dummy.fit(X_train, y_train)
print(f"Baseline ROC-AUC: {roc_auc_score(y_val, dummy.predict_proba(X_val)[:, 1]):.3f}")

# Regression baseline
dummy = DummyRegressor(strategy='mean')
dummy.fit(X_train, y_train)
print(f"Baseline RMSE: {np.sqrt(mean_squared_error(y_val, dummy.predict(X_val))):.3f}")
```

### Model zoo

```python
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import xgboost as xgb

models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "Gradient Boosting": GradientBoostingClassifier(random_state=42),
    "XGBoost": xgb.XGBClassifier(random_state=42, eval_metric='logloss'),
}
```

### Train and evaluate each

```python
results = []
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_val)
    y_proba = model.predict_proba(X_val)[:, 1] if hasattr(model, 'predict_proba') else None

    results.append({
        "model": name,
        "accuracy": model.score(X_val, y_val),
        "roc_auc": roc_auc_score(y_val, y_proba) if y_proba is not None else None,
    })

results_df = pd.DataFrame(results).sort_values("roc_auc", ascending=False)
print(results_df)
```

---

## Stage 7: Evaluation

### Classification

```python
from sklearn.metrics import classification_report, confusion_matrix, roc_curve
from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay

print(classification_report(y_val, y_pred))

cm = confusion_matrix(y_val, y_pred)
ConfusionMatrixDisplay(cm).plot()
plt.show()

fpr, tpr, _ = roc_curve(y_val, y_proba)
RocCurveDisplay(fpr=fpr, tpr=tpr, roc_auc=roc_auc_score(y_val, y_proba)).plot()
plt.show()
```

### Regression

```python
from sklearn.metrics import mean_absolute_error, r2_score

print(f"RMSE: {np.sqrt(mean_squared_error(y_val, y_pred)):.3f}")
print(f"MAE:  {mean_absolute_error(y_val, y_pred):.3f}")
print(f"R²:   {r2_score(y_val, y_pred):.3f}")

residuals = y_val - y_pred
sns.scatterplot(x=y_pred, y=residuals)
plt.axhline(0, color='red', linestyle='--')
plt.xlabel("Predicted"); plt.ylabel("Residual")
plt.title("Residual Plot")
plt.show()

sns.histplot(residuals, bins=50, kde=True)
plt.title("Residual Distribution")
plt.show()
```

### Error analysis

```python
val_df = X_val.copy()
val_df['actual'] = y_val
val_df['predicted'] = y_pred
val_df['correct'] = val_df['actual'] == val_df['predicted']

wrong = val_df[~val_df['correct']]
print(wrong['category_col'].value_counts())
```

**Deliverable**: metrics table, diagnostic plots, and a written assessment of where the model succeeds and fails.

---

## Stage 8: Comparison & Tracking

### Manual comparison

```python
comparison = pd.DataFrame(results).sort_values("roc_auc", ascending=False)
display(comparison)
```

### With Weights & Biases

```python
import wandb
wandb.init(project="my-analysis", config={"model": "Random Forest", "n_estimators": 100})
wandb.log({"roc_auc": roc_auc, "accuracy": accuracy, "train_samples": len(X_train)})
wandb.finish()
```

See the `weights-and-biases` skill for sweeps and artifact logging.

### With Trackio

```python
import trackio
trackio.init(project="my-analysis", config={"model": "rf"})
trackio.log({"roc_auc": 0.87, "accuracy": 0.82})
trackio.finish()
```

See the `huggingface-trackio` skill for alert-based autonomous loops.

### Final model

```python
best = RandomForestClassifier(n_estimators=100, random_state=42)
best.fit(X_train, y_train)
# Evaluate on held-out test set ONCE — do not tune on it
```

---

## Stage 9: Visualization for Reports

### Clean, readable plots

```python
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(x='category', y='value', data=df, ax=ax)
ax.set_title("Value by Category")
ax.set_xlabel("Category"); ax.set_ylabel("Value")
plt.tight_layout()
plt.savefig("plots/category_values.png", dpi=150)
```

### Plot catalog

| Question | Plot |
|---|---|
| Distribution of numeric | histogram / KDE / box plot |
| Distribution of categorical | bar chart / count plot |
| Relationship: two numerics | scatter / hexbin / regression plot |
| Relationship: numeric ↔ categorical | box plot / violin / strip plot |
| Correlation | heatmap |
| Time trend | line plot |
| Composition | stacked bar (pie rarely) |
| Model comparison | bar chart of metrics |
| Confusion | confusion matrix heatmap |
| Residuals | scatter (predicted vs residual) + histogram |

### Seaborn quick reference

```python
sns.histplot(df['col'], bins=30, kde=True)           # distribution
sns.boxplot(x='cat', y='num', data=df)                # distribution by group
sns.scatterplot(x='a', y='b', hue='target', data=df) # relationship
sns.heatmap(df.corr(), annot=True, cmap='coolwarm')   # correlation
sns.countplot(x='cat', data=df)                       # frequency
sns.pairplot(df, hue='target')                        # multivariate teaser
sns.regplot(x='a', y='b', data=df)                    # scatter + fit line
sns.violinplot(x='cat', y='num', data=df)             # density by group
```

---

## Stage 10: Reproducibility

### Fixed seeds everywhere

```python
import random, numpy as np
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# sklearn models with random_state
RandomForestClassifier(random_state=42)
train_test_split(..., random_state=42)
```

### Environment capture

```python
import sys, pandas, numpy, sklearn
print(f"Python: {sys.version}")
print(f"pandas: {pandas.__version__}")
print(f"numpy: {numpy.__version__}")
print(f"sklearn: {sklearn.__version__}")
# pip freeze > requirements.txt
```

### Notebook hygiene

- One analysis = one notebook. Keep cells in execution order. Re-run from top before saving.
- Move reusable functions to `.py` modules and import them.
- Add a header cell: purpose, data source, date, author, key results.
- Don't leave exploratory debris — delete failed experiments or move to a separate notebook.

### Data versioning

- Don't modify the raw data file. Keep it read-only; write cleaned versions to new files.
- If the data changes, note the version/upstream commit in the analysis.
- For anything beyond a one-off, commit the data snapshot or record its source URL and retrieval date.

---

## Stage 11: From Notebook to Production

When an analysis graduates to a pipeline or service:

1. **Extract functions** from notebook cells into a `.py` module with docstrings and type hints.
2. **Replace global state** with explicit function arguments.
3. **Add tests** for the extracted functions (see `test-driven-development`).
4. **Wrap the pipeline** in a class or set of functions with a clear public API.
5. **Log, don't print** — use the `logging` module for production code.
6. **Handle config** explicitly — YAML/JSON config file, CLI arguments, or env vars, not hardcoded paths.
7. **Validate inputs** — check shapes, types, and ranges at entry points.

---

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| **Data leakage** | Suspiciously good validation scores | Audit every feature: available at prediction time? Computed from target? Split before transform? |
| **Silent NaN propagation** | Model trains but predictions are garbage | Check `df.isna().sum()` after every transformation step. |
| **Shuffling time series** | Great CV scores, terrible real performance | Split by time. Never shuffle chronological data. |
| **Class imbalance ignored** | 99% accuracy on 99:1 data | Use stratified splits, ROC-AUC/F1, class weights or resampling. |
| **Overfitting to validation** | Validation improves, test drops | Use CV. Hold out a final test set. Stop tuning when validation plateaus. |
| **Metric mismatch** | Optimizing accuracy when business needs recall | Pick the metric that matches the decision cost structure before training. |
| **Feature scaling on full data** | Leaky preprocessing | Fit scalers/encoders/imputers on training fold only. |
| **No baseline** | Can't tell if model adds value | Always train a DummyClassifier/DummyRegressor first. |
| **Plotting too late** | Can't explain weird results | Plot early and often during EDA, not just at the end. |
| **Undocumented cleaning** | Can't reproduce the analysis | Record every drop, fill, clip, and encode decision. |

---

## Quick Reference

| Task | Tool / Function |
|---|---|
| Load CSV | `pd.read_csv(path)` |
| Load Excel | `pd.read_excel(path, sheet_name=...)` |
| Load Parquet | `pd.read_parquet(path)` |
| Load JSON | `pd.read_json(path)` |
| Load from DB | `pd.read_sql(query, connection)` |
| Shape/types | `df.shape`, `df.dtypes`, `df.info()` |
| Missingness | `df.isna().sum()` |
| Describe numeric | `df.describe()` |
| Value counts | `df['col'].value_counts()` |
| Group by | `df.groupby('col')['num'].mean()` |
| Filter | `df[df['col'] > threshold]` |
| Split | `train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)` |
| Cross-val | `cross_val_score(model, X, y, cv=5, scoring='roc_auc')` |
| Classify | `model.fit(X_train, y_train); model.predict(X_val)` |
| Classify proba | `model.predict_proba(X_val)[:, 1]` |
| Regression metrics | `mean_squared_error`, `mean_absolute_error`, `r2_score` |
| Classification metrics | `accuracy_score`, `roc_auc_score`, `f1_score` |
| Confusion matrix | `confusion_matrix(y_true, y_pred)` |
| Plot distribution | `sns.histplot`, `sns.boxplot`, `sns.violinplot` |
| Plot relationship | `sns.scatterplot`, `sns.regplot`, `sns.pairplot` |
| Plot category | `sns.countplot`, `sns.barplot` |
| Plot correlation | `sns.heatmap(df.corr(), annot=True)` |
| Save plot | `plt.savefig(path, dpi=150, bbox_inches='tight')` |

---

## Verification Checklist

Before reporting results:

- [ ] Data source documented (URL, file path, retrieval date)
- [ ] Raw data untouched; cleaning applied to a copy
- [ ] Every cleaning decision written down
- [ ] No features that leak the target
- [ ] Split done before any fit/transform
- [ ] Baseline model trained and reported
- [ ] Metrics match the problem type (classification vs regression)
- [ ] Class imbalance addressed if present
- [ ] Validation strategy documented (single split / CV / time-based)
- [ ] Random seeds fixed
- [ ] Versions recorded (Python, pandas, sklearn)
- [ ] Plots labeled, titled, and legible at target size
- [ ] Results reproducible from the notebook/script alone
