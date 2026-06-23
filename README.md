# Pandas EDA Through Bias Stories — Workshop Notebooks

Beginner-friendly Pandas EDA, taught through memorable bias stories. Each
bias gets its own Jupyter notebook so you can walk through it with students
one concept at a time.

## Layout

Material is organized one folder per **day**. Each day holds its own
`data/` and `notebooks/`.

```
Data Cleaning and Exploratory Data Analysis/   <- Day 1
  data/                    datasets used by the notebooks (varied formats)
  notebooks/               one notebook per bias type
    01_datasaurus_always_plot.ipynb
    02_simpsons_paradox.ipynb
    03_survivorship_bias.ipynb
    04_gaming_whales_outliers.ipynb
    05_collider_bias.ipynb
    06_regression_to_mean.ipynb
    07_misleading_variables.ipynb
    _build_notebooks.py    generator script (re-run to rebuild notebooks)
```

Future days will be added as sibling top-level folders.

## Running

```bash
pip install pandas matplotlib jupyter
cd "Data Cleaning and Exploratory Data Analysis"
jupyter lab
```

Open any notebook in `notebooks/`. Every markdown cell is wrapped in an
inline-styled `<div style="font-size: 24px; line-height: 1.6;">` so the
narration text renders at 24px+ in every notebook environment
(JupyterLab, classic Jupyter, VS Code, Colab, nbviewer, GitHub preview,
and HTML export) — no CSS injection required.

For the **code editor and output** font size, use the host application:

- JupyterLab: *Settings → Theme → Increase Code Font Size*
- VS Code: workspace setting `editor.fontSize` and `notebook.markup.fontSize`
- Browser zoom (Ctrl/Cmd + `+`) bumps everything at once and works anywhere.

## Rebuilding the notebooks

Notebook content is generated from `_build_notebooks.py` inside each day's
`notebooks/` folder. If you edit the script, regenerate with:

```bash
python "Data Cleaning and Exploratory Data Analysis/notebooks/_build_notebooks.py"
```

## Coverage

Each notebook opens with a **different** pandas reader so students see
the breadth of formats pandas can handle. Datasaurus stays on CSV as
the baseline.

| Bias | Dataset | Reader | Notebook |
|---|---|---|---|
| Datasaurus / always plot | `data/always_plot_demo.csv` | `pd.read_csv` | `01_datasaurus_always_plot.ipynb` |
| Simpson's Paradox | `data/simpsons_paradox_treatment.xlsx` | `pd.read_excel` | `02_simpsons_paradox.ipynb` |
| Survivorship bias | `data/startup_survivorship.json` | `pd.read_json` | `03_survivorship_bias.ipynb` |
| Gaming whales / outliers | `data/gaming_outliers.parquet` | `pd.read_parquet` | `04_gaming_whales_outliers.ipynb` |
| Collider bias | `data/collider_admissions.feather` | `pd.read_feather` | `05_collider_bias.ipynb` |
| Regression to the mean | `data/regression_to_mean_scores.pkl` | `pd.read_pickle` | `06_regression_to_mean.ipynb` |
| Misleading variables / leakage | `data/misleading_variables_churn.html` | `pd.read_html` | `07_misleading_variables.ipynb` |

A CSV copy of `misleading_variables_churn` is also kept under `data/`
because notebooks 03 and 06 reference it as a secondary example.

### Extra dependencies

Beyond `pandas` and `matplotlib`, the varied formats need:

```bash
pip install openpyxl pyarrow lxml html5lib
```

(`openpyxl` for `.xlsx`, `pyarrow` for Parquet/Feather, `lxml` +
`html5lib` for `read_html`. JSON, pickle, and CSV are built into pandas.)
