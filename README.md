# Pandas EDA Through Bias Stories — Workshop Notebooks

Beginner-friendly Pandas EDA, taught through memorable bias stories. Each
bias gets its own Jupyter notebook so you can walk through it with students
one concept at a time.

## Layout

```
data/                      CSV datasets used by the notebooks
notebooks/                 one notebook per bias type
  01_datasaurus_always_plot.ipynb
  02_simpsons_paradox.ipynb
  03_survivorship_bias.ipynb
  04_gaming_whales_outliers.ipynb
  05_collider_bias.ipynb
  06_regression_to_mean.ipynb
  07_misleading_variables.ipynb
  _build_notebooks.py      generator script (re-run to rebuild notebooks)
```

## Running

```bash
pip install pandas matplotlib jupyter
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

Notebook content is generated from `notebooks/_build_notebooks.py`. If you
edit the script, regenerate with:

```bash
python notebooks/_build_notebooks.py
```

## Coverage

| Bias | Dataset | Notebook |
|---|---|---|
| Datasaurus / always plot | `data/always_plot_demo.csv` | `01_datasaurus_always_plot.ipynb` |
| Simpson's Paradox | `data/simpsons_paradox_treatment.csv` | `02_simpsons_paradox.ipynb` |
| Survivorship bias | `data/startup_survivorship.csv` | `03_survivorship_bias.ipynb` |
| Gaming whales / outliers | `data/gaming_outliers.csv` | `04_gaming_whales_outliers.ipynb` |
| Collider bias | `data/collider_admissions.csv` | `05_collider_bias.ipynb` |
| Regression to the mean | `data/regression_to_mean_scores.csv` | `06_regression_to_mean.ipynb` |
| Misleading variables / leakage | `data/misleading_variables_churn.csv` | `07_misleading_variables.ipynb` |
