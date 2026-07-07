"""Generate one Jupyter notebook per bias type from the workshop slide content.

Run from the repo root or from this directory:
    python notebooks/_build_notebooks.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

DAY_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = DAY_DIR / "data"
IMAGES_DIR = DAY_DIR / "images"

# Each markdown cell is wrapped in this block-level div so the rendered text
# is large in every notebook renderer (JupyterLab, classic Jupyter, VS Code,
# Colab, nbviewer, GitHub preview, HTML export). Per CommonMark, blank lines
# inside an HTML block let markdown render normally between the tags, so
# headers / lists / fenced code still work.
MD_WRAP_OPEN = '<div style="font-size: 24px; line-height: 1.6;">\n\n'
MD_WRAP_CLOSE = '\n\n</div>'


def md(source: str) -> dict:
    """Markdown cell wrapped in a large-font div."""
    wrapped = MD_WRAP_OPEN + source.strip() + MD_WRAP_CLOSE
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": wrapped.splitlines(keepends=True),
    }


def code(source: str) -> dict:
    """Code cell (empty outputs, ready to run)."""
    return {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": source.splitlines(keepends=True) or [""],
    }


def notebook(cells: list[dict]) -> dict:
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "pygments_lexer": "ipython3",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def setup_cells(title: str, subtitle: str, hook_image: str | None = None) -> list[dict]:
    """Common opening cells: title and imports.

    Markdown cells use an inline-styled wrapper for large font (see `md`).
    Code-editor font size cannot be reliably set per-notebook across
    JupyterLab / VS Code / Colab — use the host application's settings or
    browser zoom for that.

    If `hook_image` (a notebook-relative path) is given, it is embedded right
    under the subtitle as a visual hook.
    """
    title_src = f"# {title}\n\n## {subtitle}"
    if hook_image:
        title_src += f"\n\n![{title}]({hook_image})"
    return [
        md(title_src),
        md("### Imports"),
        code(
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n"
            "\n"
            "plt.rcParams['font.size'] = 16\n"
            "plt.rcParams['figure.figsize'] = (8, 5)"
        ),
    ]


# ---------------------------------------------------------------------------
# Notebook 0: Inspect & Clean (the poisoned dataset)
# ---------------------------------------------------------------------------
inspect_cells = (
    setup_cells(
        "Garbage In, Garbage Out & Poisoned Data",
        "A single stray row can poison a whole column",
        hook_image="../images/data_poisoning.png",
    )
    + [
        md(
            "## The story\n\n"
            "Before any analysis, open the file and look at it. A single "
            "leftover row — like a stray `test` row — can quietly change a "
            "numeric column into text. This notebook builds the habit of "
            "inspecting and cleaning *before* you compute anything."
        ),
        md(
            "## 1. Load the evidence with `pd.read_csv()`\n\n"
            "`pd.read_csv()` turns a plain text file of comma-separated "
            "values into a **DataFrame** — the table object every other "
            "pandas function operates on. Nothing can be inspected until "
            "the file is a DataFrame."
        ),
        code('df = pd.read_csv("../data/always_plot_demo.csv")'),
        md(
            "## 2. First glance with `df.head()`\n\n"
            "`head()` shows the first five rows — the fastest sanity check "
            "that the file loaded correctly, and your first look at what "
            "the columns actually contain."
        ),
        code("df.head()"),
        md(
            "## 3. Last glance with `df.tail()`\n\n"
            "Catch weird endings, appended notes, or format changes. "
            "**Look closely at the very last row here** — a stray "
            "`test, test, test` row sneaked in at the bottom of the file. "
            "This is exactly the kind of junk that `head()` would never "
            "show you."
        ),
        code("df.tail()"),
        md(
            "That one bad row has a hidden cost. Because `x` and `y` now "
            "contain the text `\"test\"`, pandas could not read those "
            "columns as numbers — watch what `dtypes` says about them in a "
            "moment. A single garbage row at the edge poisons the type of "
            "the whole column."
        ),
        md("## 4. Random glance with `df.sample()`\n\nIf rows are sorted, `head()` can stage-manage the evidence. `sample()` breaks the staging."),
        code("df.sample(5, random_state=42)"),
        md(
            "## 5. How much evidence? `df.shape`\n\n"
            "`shape` returns `(rows, columns)`. Know your sample size "
            "before quoting any statistic — a mean over 12 rows and a mean "
            "over 12,000 deserve very different confidence."
        ),
        code("df.shape"),
        md(
            "## 6. Name the variables with `df.columns`\n\n"
            "`columns` lists the column names, so you catch typos, "
            "trailing spaces, and mystery variables before you start "
            "referencing them in code."
        ),
        code("list(df.columns)"),
        md("## 7. Schema check with `df.info()`\n\n`info()` combines non-null counts with types — fastest first audit."),
        code("df.info()"),
        md(
            "## 8. Data types with `df.dtypes`\n\n"
            "Here is the proof. `x` and `y` should be `float64`, but they "
            "show up as `object` (text) — all because of that one "
            "`test` row."
        ),
        code("df.dtypes"),
        md(
            "## 9. Isolate numeric columns with `df.select_dtypes()`\n\n"
            "Watch the consequence: asking for the numeric columns returns "
            "**nothing useful** — `x` and `y` are missing, because pandas no "
            "longer sees them as numbers."
        ),
        code('numeric = df.select_dtypes(include="number")\nnumeric.head()'),
        md(
            "## 10. Clean the bad row, then fix the types\n\n"
            "Drop the junk row and convert `x` and `y` back to numbers. "
            "Now the columns are usable again."
        ),
        code(
            'df = df[df["dataset"] != "test"].copy()\n'
            'df["x"] = pd.to_numeric(df["x"])\n'
            'df["y"] = pd.to_numeric(df["y"])\n'
            'df.dtypes'
        ),
        md(
            "## More ways data gets messy or poisoned\n\n"
            "The `test` row was one kind of poison. Here are five more you "
            "will meet constantly in real datasets. Each uses a tiny made-up "
            "table so the problem is easy to see."
        ),
        md(
            "### 1. Impossible / out-of-range values\n\n"
            "An `age` of `999` or `-3` is not a person — it is a typo or a "
            "sentinel, and one bad value can drag the mean far off. "
            "Range-check before you summarize."
        ),
        code(
            'people = pd.DataFrame({"age": [27, 5, 999, -3, 44]})\n'
            'print("mean with bad rows:", round(people["age"].mean(), 1))\n'
            'valid = people[(people["age"] >= 0) & (people["age"] <= 120)]\n'
            'print("\\nmean after range check:", round(valid["age"].mean(), 1))'
        ),
        md(
            "### 2. Missing values in disguise\n\n"
            "Real missing values are often hidden as sentinels like `-999`, "
            "`\"N/A\"`, or `\"unknown\"`. Pandas does not count them as `NaN` "
            "until you tell it to — so `isna()` reports the data as complete."
        ),
        code(
            'disguised = pd.DataFrame({\n'
            '    "age": [34, -999, 28, 41],\n'
            '    "city": ["Paris", "N/A", "Lima", "unknown"],\n'
            '})\n'
            'print("isna sees nothing wrong:", disguised.isna().sum().sum())\n'
            'real = disguised.replace([-999, "N/A", "unknown"], pd.NA)\n'
            'print("\\nafter replacing sentinels:", real.isna().sum().sum())'
        ),
        md(
            "### 3. Numbers stored as text\n\n"
            "A column of prices like `\"$1,200\"` is text, not numbers. "
            "Summing it *glues the strings together* instead of adding."
        ),
        code(
            'prices = pd.DataFrame({"price": ["$1,200", "$950", "$3,400"]})\n'
            'print("Broken (string) sum:", prices["price"].sum())\n'
            'clean = prices["price"].str.replace(r"[$,]", "", regex=True).astype(float)\n'
            'print("\\nReal total:", clean.sum())'
        ),
        md(
            "### 4. Inconsistent categories\n\n"
            "Casing and stray spaces split one real category into several. "
            "`\"USA\"`, `\"usa\"`, and `\" USA \"` look identical to us but are "
            "different groups to pandas."
        ),
        code(
            'survey = pd.DataFrame({"country": ["USA", "usa", " USA ", "Canada", "canada"]})\n'
            'print("raw:    ", survey["country"].value_counts().to_dict())\n'
            'normalized = survey["country"].str.strip().str.upper()\n'
            'print("\\ncleaned:", normalized.value_counts().to_dict())'
        ),
        md(
            "### 5. Duplicate rows\n\n"
            "A row copied twice silently double-counts. Always check "
            "`duplicated()` before trusting a total."
        ),
        code(
            'orders = pd.DataFrame({"order_id": [1, 2, 2, 3], "amount": [10, 25, 25, 8]})\n'
            'display(orders)  # rows 1 and 2 are identical -- the duplicate\n'
            'print("with duplicates -> rows:", len(orders), "total:", orders["amount"].sum())\n'
            'deduped = orders.drop_duplicates()\n'
            'print("\\nafter dedupe    -> rows:", len(deduped), "total:", deduped["amount"].sum())'
        ),
        md(
            "### A few more to watch for\n\n"
            "- **Mixed or ambiguous date formats** (`01/02/03`) — parse with "
            "`pd.to_datetime` and check the result.\n"
            "- **ID columns losing leading zeros** when read as numbers "
            "(`007` becomes `7`).\n"
            "- **Text-encoding gremlins** (`café` showing up as `cafÃ©`).\n"
            "- **Silently mixed units** (kg vs lb, USD vs EUR) in one column.\n"
            "- **Trailing spaces in column names** (`\"age \"` vs `\"age\"`)."
        ),
        md(
            "## Why this matters to a data scientist\n\n"
            "Every model is a compression of its training data. The `test` "
            "row did not crash anything — it silently turned two numeric "
            "columns into text, and anything downstream would have either "
            "crashed later or quietly dropped those columns from the "
            "analysis.\n\n"
            "In AI this failure mode also exists *on purpose*: **data "
            "poisoning**, where an attacker plants crafted rows in scraped "
            "training data so a model learns something subtly hostile. The "
            "defense is the same habit either way: inspect the data before "
            "you compute on it — because the model never will."
        ),
        md(
            "## Takeaway\n\n"
            "Functions introduced: `pd.read_csv`, `head`, `tail`, `sample`, "
            "`shape`, `columns`, `info`, `dtypes`, `select_dtypes`, "
            "`pd.to_numeric`.\n\n"
            "From the poison gallery: `isna`, `replace`, `.str.strip`, "
            "`.str.upper`, `.str.replace`, `astype`, `value_counts`, "
            "`drop_duplicates`, `mean`, `sum`.\n\n"
            "**Concept learned: inspect and clean the data before you "
            "analyze it.**"
        ),
    ]
)

# ---------------------------------------------------------------------------
# Notebook 1: Datasaurus (the real Datasaurus Dozen)
# ---------------------------------------------------------------------------
datasaurus_cells = (
    setup_cells(
        "Datasaurus: Same Stats, Different Shapes",
        "Why summary statistics are not enough",
        hook_image="../images/datasaurus_summary.png",
    )
    + [
        md(
            "## The story\n\n"
            "The famous **Datasaurus Dozen** is 13 datasets engineered to "
            "share nearly the same mean, standard deviation, and correlation "
            "— yet each draws a completely different picture. If you trust the "
            "summary table alone, you never see the dinosaur. **Always plot.**"
        ),
        md(
            "## 1. Load the Datasaurus Dozen\n\n"
            "The data ships as an Excel workbook. `pd.read_excel()` loads "
            "the raw points the same way `read_csv` would — one row per "
            "(x, y) pair, tagged with which of the 13 datasets it belongs "
            "to — you just point it at the `.xlsx` file instead."
        ),
        code('dino = pd.read_excel("../data/datasaurus_dozen.xlsx")\ndino.head()'),
        md(
            "## 2. The summary statistics look identical\n\n"
            "`groupby(\"dataset\")` splits the table into the 13 sets, and "
            "`.agg([\"mean\", \"std\"])` computes both statistics for each "
            "in one pass — the entire 'summary table' in one line."
        ),
        code('dino.groupby("dataset")[["x", "y"]].agg(["mean", "std"]).round(2)'),
        md("Same mean, same standard deviation across all 13 sets."),
        md(
            "## 3. The correlation is identical too\n\n"
            "`corr()` measures the linear relationship between `x` and `y` "
            "— the single number people trust most to describe a "
            "relationship."
        ),
        code('dino.groupby("dataset")[["x", "y"]].corr().round(2)'),
        md(
            "## 4. Now plot them\n\n"
            "Thirteen scatter plots in one grid: same numbers, very "
            "different pictures."
        ),
        code(
            'fig, axes = plt.subplots(4, 4, figsize=(14, 14))\n'
            '\n'
            'for ax, (name, part) in zip(axes.flat, dino.groupby("dataset")):\n'
            '    part.plot(kind="scatter", x="x", y="y", title=name, ax=ax, s=8)\n'
            '\n'
            '# Hide the unused axes (13 datasets, 16 slots).\n'
            'for ax in axes.flat[dino["dataset"].nunique():]:\n'
            '    ax.set_visible(False)\n'
            '\n'
            'fig.tight_layout()\n'
            'plt.show()'
        ),
        md(
            "Identical means, standard deviations, and correlation — yet a "
            "dinosaur, a star, circles, and lines. **This is why you always "
            "plot the data.**"
        ),
        md(
            "## Anscombe's quartet: the original\n\n"
            "Long before the Datasaurus, Frank Anscombe (1973) built four "
            "small datasets that share the same mean, variance, and "
            "correlation — **and the exact same best-fit line** — yet tell "
            "four different stories. It is the classic reason to plot before "
            "you model."
        ),
        code(
            'import numpy as np\n'
            '\n'
            'anscombe = pd.DataFrame({\n'
            '    "dataset": ["I"] * 11 + ["II"] * 11 + ["III"] * 11 + ["IV"] * 11,\n'
            '    "x": [10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5] * 3\n'
            '         + [8, 8, 8, 8, 8, 8, 8, 19, 8, 8, 8],\n'
            '    "y": [8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68,\n'
            '          9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74,\n'
            '          7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73,\n'
            '          6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89],\n'
            '})\n'
            'anscombe.head()'
        ),
        md("Every dataset has the same summary statistics:"),
        code(
            'anscombe.groupby("dataset").agg(\n'
            '    mean_x=("x", "mean"),\n'
            '    mean_y=("y", "mean"),\n'
            '    var_x=("x", "var"),\n'
            '    var_y=("y", "var"),\n'
            ').round(2)'
        ),
        code('anscombe.groupby("dataset")[["x", "y"]].corr().round(3)'),
        md("Now plot each one with its best-fit line. The line is identical — but only honest for Dataset I:"),
        code(
            'labels = {\n'
            '    "I": "Dataset I \\u2014 linear fit is right",\n'
            '    "II": "Dataset II \\u2014 needs a quadratic",\n'
            '    "III": "Dataset III \\u2014 one outlier warps it",\n'
            '    "IV": "Dataset IV \\u2014 one point sets the slope",\n'
            '}\n'
            'colors = {"I": "#4a78df", "II": "#3caea3", "III": "#e69a3c", "IV": "#6a4ca5"}\n'
            '\n'
            'fig, axes = plt.subplots(2, 2, figsize=(12, 10))\n'
            'for ax, (name, part) in zip(axes.flat, anscombe.groupby("dataset")):\n'
            '    ax.scatter(part["x"], part["y"], color=colors[name], s=40)\n'
            '    slope, intercept = np.polyfit(part["x"], part["y"], 1)\n'
            '    xs = np.array([part["x"].min(), part["x"].max()])\n'
            '    ax.plot(xs, slope * xs + intercept, "--", color="0.5")\n'
            '    ax.set_title(labels[name])\n'
            '    ax.set_xlabel("x")\n'
            '    ax.set_ylabel("y")\n'
            '\n'
            'fig.tight_layout()\n'
            'plt.show()'
        ),
        md(
            "Same fitted line `y = 3.00 + 0.50x` in every panel — but it only "
            "tells the truth for Dataset I. Dataset II is really a curve, "
            "Dataset III is thrown off by a single outlier, and in Dataset IV "
            "one lone point sets the entire slope."
        ),
        md(
            "## Why plotting beats a summary table\n\n"
            "> A statistical test requires you to already suspect the specific "
            "thing you're testing for — you run the normality test because you "
            "hypothesized non-normality. Visualization is hypothesis-"
            "generating: you look at a histogram and discover bimodality you "
            "never would have thought to test for.\n\n"
            "Anscombe's quartet and the Datasaurus Dozen make the same point: "
            "a summary table can only confirm what you already suspected, but "
            "a plot can surprise you. **Always plot the data.**"
        ),
        md(
            "## Where to go next\n\n"
            "For a huge catalog of plot types (and copy-paste code for each), "
            "browse the matplotlib gallery: "
            "<https://matplotlib.org/stable/gallery/index>"
        ),
        md(
            "## Takeaway\n\n"
            "Functions featured: `groupby`, `.agg`, `corr`, `plot`.\n\n"
            "**Concept learned: identical summary statistics — even an "
            "identical best-fit line — can hide very different shapes. Always "
            "plot.**"
        ),
    ]
)

# ---------------------------------------------------------------------------
# Notebook 2: Simpson's Paradox
# ---------------------------------------------------------------------------
simpsons_cells = (
    setup_cells(
        "Simpson's Paradox: The Group Flips the Story",
        "Overall metrics can reverse inside groups",
        hook_image="../images/Simpsons_Paradox.png",
    )
    + [
        md(
            "## The story\n\n"
            "Overall, the treatment appears worse. Inside both risk groups, "
            "the treatment performs better. **The group variable flips the "
            "story.**"
        ),
        md(
            "## 1. Load the trial data\n\n"
            "The file is an Excel workbook. `pd.read_excel()` opens it the "
            "same way `pd.read_csv()` opens a CSV — you point it at a path "
            "and get back a DataFrame. (Behind the scenes pandas uses the "
            "`openpyxl` engine for `.xlsx` files.)"
        ),
        code('trial = pd.read_excel("../data/simpsons_paradox_treatment.xlsx")\ntrial.head()'),
        code("trial.info()"),
        md("## 2. Inspect the key columns\n\nIdentify the comparison, the outcome, and the possible confounder."),
        code('trial[["risk_group", "treatment_arm", "success"]].head()'),
        md("## 3. Start with counts: `value_counts()`\n\nCounts show whether the groups are balanced."),
        code('trial["treatment_arm"].value_counts()'),
        code('trial["risk_group"].value_counts()'),
        md("## 4. Two-way counts with `pd.crosstab()`\n\nComposition matters *before* outcome comparison."),
        code('pd.crosstab(trial["risk_group"], trial["treatment_arm"])'),
        md(
            "## 5. The rushed analyst's answer: overall success rate\n\n"
            "This is where the rushed analyst starts — and stops too early."
        ),
        code('trial.groupby("treatment_arm")["success"].mean()'),
        md("## 6. Now stratify by the hidden variable\n\nGroup by risk group **and** treatment arm."),
        code('trial.groupby(["risk_group", "treatment_arm"])["success"].mean()'),
        md(
            "## 7. Use `.agg()` for counts and rates together\n\n"
            "A rate without a count is fragile. Show both."
        ),
        code(
            'trial.groupby(["risk_group", "treatment_arm"]).agg(\n'
            '    patients=("patient_id", "count"),\n'
            '    success_rate=("success", "mean"),\n'
            ')'
        ),
        md(
            "## 8. Make the grouped table readable with `unstack()`\n\n"
            "`unstack()` pivots the inner index level into columns, "
            "turning the long grouped result into a compact grid — the "
            "same numbers, but the comparison now sits side by side."
        ),
        code('trial.groupby(["risk_group", "treatment_arm"])["success"].mean().unstack()'),
        md("## 9. Normalize the crosstab\n\nWhat fraction of each treatment arm came from each risk group?"),
        code('pd.crosstab(trial["risk_group"], trial["treatment_arm"], normalize="columns")'),
        md("## Mini-lab: find the flip"),
        code(
            'overall = trial.groupby("treatment_arm")["success"].mean()\n'
            'stratified = trial.groupby(["risk_group", "treatment_arm"])["success"].mean()\n'
            'composition = pd.crosstab(trial["risk_group"], trial["treatment_arm"])\n'
            '\n'
            'print("Overall success rate:")\n'
            'print(overall)\n'
            'print("\\nStratified success rate:")\n'
            'print(stratified)\n'
            'print("\\nGroup composition:")\n'
            'print(composition)'
        ),
        md(
            "## Why this matters to a data scientist\n\n"
            "Overall metrics are how everything gets reported — "
            "dashboards, A/B tests, model accuracy. Simpson's paradox "
            "means an overall number can point in the *opposite* "
            "direction of every group it summarizes.\n\n"
            "The same trap appears when an A/B test is pooled across "
            "countries, or when a model's accuracy is quoted without "
            "checking subgroups: a model can look fine overall while "
            "being the worst option for every group that matters "
            "(checking exactly this is the core move of a fairness "
            "audit). Before trusting any headline metric, name the groups "
            "that matter and re-compute the metric inside each one."
        ),
        md(
            "## Takeaway\n\n"
            "Functions introduced: `pd.read_excel`, `groupby`, `.agg`, `pd.crosstab`, `value_counts`, `unstack`.\n\n"
            "**Concept learned: important groups can reverse the headline conclusion.**"
        ),
    ]
)

# ---------------------------------------------------------------------------
# Notebook 3: Survivorship Bias
# ---------------------------------------------------------------------------
survivorship_cells = (
    setup_cells(
        "Survivorship Bias: Missing Failures Are Still Evidence",
        "Missing rows and missing values are clues, not noise",
        hook_image="../images/survivorship_bias.png",
    )
    + [
        md(
            "## The story\n\n"
            "Revenue exists for surviving startups. Failed startups often "
            "have missing revenue, or vanish from the dataset entirely. If "
            "you only analyze survivors, you are studying winners and "
            "calling it the population."
        ),
        md(
            "## 1. Load the startup dataset\n\n"
            "This file is JSON — common when data comes from a web API. We "
            "wrote it in *records* orientation (a list of row-dicts), so we "
            "pass `orient='records'` to `pd.read_json()` to read it back."
        ),
        code('startups = pd.read_json("../data/startup_survivorship.json", orient="records")\nstartups.head()'),
        code("startups.info()"),
        md("## 2. Missingness map with `df.isna()`\n\n`isna()` creates a True/False map of missingness."),
        code("startups.isna().head()"),
        md("## 3. Missing counts with `df.isna().sum()`\n\nCount absence by column."),
        code("startups.isna().sum().sort_values(ascending=False)"),
        md("## 4. Outcome counts\n\nSurvivorship analysis starts with the outcome distribution."),
        code('startups["survived_3yr"].value_counts()'),
        md("## 5. Cross missingness with the outcome\n\nIs revenue missing because the startup failed?"),
        code('pd.crosstab(startups["survived_3yr"], startups["year3_revenue_millions"].isna(),\n            rownames=["survived_3yr"], colnames=["revenue_missing"])'),
        md(
            "## 6. Fill carefully with `df.fillna()`\n\n"
            "Filling can be right or wrong depending on meaning. Filling "
            "missing revenue with 0 implies the startup earned nothing — "
            "but maybe revenue was simply unrecorded."
        ),
        code('startups["year3_revenue_millions"].fillna(0).describe()'),
        md(
            "## 7. Drop carefully with `df.dropna()`\n\n"
            "Dropping missing revenue creates a **survivor-only** table."
        ),
        code('survivors_only = startups.dropna(subset=["year3_revenue_millions"])'),
        md("## 8. Compare before and after\n\nAlways compare shapes and group counts after row removal."),
        code(
            'print("Full dataset shape:   ", startups.shape)\n'
            'print("Survivors-only shape: ", survivors_only.shape)\n'
            '\n'
            'print("\\nSector counts (full):")\n'
            'print(startups["sector"].value_counts())\n'
            '\n'
            'print("\\nSector counts (survivors only):")\n'
            'print(survivors_only["sector"].value_counts())'
        ),
        md(
            "## 9. Survived vs. failed per sector with `unstack()`\n\n"
            "`groupby([\"sector\", \"survived_3yr\"]).size()` counts rows for "
            "every (sector, outcome) pair, but returns a hard-to-read "
            "stacked Series; `unstack()` pivots the inner level into columns "
            "so you get a readable sector × outcome table. The `False` "
            "column is exactly the failures that `dropna` threw away."
        ),
        code('startups.groupby(["sector", "survived_3yr"]).size().unstack()'),
        md(
            "## 10. The biased headline vs. the honest one\n\n"
            "What does the headline 'average startup revenue' look like "
            "from each table?"
        ),
        code(
            'biased = survivors_only["year3_revenue_millions"].mean()\n'
            'honest_zero_fill = startups["year3_revenue_millions"].fillna(0).mean()\n'
            'print(f"Survivor-only average revenue: {biased:.2f}M")\n'
            'print(f"All startups (failed = 0):     {honest_zero_fill:.2f}M")'
        ),
        md(
            "## 11. Joining tables with `pd.merge()`\n\n"
            "Joins can *create* survivorship bias. A press directory only "
            "writes about companies that are still alive — merge against it "
            "with the default `how='inner'` and every failed startup "
            "silently disappears. `how='left'` keeps the full population.\n\n"
            "![Inner vs. left merge](../images/merge_inner_left.png)"
        ),
        code(
            'press = survivors_only[["startup_id"]].copy()\n'
            'press["press_article"] = "feature story"\n'
            '\n'
            'inner = startups.merge(press, on="startup_id")\n'
            'left = startups.merge(press, on="startup_id", how="left")\n'
            'print("all startups:      ", startups.shape)\n'
            'print("inner merge result:", inner.shape, " <- failures silently gone")\n'
            'print("left merge result: ", left.shape)'
        ),
        md("## 12. Find duplicates with `df.duplicated()`\n\n`duplicated()` flags every row that is an exact copy of an earlier one — duplicates silently double-count whatever you sum or average."),
        code("startups.duplicated().sum()"),
        md("## 13. Remove duplicates with `df.drop_duplicates()`\n\nRemove duplicates only after checking what they represent."),
        code(
            'clean = startups.drop_duplicates()\n'
            'print(startups.shape, clean.shape)'
        ),
        md(
            "## The danger of filling: imputation changes the statistics\n\n"
            "Back to section 6 for a harder look. Filling is never free: "
            "every strategy *fabricates* 1,769 revenue values — far more "
            "fabricated data than the 634 real values — and each strategy "
            "distorts the statistics in a different way."
        ),
        code(
            'real_rev = survivors_only["year3_revenue_millions"]\n'
            'zero_fill = startups["year3_revenue_millions"].fillna(0)\n'
            'mean_fill = startups["year3_revenue_millions"].fillna(\n'
            '    startups["year3_revenue_millions"].mean()\n'
            ')\n'
            '\n'
            'print("corr(seed_funding, revenue)")\n'
            'print("  real (survivors only):", round(survivors_only["seed_funding_millions"].corr(real_rev), 3))\n'
            'print("  after mean-fill:      ", round(startups["seed_funding_millions"].corr(mean_fill), 3))\n'
            '\n'
            'print("\\ncorr(market_score, revenue)")\n'
            'print("  real (survivors only):", round(survivors_only["market_score"].corr(real_rev), 3))\n'
            'print("  after zero-fill:      ", round(startups["market_score"].corr(zero_fill), 3))\n'
            '\n'
            'print("\\nspread of revenue (std)")\n'
            'print("  real (survivors only):", round(real_rev.std(), 2))\n'
            'print("  after mean-fill:      ", round(mean_fill.std(), 2))'
        ),
        md(
            "Each fill strategy commits a different crime:\n\n"
            "- **Mean-fill destroys real relationships.** The seed-funding "
            "correlation is roughly cut in half, and the spread of revenue "
            "drops from about 17 to about 9 — injecting 1,769 identical "
            "values flattens every pattern in the column.\n"
            "- **Zero-fill invents relationships that do not exist.** Among "
            "survivors, `market_score` has *no* relationship with revenue. "
            "But market score does predict *survival* — so writing 0 into "
            "every failed startup copies the survival pattern into the "
            "revenue column, and a correlation appears from nowhere. A "
            "model would happily learn it.\n\n"
            "Every statistic you compute after filling is partly a "
            "statistic of your fill strategy. Imputation is a **modeling "
            "decision**, not cleanup — document it, justify it, and check "
            "what it does to the numbers you care about."
        ),
        md("## Mini-lab: missing failures"),
        code(
            'print(startups.isna().sum())\n'
            'print(startups["survived_3yr"].value_counts())\n'
            'survivors_only = startups.dropna(subset=["year3_revenue_millions"])\n'
            'print(startups.shape, survivors_only.shape)'
        ),
        md(
            "## Don't change data silently\n\n"
            "Prefer creating a new object over overwriting the original "
            "during EDA — your future self will thank you. That is why we "
            "wrote `survivors_only = startups.dropna(...)` above instead of "
            "overwriting `startups`."
        ),
        md(
            "## Why this matters to a data scientist\n\n"
            "Everything downstream inherits this bias. Train a revenue "
            "model on `survivors_only` and it does not learn *what makes "
            "startups succeed* — it learns *what successful startups look "
            "like*, which is a different question. Deployed on next "
            "year's cohort (which contains its future failures), its "
            "predictions will be systematically too optimistic, because "
            "the model has literally never seen a failure.\n\n"
            "The deeper problem: the missingness here is **informative**. "
            "Revenue is missing *because* the startup failed — "
            "statisticians call this *missing not at random* (MNAR): the "
            "mechanism that hides a value is tied to the value itself. No "
            "fill strategy can recover information that was never "
            "recorded."
        ),
        md(
            "## The solution: model what you actually observe\n\n"
            "We cannot conjure the missing revenue, but we are not stuck "
            "— restructure the problem around what *is* observed for "
            "everyone:\n\n"
            "1. **Model survival first.** `survived_3yr` is present for "
            "every row, so surviving-vs-failing is an honest question for "
            "the full population.\n"
            "2. **Model revenue *given* survival** on the survivors — and "
            "label that estimate as conditional.\n"
            "3. **Multiply the two** for an honest expected value (a "
            "*two-stage* or *hurdle* model).\n\n"
            "And the strongest fix is upstream: **design the missingness "
            "out** — track cohorts from founding day so failures stay in "
            "the dataset, instead of scraping success stories after the "
            "fact."
        ),
        code(
            'p_survive = startups["survived_3yr"].mean()\n'
            'revenue_if_survive = survivors_only["year3_revenue_millions"].mean()\n'
            '\n'
            'print(f"Stage 1 - P(survive 3 years):    {p_survive:.1%}  (uses all {len(startups)} rows)")\n'
            'print(f"Stage 2 - E[revenue | survived]: {revenue_if_survive:.2f}M  (uses {len(survivors_only)} survivors)")\n'
            'print(f"\\nHonest expected revenue:  {p_survive * revenue_if_survive:.2f}M per startup founded")\n'
            'print(f"Survivor-only headline:   {revenue_if_survive:.2f}M  <- almost 4x too optimistic")'
        ),
        md(
            "This also explains why the zero-fill average in section 10 "
            "was defensible *here*: in this dataset, missing revenue "
            "really does mean \"failed, earned nothing\", so the zero-fill "
            "mean and the two-stage estimate agree. When missing instead "
            "means \"unrecorded\", zero-fill is simply wrong — but the "
            "two-stage decomposition still works, because it never "
            "pretends to know values it does not have."
        ),
        md(
            "## Takeaway\n\n"
            "Functions introduced: `pd.read_json`, `isna`, "
            "`value_counts`, `pd.crosstab`, `unstack`, `fillna`, `dropna`, "
            "`pd.merge`, `duplicated`, `drop_duplicates`.\n\n"
            "**Concept learned: missing rows and missing values are "
            "evidence. A model trained only on survivors learns the wrong "
            "population — model what is observed for everyone (survival) "
            "first, then model the rest conditionally.**"
        ),
    ]
)

# ---------------------------------------------------------------------------
# Notebook 4: Gaming Whales / Outliers
# ---------------------------------------------------------------------------
whales_cells = (
    setup_cells(
        "Gaming Whales and Dolphins: Outliers Run the Economy",
        "Outliers can be errors, edge cases, or the whole story",
        hook_image="../images/whales.png",
    )
    + [
        md(
            "## The story\n\n"
            "Most players spend little. A tiny group of 'whales' spends a "
            "lot. The 'average player' may not exist. Removing outliers "
            "here would delete the business model."
        ),
        md(
            "## 1. Load the gaming dataset\n\n"
            "Rows are players; columns include spend, sessions, and segment. "
            "The file is in **Parquet** — a columnar binary format common in "
            "modern data lakes. `pd.read_parquet()` reads it just like CSV, "
            "but loads much faster and preserves dtypes exactly. (Requires "
            "the `pyarrow` package.)"
        ),
        code('game = pd.read_parquet("../data/gaming_outliers.parquet")\ngame.head()'),
        code("game.info()"),
        md(
            "## 2. Distribution snapshot with `df.describe()`\n\n"
            "Look at quartiles, mean, max, and spread. Compare the mean to "
            "the median — a big gap is your first whale alarm."
        ),
        code('game["monthly_spend"].describe()'),
        md("## 3. Segment counts with `value_counts()`\n\nWhales are rare by count."),
        code('game["segment"].value_counts()'),
        md(
            "## 4. Unique values with `df.nunique()`\n\n"
            "`nunique()` helps you tell IDs apart from categories and "
            "continuous variables."
        ),
        code("game.nunique()"),
        md("## 5. Sort the heavy tail\n\nLook directly at the top spenders."),
        code('game.sort_values("monthly_spend", ascending=False).head(20)'),
        md("## 6. Visualize the distribution\n\nA histogram is the most direct way to *see* a heavy tail."),
        code(
            'game["monthly_spend"].plot(kind="hist", bins=50, title="Monthly spend (all players)")\n'
            'plt.xlabel("Monthly spend ($)")\n'
            'plt.show()'
        ),
        md("And on a log scale, so you can see what's hiding in the tail:"),
        code(
            'game["monthly_spend"].plot(kind="hist", bins=50, log=True,\n'
            '                           title="Monthly spend (log y-axis)")\n'
            'plt.xlabel("Monthly spend ($)")\n'
            'plt.show()'
        ),
        md("## 7. Group revenue by segment\n\nRevenue contribution matters more than player count."),
        code(
            'segment_summary = game.groupby("segment").agg(\n'
            '    players=("player_id", "count"),\n'
            '    avg_spend=("monthly_spend", "mean"),\n'
            '    total_spend=("monthly_spend", "sum"),\n'
            ')\n'
            'segment_summary'
        ),
        md(
            "## 8. What share of revenue comes from each segment?\n\n"
            "Dividing each segment's total by the grand total turns raw "
            "sums into shares — the number that tells you who actually "
            "funds the game."
        ),
        code(
            'segment_summary["revenue_share"] = (\n'
            '    segment_summary["total_spend"] / segment_summary["total_spend"].sum()\n'
            ')\n'
            'segment_summary[["players", "total_spend", "revenue_share"]].round(3)'
        ),
        md(
            "## 9. Should we remove the whales?\n\n"
            "Not automatically. Decide whether outliers are:\n\n"
            "- **errors** (drop them),\n"
            "- **rare valid users** (keep, but report separately), or\n"
            "- **the business itself** (keep, and never quote a plain mean)."
        ),
        md("## Mini-lab: whale economics"),
        code(
            'print(game["monthly_spend"].describe())\n'
            'print(game["segment"].value_counts())\n'
            'print(game.groupby("segment")["monthly_spend"].sum())'
        ),
        md(
            "## Discussion\n\n"
            "- A teammate reports 'the average player spends $X/month'. "
            "Why is this misleading?\n"
            "- What number would be more honest to report instead?\n"
        ),
        md(
            "## Why this matters to a data scientist\n\n"
            "Heavy tails are the rule in tech data, not the exception: "
            "revenue per customer, session length, tokens per request, "
            "file sizes, follower counts. Two practical consequences:\n\n"
            "- **Report distributions, not means.** 'The average player "
            "spends $12.74' is technically true and practically false — "
            "the *median* player spends about $3 (the 50% row in "
            "`describe()` above). Quote the median, the quartiles, or the "
            "revenue-share table you built.\n"
            "- **Never remove outliers on autopilot.** A preprocessing "
            "step that clips 'anomalies' would delete the whales here — "
            "and with them, most of the revenue. In an ML pipeline, "
            "automatic outlier removal can silently amputate the exact "
            "behavior the business runs on."
        ),
        md(
            "## Takeaway\n\n"
            "Functions introduced: `pd.read_parquet`, `describe`, `nunique`.\n\n"
            "Functions reinforced: `value_counts`, `sort_values`, "
            "`groupby().agg`, `plot`.\n\n"
            "**Concept learned: outliers can be errors, edge cases, or the "
            "whole story.**"
        ),
    ]
)


# ---------------------------------------------------------------------------
# Notebook 5: Collider Bias
# ---------------------------------------------------------------------------
collider_cells = (
    setup_cells(
        "Collider Bias: Selection Changes the Evidence",
        "A dataset is not just data — it is the result of a selection process",
        hook_image="../images/collider_bias.png",
    )
    + [
        md(
            "## The story\n\n"
            "Applicants are selected using ability **and** portfolio. Inside "
            "admitted students, the relationship between those two variables "
            "can look very different — even reversed — compared to the full "
            "applicant pool. The doorway distorts the evidence."
        ),
        md(
            "## 1. Load the admissions data\n\n"
            "Open the file and ask whether it is the full pool or a selected "
            "subset. This file is in **Feather** — Apache Arrow's on-disk "
            "format, useful for fast interchange between Python and R. "
            "`pd.read_feather()` returns a DataFrame just like `read_csv`."
        ),
        code('apps = pd.read_feather("../data/collider_admissions.feather")\napps.head()'),
        code("apps.info()"),
        md("## 2. Find the selection clue\n\nA source or status column often reveals how rows entered the table."),
        code('apps["data_source"].value_counts()'),
        code('apps["admitted"].value_counts()'),
        md(
            "## 3. Filter with `df.query()`\n\n"
            "`query()` is the most readable way to express many row-selection "
            "stories."
        ),
        code(
            'admitted = apps.query("admitted == True")\n'
            'not_admitted = apps.query("admitted == False")\n'
            'admitted.shape, not_admitted.shape'
        ),
        md(
            "## 4. Compare full vs. selected\n\n"
            "Now look at the correlation between ability and portfolio in "
            "the full pool, then inside the admitted subset."
        ),
        code('apps[["ability", "portfolio_score"]].corr()'),
        code('admitted[["ability", "portfolio_score"]].corr()'),
        md(
            "In the full pool, ability and portfolio are unrelated: "
            "knowing one tells you nothing about the other (correlation "
            "≈ 0). Inside the admitted group, a strong **negative** "
            "correlation appears (≈ −0.35).\n\n"
            "Why? Admission required impressing on *something*. A student "
            "who got in with modest ability must have had a strong "
            "portfolio; a student with a weak portfolio must have had "
            "high ability — otherwise they would not be in the file. The "
            "doorway filters out everyone who was low on both, and that "
            "missing corner is what manufactures the trade-off.\n\n"
            "Here is why it matters: study only the admitted file and you "
            "would 'discover' that talented students build worse "
            "portfolios — and then hand out coaching advice, change "
            "policy, or train a model on a pattern that exists only "
            "behind the doorway, not in the world."
        ),
        md(
            "## 5. Visualize it\n\n"
            "Two scatter plots side by side — the full pool next to the "
            "admitted subset — make the manufactured pattern visible at a "
            "glance."
        ),
        code(
            'fig, axes = plt.subplots(1, 2, figsize=(12, 5))\n'
            'apps.plot(kind="scatter", x="ability", y="portfolio_score",\n'
            '          ax=axes[0], title="All applicants", alpha=0.4)\n'
            'admitted.plot(kind="scatter", x="ability", y="portfolio_score",\n'
            '              ax=axes[1], title="Admitted only", alpha=0.4, color="C1")\n'
            'plt.tight_layout()\n'
            'plt.show()'
        ),
        md(
            "## 6. Compound conditions\n\n"
            "Real selection rules often combine multiple conditions."
        ),
        code('apps.query("admitted == True and ability > 0").shape'),
        code('apps.query("portfolio_score > 1 or ability > 1").shape'),
        md(
            "## 7. Column selection with `df.loc[]`\n\n"
            "`loc` selects by labels: rows by condition, columns by name."
        ),
        code('apps.loc[:, ["ability", "portfolio_score", "admitted"]].head()'),
        md(
            "## 8. Rows and columns together with `loc`\n\n"
            "`loc` accepts a row condition and a column list in one call "
            "— filter and select in a single step, no chaining needed."
        ),
        code('apps.loc[apps["admitted"] == True, ["ability", "portfolio_score"]].head()'),
        md(
            "## 9. Position selection with `df.iloc[]`\n\n"
            "`iloc` is for quick position-based checks."
        ),
        code("apps.iloc[:5, :4]"),
        md(
            "## Mini-lab: recreate the bias\n\n"
            "Compute correlations before and after selection."
        ),
        code(
            'full_corr = apps[["ability", "portfolio_score"]].corr()\n'
            'selected_corr = apps.query("admitted == True")[["ability", "portfolio_score"]].corr()\n'
            'print("Full pool correlation:")\n'
            'print(full_corr)\n'
            'print("\\nAdmitted-only correlation:")\n'
            'print(selected_corr)'
        ),
        md(
            "## Why this matters to a data scientist\n\n"
            "Almost every real dataset went through a doorway before it "
            "reached you: hospital records contain the people sick enough "
            "to come in, support tickets contain the customers annoyed "
            "enough to write, loan-default data contains only the "
            "applicants who were approved. The selection is invisible in "
            "the table — the rows that did not make it leave no trace.\n\n"
            "For AI this is a training-data problem. A default model "
            "trained on approved loans has never seen the applicants the "
            "old policy rejected, so it inherits the old policy's blind "
            "spots — and it can learn manufactured trade-offs exactly "
            "like the one above. Before modeling, always ask: *who had "
            "to pass through what doorway for this row to exist?*"
        ),
        md(
            "## Takeaway\n\n"
            "Functions introduced: `pd.read_feather`, `query`, `corr`, `loc`, `iloc`.\n\n"
            "**Concept learned: selection can invent or hide relationships.**"
        ),
    ]
)

# ---------------------------------------------------------------------------
# Notebook 6: Regression to the Mean
# ---------------------------------------------------------------------------
rtm_cells = (
    setup_cells(
        "Regression to the Mean: Extremes Drift Back",
        "Before/after stories are tempting — extreme baselines make them dangerous",
        hook_image="../images/regression_to_mean.png",
    )
    + [
        md(
            "## The story\n\n"
            "Students with very low baseline scores tend to improve on a "
            "follow-up test, even with no intervention. Students with very "
            "high baseline scores tend to drop. This is **regression to the "
            "mean** — extremes drift back toward average just because of "
            "measurement noise."
        ),
        md(
            "## 1. Load the score dataset\n\n"
            "Rows are students with baseline, follow-up, and change. The "
            "file is a **pickle** — Python's native serialization format, "
            "saved with `df.to_pickle(...)`. `pd.read_pickle()` is the "
            "fastest round-trip for Python-only workflows.\n\n"
            "*Security note:* never unpickle files from untrusted sources — "
            "pickles can execute arbitrary code on load."
        ),
        code('scores = pd.read_pickle("../data/regression_to_mean_scores.pkl")\nscores.head()'),
        code("scores.info()"),
        md("## 2. Find extremes with `df.sort_values()`\n\nSorting reveals the selected extremes."),
        code('lowest = scores.sort_values("baseline_score").head(20)\nlowest'),
        code('highest = scores.sort_values("baseline_score", ascending=False).head(20)\nhighest'),
        md(
            "## 3. Compare change in the extreme groups\n\n"
            "If regression to the mean is at play, the lowest baselines "
            "should *rise* on follow-up and the highest baselines should "
            "*fall* — even without any intervention."
        ),
        code(
            'low = scores.sort_values("baseline_score").head(100)\n'
            'high = scores.sort_values("baseline_score").tail(100)\n'
            'print(f"Avg change for 100 lowest baselines:  {low[\'change\'].mean():+.2f}")\n'
            'print(f"Avg change for 100 highest baselines: {high[\'change\'].mean():+.2f}")'
        ),
        md(
            "## 4. Build a both-tails group\n\n"
            "Concatenate the two extreme tails to compare against the middle."
        ),
        code(
            'extremes = pd.concat([\n'
            '    scores.sort_values("baseline_score").head(60),\n'
            '    scores.sort_values("baseline_score").tail(60),\n'
            '])\n'
            'extremes.shape'
        ),
        md(
            "## 5. Visualize the drift\n\n"
            "One scatter of change against baseline shows the whole "
            "phenomenon — every student is a dot, and the red dashed line "
            "marks 'no change'."
        ),
        code(
            'ax = scores.plot(kind="scatter", x="baseline_score", y="change",\n'
            '                 alpha=0.3, title="Change vs. baseline score")\n'
            'ax.axhline(0, color="red", linestyle="--")\n'
            'plt.show()'
        ),
        md("Low baselines mostly rise; high baselines mostly fall. The line of zero change cuts diagonally through the cloud."),
        md("## 6. Relationships with `df.corr()`\n\nCorrelation helps describe the link between baseline, follow-up, and change."),
        code('scores[["baseline_score", "followup_score", "change"]].corr()'),
        md(
            "## 7. Change scores need suspicion\n\n"
            "`change` is strongly negatively correlated with `baseline` "
            "almost automatically: baseline includes random noise that "
            "subtracts out in the change."
        ),
        code('scores[["baseline_score", "change"]].corr()'),
        md("## Mini-lab: extremes drift"),
        code(
            'low = scores.sort_values("baseline_score").head(100)\n'
            'high = scores.sort_values("baseline_score").tail(100)\n'
            'print("Low baseline avg change:", round(low["change"].mean(), 2))\n'
            'print("High baseline avg change:", round(high["change"].mean(), 2))'
        ),
        md(
            "## Discussion\n\n"
            "- If the lowest-scoring students improved after coaching, what "
            "else must be true before claiming the intervention worked?\n"
            "- What would a fair comparison group look like?\n\n"
            "**Real-world examples:** bad sales months rebound, "
            "career-best athletes decline, angry customers calm down, "
            "extreme stores normalize."
        ),
        md(
            "## Why this matters to a data scientist\n\n"
            "Any process that *selects on an extreme and then "
            "re-measures* will show this drift: the worst-performing "
            "stores 'improve' after a management visit, the "
            "lowest-engagement users 'respond' to the win-back email, "
            "last week's bad model metrics 'recover' after an emergency "
            "retrain. In every case, part — sometimes all — of the "
            "improvement is regression to the mean, not your "
            "intervention.\n\n"
            "This is exactly why A/B tests have control groups: the "
            "control arm shows how much drift-back happens with *no* "
            "intervention, so the treatment only gets credit for the "
            "difference. When there is no control group, treat every "
            "before/after story that starts from an extreme with "
            "suspicion — including your own."
        ),
        md(
            "## Takeaway\n\n"
            "Functions introduced: `pd.read_pickle`, `sort_values`, `pd.concat`, `corr`.\n\n"
            "**Concept learned: extreme selection can make ordinary drift "
            "look causal.**"
        ),
    ]
)

# ---------------------------------------------------------------------------
# Notebook 7: Misleading Variables / Leakage
# ---------------------------------------------------------------------------
misleading_cells = (
    setup_cells(
        "Misleading Variables: Some Columns Are Traps",
        "Cleanup is not housekeeping — it is deciding what evidence belongs",
        hook_image="../images/Misleading_Variables.png",
    )
    + [
        md(
            "## The story\n\n"
            "A churn dataset contains useful predictors (plan, tenure), "
            "identifiers (`customer_id`), dates, and variables that "
            "*happen after* churn (`refund_after_churn`). The latter look "
            "powerfully predictive, but they leak the answer."
        ),
        md(
            "## 1. Load the churn dataset\n\n"
            "This file is an **HTML table** — the kind of thing you might "
            "scrape from a web page. `pd.read_html()` parses every `<table>` "
            "it finds and returns a **list of DataFrames**, so we take the "
            "first one with `[0]`."
        ),
        code('churn = pd.read_html("../data/misleading_variables_churn.html")[0]\nchurn.head()'),
        code("churn.info()"),
        md(
            "## 2. Column audit with `df.columns`\n\n"
            "Ask whether each column is an **identifier**, **outcome**, "
            "**predictor**, **date**, **proxy**, or **leak**."
        ),
        code("list(churn.columns)"),
        md("## 3. Type audit with `df.dtypes`\n\nTypes reveal disguised dates, booleans, and numbers."),
        code("churn.dtypes"),
        md("## 4. Convert with `df.astype()`\n\nUse `astype()` when the intended type is clear."),
        code('churn["churned"] = churn["churned"].astype("bool")\nchurn["churned"].dtype'),
        md(
            "## 5. Convert dates with `pd.to_datetime()`\n\n"
            "`pd.to_datetime()` turns date text into real datetime values "
            "— until then, 'dates' are just strings that sort "
            "alphabetically and cannot be compared, subtracted, or "
            "bucketed by year."
        ),
        code('churn["signup_date"] = pd.to_datetime(churn["signup_date"])\nchurn["signup_date"].dtype'),
        md(
            "## 6. Find suspicious correlations\n\n"
            "A variable can look powerful because it leaks future information."
        ),
        code(
            'numeric = churn.select_dtypes(include="number")\n'
            'numeric.corr(numeric_only=True).round(3)'
        ),
        md(
            "Pay special attention to anything that correlates strongly with "
            "`churned`. Ask: *could this value have been known at decision "
            "time, or is it a consequence of churn?*"
        ),
        md(
            "## 7. Cross-check a suspect with the outcome\n\n"
            "`refund_after_churn` smells like a leak — by name alone."
        ),
        code('pd.crosstab(churn["churned"], churn["refund_after_churn"])'),
        md("If refunds only happen *after* churn, this column can perfectly predict the outcome — but only because the outcome already happened."),
        md(
            "## 8. Drop columns with `df.drop()`\n\n"
            "Dropping columns is an **analytical decision** that should be "
            "explained, not a default cleanup step."
        ),
        code(
            'safe = churn.drop(columns=["customer_id", "refund_after_churn", "last_login_days_ago"])\n'
            'list(safe.columns)'
        ),
        md(
            "Why each drop:\n\n"
            "- `customer_id` — identifier, no predictive content\n"
            "- `refund_after_churn` — happens after the outcome (**leak**)\n"
            "- `last_login_days_ago` — measured at extraction time, may also leak"
        ),
        md(
            "## 9. Drop rows vs. drop columns\n\n"
            "Same verb, very different consequence."
        ),
        code(
            'print("Drop rows with any NA:  ", churn.dropna().shape)\n'
            'print("Drop one column:        ", churn.drop(columns=["customer_id"]).shape)'
        ),
        md("## Mini-lab: leakage hunt"),
        code(
            'print(churn.columns.tolist())\n'
            'print(churn.dtypes)\n'
            'safe = churn.drop(columns=["customer_id", "refund_after_churn"])\n'
            'print("Kept columns:", list(safe.columns))'
        ),
        md(
            "## Discussion\n\n"
            "- For each remaining column, when in the customer's lifetime "
            "is its value known? Before churn, at churn, or after?\n"
            "- Which columns would you keep for an honest churn-prediction "
            "EDA, and which would you justify dropping in writing?"
        ),
        md(
            "## Why this matters to an AI engineer\n\n"
            "Leakage is the most common way a machine-learning project "
            "fails *silently*. A leaky feature makes the offline model "
            "look outstanding — `refund_after_churn` can predict churn "
            "almost perfectly — and then the model collapses in "
            "production, because at prediction time the churn has not "
            "happened yet and the feature's value does not exist.\n\n"
            "No error message will ever tell you this. The offline "
            "metrics get *better* as the leak gets worse — which is "
            "exactly backwards. The only defense is the audit you just "
            "did: for every column, ask *when* its value becomes known, "
            "and drop — in writing — everything that is not knowable at "
            "prediction time."
        ),
        md(
            "## Takeaway\n\n"
            "Functions introduced / reinforced: `pd.read_html`, `columns`, "
            "`dtypes`, `astype`, `to_datetime`, `select_dtypes`, `corr`, "
            "`pd.crosstab`, `drop`, `dropna`.\n\n"
            "**Concept learned: not every column deserves to survive EDA.**"
        ),
    ]
)


NOTEBOOKS = {
    "00_inspect_and_clean.ipynb": inspect_cells,
    "01_datasaurus_always_plot.ipynb": datasaurus_cells,
    "02_simpsons_paradox.ipynb": simpsons_cells,
    "03_survivorship_bias.ipynb": survivorship_cells,
    "04_gaming_whales_outliers.ipynb": whales_cells,
    "05_collider_bias.ipynb": collider_cells,
    "06_regression_to_mean.ipynb": rtm_cells,
    "07_misleading_variables.ipynb": misleading_cells,
}


# Extra whitespace (px) above each numbered section heading, applied to every
# notebook so the sections read as clearly separated teaching blocks. 224px was
# chosen after comparing several gap sizes in nb00/nb01.
SECTION_GAP_PX = 224

_NUMBERED_HEADING = re.compile(r"^## \d+\.")


def add_section_gap(cells: list[dict], gap_px: int) -> list[dict]:
    """Add vertical whitespace above each numbered `## N.` section heading.

    Widens the top margin of the heading cell's font wrapper so the sections
    read as clearly separated blocks. `gap_px` is the extra space in pixels;
    0 leaves cells untouched. Applied per-notebook so we can compare sizes.
    """
    if not gap_px:
        return cells
    gap_open = (
        f'<div style="font-size: 24px; line-height: 1.6; '
        f'margin-top: {gap_px}px;">\n\n'
    )
    out: list[dict] = []
    for cell in cells:
        if cell["cell_type"] == "markdown":
            src = "".join(cell["source"])
            if src.startswith(MD_WRAP_OPEN):
                inner = src[len(MD_WRAP_OPEN):].lstrip()
                first_line = inner.splitlines()[0] if inner else ""
                if _NUMBERED_HEADING.match(first_line):
                    new_src = gap_open + src[len(MD_WRAP_OPEN):]
                    cell = {**cell, "source": new_src.splitlines(keepends=True)}
        out.append(cell)
    return out


def strip_mini_labs(cells: list[dict]) -> list[dict]:
    """Drop any 'Mini-lab' markdown header and the code cell that follows it."""
    out: list[dict] = []
    i = 0
    while i < len(cells):
        cell = cells[i]
        first_line = ""
        if cell["cell_type"] == "markdown":
            src = "".join(cell["source"])
            # Look past the wrapper div opening for the real heading.
            stripped = src.replace(MD_WRAP_OPEN, "").lstrip()
            first_line = stripped.splitlines()[0] if stripped else ""
        if first_line.lower().startswith("## mini-lab"):
            # Skip this markdown cell and any immediately following code cell.
            i += 1
            if i < len(cells) and cells[i]["cell_type"] == "code":
                i += 1
            continue
        out.append(cell)
        i += 1
    return out


def hoist_takeaway(cells: list[dict]) -> list[dict]:
    """Move the Takeaway markdown cell to the top, right after the title.

    Each module ends with a markdown cell whose body begins with
    `## Takeaway` (functions introduced + concept learned). Surface that
    summary as the first thing students see, so the punchline is up front.
    """
    cells = list(cells)
    takeaway_idx = None
    for i, cell in enumerate(cells):
        if cell["cell_type"] != "markdown":
            continue
        src = "".join(cell["source"])
        # Strip the div wrapper to inspect the real markdown body.
        body = src.replace(MD_WRAP_OPEN, "").lstrip()
        first_line = body.splitlines()[0] if body else ""
        if first_line.startswith("## Takeaway"):
            takeaway_idx = i
            break

    if takeaway_idx is None:
        return cells

    takeaway = cells.pop(takeaway_idx)
    # cells[0] is the H1 title; insert takeaway at position 1.
    cells.insert(1, takeaway)
    return cells


def build_datasaurus_summary_image() -> None:
    """Render the Datasaurus "same stats, different shapes" hook infographic.

    A central box of the (near-identical) summary statistics with arrows out
    to eight of the thirteen shapes, drawn from the real datasaurus_dozen.xlsx.
    Saved to images/datasaurus_summary.png and embedded at the top of nb01.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd
    from matplotlib.patches import FancyArrowPatch

    df = pd.read_excel(DATA_DIR / "datasaurus_dozen.xlsx")
    g = df.groupby("dataset")
    stats = g[["x", "y"]].agg(["mean", "std"])
    xmean = stats[("x", "mean")].mean()
    ymean = stats[("y", "mean")].mean()
    xsd = stats[("x", "std")].mean()
    ysd = stats[("y", "std")].mean()
    corr = g.apply(lambda d: d["x"].corr(d["y"]), include_groups=False).mean()

    positions = {
        "away": (0, 0), "bullseye": (0, 1), "circle": (0, 2),
        "dino": (1, 0), "h_lines": (1, 2),
        "high_lines": (2, 0), "slant_down": (2, 1), "slant_up": (2, 2),
    }
    colors = {
        "away": "#e36c6c", "bullseye": "#e69a3c", "circle": "#c7b500",
        "dino": "#88a838", "h_lines": "#3cae8c", "high_lines": "#3caea3",
        "slant_down": "#4aa3df", "slant_up": "#4a78df",
    }

    fig, axes = plt.subplots(3, 3, figsize=(11, 9))
    for name, (r, c) in positions.items():
        ax = axes[r][c]
        part = g.get_group(name)
        ax.scatter(part["x"], part["y"], s=10, color=colors[name])
        ax.set_title(name, fontsize=15)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

    center = axes[1][1]
    center.axis("off")
    text = (
        f"X Mean : {xmean:5.2f}\n"
        f"Y Mean : {ymean:5.2f}\n"
        f"X SD   : {xsd:5.2f}\n"
        f"Y SD   : {ysd:5.2f}\n"
        f"Corr.  : {corr:5.2f}"
    )
    box = center.text(
        0.5, 0.5, text, ha="center", va="center", family="monospace",
        fontsize=17, bbox=dict(boxstyle="round,pad=0.6", facecolor="#e8e8e8", edgecolor="none"),
    )

    fig.tight_layout()
    fig.canvas.draw()  # finalize positions so the stats-box extent is known

    # Each arrow spans only the gutter: it starts at the edge of the gray stats
    # box and stops at the edge of its target panel, so it never overlaps either.
    inv = fig.transFigure.inverted()
    ext = box.get_bbox_patch().get_window_extent()
    bx0, by0 = inv.transform((ext.x0, ext.y0))
    bx1, by1 = inv.transform((ext.x1, ext.y1))
    cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2

    def ray_exit(px, py, ux, uy, x0, y0, x1, y1):
        """Distance from interior point (px,py) along unit (ux,uy) to the rect edge."""
        ts = []
        if ux > 0:
            ts.append((x1 - px) / ux)
        elif ux < 0:
            ts.append((x0 - px) / ux)
        if uy > 0:
            ts.append((y1 - py) / uy)
        elif uy < 0:
            ts.append((y0 - py) / uy)
        return min(ts)

    pad = 0.006
    renderer = fig.canvas.get_renderer()
    for name, (r, c) in positions.items():
        # Use the tight bbox (scatter + title) so arrows stop short of the
        # panel title instead of piercing it — get_position() excludes titles.
        t = axes[r][c].get_tightbbox(renderer)
        px0, py0 = inv.transform((t.x0, t.y0))
        px1, py1 = inv.transform((t.x1, t.y1))
        px, py = (px0 + px1) / 2, (py0 + py1) / 2
        ux, uy = px - cx, py - cy
        norm = (ux ** 2 + uy ** 2) ** 0.5
        ux, uy = ux / norm, uy / norm
        tb = ray_exit(cx, cy, ux, uy, bx0, by0, bx1, by1)        # leave the box
        sx, sy = cx + ux * (tb + pad), cy + uy * (tb + pad)
        tp = ray_exit(px, py, -ux, -uy, px0, py0, px1, py1)      # reach the panel
        ex, ey = px - ux * (tp + pad), py - uy * (tp + pad)
        fig.add_artist(FancyArrowPatch(
            (sx, sy), (ex, ey), transform=fig.transFigure,
            arrowstyle="-|>", mutation_scale=15, color="0.35", lw=1.4,
        ))

    IMAGES_DIR.mkdir(exist_ok=True)
    fig.savefig(IMAGES_DIR / "datasaurus_summary.png", dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {IMAGES_DIR / 'datasaurus_summary.png'}")


def build_merge_diagram_image() -> None:
    """Render the inner-vs-left merge diagram embedded in nb03 section 11.

    Cartoon tables: `startups` (survivors + failures) merged against a
    survivor-only `press` table. how='inner' silently drops the failed rows;
    how='left' keeps everyone and marks the missing stories NaN.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, Rectangle

    SURV = "#a5cf8d"   # survivors (they have press coverage)
    FAIL = "#d4d4d4"   # failed startups
    STORY = "#ffffff"
    NAN = "#f5e9c9"    # the left join's "no match" cells

    row_h, cell_w, gap = 0.55, 1.45, 0.06

    fig, ax = plt.subplots(figsize=(12, 7.2))
    ax.set_xlim(0, 12.4)
    ax.set_ylim(0, 9.0)
    ax.axis("off")

    def draw_table(x, top, title, rows, caption=None):
        ncols = len(rows[0])
        width = ncols * cell_w + (ncols - 1) * gap
        ax.text(x + width / 2, top + 0.15, title, ha="center", va="bottom",
                fontsize=13, fontweight="bold")
        for r, cells in enumerate(rows):
            y = top - (r + 1) * (row_h + gap)
            for c, (txt, color) in enumerate(cells):
                ax.add_patch(Rectangle((x + c * (cell_w + gap), y),
                                       cell_w, row_h,
                                       facecolor=color, edgecolor="0.45"))
                ax.text(x + c * (cell_w + gap) + cell_w / 2, y + row_h / 2,
                        txt, ha="center", va="center", fontsize=11)
        if caption:
            y = top - len(rows) * (row_h + gap) - 0.42
            ax.text(x + width / 2, y, caption, ha="center", va="center",
                    fontsize=11, style="italic", color="0.25")

    draw_table(0.5, 7.9, "startups — everyone",
               [[("S1", SURV)], [("S2", SURV)], [("F1", FAIL)],
                [("F2", FAIL)], [("F3", FAIL)]])
    draw_table(0.5, 3.1, "press — survivors only",
               [[("S1", SURV), ("story", STORY)],
                [("S2", SURV), ("story", STORY)]])

    draw_table(7.6, 8.2, 'how="inner"  (the default)',
               [[("S1", SURV), ("story", STORY)],
                [("S2", SURV), ("story", STORY)]],
               caption="failed startups silently vanish")
    draw_table(7.6, 4.6, 'how="left"',
               [[("S1", SURV), ("story", STORY)],
                [("S2", SURV), ("story", STORY)],
                [("F1", FAIL), ("NaN", NAN)],
                [("F2", FAIL), ("NaN", NAN)],
                [("F3", FAIL), ("NaN", NAN)]],
               caption="everyone kept — no story becomes NaN")

    for start, end in [((4.3, 5.6), (7.3, 7.5)), ((4.3, 4.4), (7.3, 3.2))]:
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>",
                                     mutation_scale=18, color="0.35", lw=1.6))
    ax.text(5.8, 7.0, "merge", ha="center", fontsize=12, color="0.3")
    ax.text(5.8, 3.4, "merge", ha="center", fontsize=12, color="0.3")

    for x, color, label in [(0.5, SURV, "survived"), (2.6, FAIL, "failed")]:
        ax.add_patch(Rectangle((x, 0.25), 0.45, 0.35, facecolor=color,
                               edgecolor="0.45"))
        ax.text(x + 0.58, 0.42, label, va="center", fontsize=11)

    IMAGES_DIR.mkdir(exist_ok=True)
    fig.savefig(IMAGES_DIR / "merge_inner_left.png", dpi=110,
                bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {IMAGES_DIR / 'merge_inner_left.png'}")


def main() -> None:
    build_datasaurus_summary_image()
    build_merge_diagram_image()
    out_dir = Path(__file__).resolve().parent
    for name, cells in NOTEBOOKS.items():
        cells = hoist_takeaway(strip_mini_labs(cells))
        cells = add_section_gap(cells, SECTION_GAP_PX)
        nb = notebook(cells)
        path = out_dir / name
        path.write_text(json.dumps(nb, indent=1) + "\n")
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
