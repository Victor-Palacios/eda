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
  _build_notebooks.py      generator script (re-run to rebuild notebooks)
```

## Running

```bash
pip install pandas matplotlib jupyter
jupyter lab
```

Open any notebook in `notebooks/` and **run the first code cell first** — it
injects CSS so all text (markdown, code, and outputs) renders at a minimum
of 24px, which is suitable for live classroom display.

## Rebuilding the notebooks

Notebook content is generated from `notebooks/_build_notebooks.py`. If you
edit the script, regenerate with:

```bash
python notebooks/_build_notebooks.py
```

## Coverage so far

| Bias | Dataset | Notebook |
|---|---|---|
| Datasaurus / always plot | `data/always_plot_demo.csv` | `01_datasaurus_always_plot.ipynb` |
| Simpson's Paradox | `data/simpsons_paradox_treatment.csv` | `02_simpsons_paradox.ipynb` |
| Survivorship bias | `data/startup_survivorship.csv` | `03_survivorship_bias.ipynb` |
| Gaming whales / outliers | `data/gaming_outliers.csv` | `04_gaming_whales_outliers.ipynb` |

Additional bias modules from the slide deck (collider bias, regression to
the mean, misleading variables, capstone) can be added once their CSVs are
available — drop them into `data/` and extend `_build_notebooks.py`.
