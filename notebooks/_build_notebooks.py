"""Generate one Jupyter notebook per bias type from the workshop slide content.

Run from the repo root or from this directory:
    python notebooks/_build_notebooks.py
"""
from __future__ import annotations

import json
from pathlib import Path

# CSS injected at the top of every notebook so all text is at least 24px.
# Targets both rendered markdown and code-editor / output font sizes.
LARGE_FONT_CSS_CELL_SOURCE = '''\
from IPython.display import HTML, display

display(HTML("""
<style>
/* Rendered markdown */
.jp-RenderedHTMLCommon,
.jp-RenderedMarkdown,
.rendered_html {
    font-size: 24px !important;
    line-height: 1.5 !important;
}
.jp-RenderedHTMLCommon h1, .rendered_html h1 { font-size: 40px !important; }
.jp-RenderedHTMLCommon h2, .rendered_html h2 { font-size: 34px !important; }
.jp-RenderedHTMLCommon h3, .rendered_html h3 { font-size: 30px !important; }
.jp-RenderedHTMLCommon h4, .rendered_html h4 { font-size: 28px !important; }
.jp-RenderedHTMLCommon table, .rendered_html table {
    font-size: 22px !important;
}

/* Code editor (CodeMirror, used by classic + JupyterLab) */
.CodeMirror, .cm-editor, .jp-Editor, .jp-InputArea-editor {
    font-size: 24px !important;
}
.cm-content, .cm-line { font-size: 24px !important; }

/* Code output (print, tracebacks, DataFrame text) */
.jp-OutputArea-output,
.output_area,
.output pre,
.jp-RenderedText pre {
    font-size: 22px !important;
}

/* DataFrame tables in output */
.dataframe, .dataframe th, .dataframe td {
    font-size: 22px !important;
}
</style>
"""))
'''


def md(source: str) -> dict:
    """Markdown cell."""
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source.splitlines(keepends=True) or [""],
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


def setup_cells(title: str, subtitle: str) -> list[dict]:
    """Common opening cells: title, large-font CSS, imports."""
    return [
        md(f"# {title}\n\n## {subtitle}"),
        md(
            "Run the cell below first. It enlarges the font for both code and "
            "markdown so the notebook is easy to read while walking through it "
            "in class."
        ),
        code(LARGE_FONT_CSS_CELL_SOURCE),
        md("### Imports"),
        code("import pandas as pd\nimport matplotlib.pyplot as plt\n\nplt.rcParams['font.size'] = 16\nplt.rcParams['figure.figsize'] = (8, 5)"),
    ]


# ---------------------------------------------------------------------------
# Notebook 1: Datasaurus
# ---------------------------------------------------------------------------
datasaurus_cells = (
    setup_cells(
        "Datasaurus: First Look, Then Plot",
        "Why summary statistics are not enough",
    )
    + [
        md(
            "## The story\n\n"
            "Several different datasets can share nearly identical means, "
            "standard deviations, and correlations — yet look completely "
            "different when you plot them. **Always plot.**"
        ),
        md("## 1. Load the evidence with `pd.read_csv()`\n\nThe file is the witness. Start by opening it."),
        code('df = pd.read_csv("../data/always_plot_demo.csv")'),
        md("## 2. First glance with `df.head()`\n\nWhat does one row look like?"),
        code("df.head()"),
        md("## 3. Last glance with `df.tail()`\n\nCatch weird endings, appended notes, or format changes."),
        code("df.tail()"),
        md("## 4. Random glance with `df.sample()`\n\nIf rows are sorted, `head()` can stage-manage the evidence. `sample()` breaks the staging."),
        code("df.sample(5, random_state=42)"),
        md("## 5. How much evidence? `df.shape`"),
        code("df.shape"),
        md("## 6. Name the variables with `df.columns`"),
        code("list(df.columns)"),
        md("## 7. Schema check with `df.info()`\n\n`info()` combines non-null counts with types — fastest first audit."),
        code("df.info()"),
        md("## 8. Data types with `df.dtypes`"),
        code("df.dtypes"),
        md("## 9. Isolate numeric columns with `df.select_dtypes()`"),
        code('numeric = df.select_dtypes(include="number")\nnumeric.head()'),
        md(
            "## 10. Look at summary statistics for each shape\n\n"
            "Notice how similar the summaries are — yet the data is wildly "
            "different (we will see that next)."
        ),
        code('df.groupby("dataset")[["x", "y"]].agg(["mean", "std"]).round(2)'),
        md("## 11. Correlations per dataset"),
        code('df.groupby("dataset")[["x", "y"]].corr().round(2)'),
        md("## 12. Now plot each dataset\n\nThe story lands when you see the shapes."),
        code(
            'for name, part in df.groupby("dataset"):\n'
            '    ax = part.plot(kind="scatter", x="x", y="y", title=name)\n'
            '    plt.show()'
        ),
        md(
            "## Discussion\n\n"
            "- What would a report of means and standard deviations hide here?\n"
            "- Which dataset would you flag as suspicious if you only had the summary table?\n"
        ),
        md(
            "## Mini-lab: the plotting habit\n\n"
            "Build a fast EDA opening ritual:"
        ),
        code(
            'df = pd.read_csv("../data/always_plot_demo.csv")\n'
            'print(df.shape)\n'
            'print(df.dtypes)\n'
            'print(df.sample(5, random_state=42))\n'
            'df.query("dataset == \'line\'").plot(kind="scatter", x="x", y="y")'
        ),
        md(
            "## Takeaway\n\n"
            "Functions introduced: `pd.read_csv`, `head`, `tail`, `sample`, "
            "`shape`, `columns`, `info`, `dtypes`, `select_dtypes`, `plot`.\n\n"
            "**Concept learned: before interpretation, look at the data.**"
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
    )
    + [
        md(
            "## The story\n\n"
            "Overall, the treatment appears worse. Inside both risk groups, "
            "the treatment performs better. **The group variable flips the "
            "story.**"
        ),
        md("## 1. Load the trial data\n\nRows are patients; columns are risk group, treatment arm, and outcome."),
        code('trial = pd.read_csv("../data/simpsons_paradox_treatment.csv")\ntrial.head()'),
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
        md("## 8. Make the grouped table readable with `unstack()`"),
        code('trial.groupby(["risk_group", "treatment_arm"])["success"].mean().unstack()'),
        md("## 9. Normalize the crosstab\n\nWhat fraction of each treatment arm came from each risk group?"),
        code('pd.crosstab(trial["risk_group"], trial["treatment_arm"], normalize="columns")'),
        md(
            "## The four-step Simpson check\n\n"
            "1. Overall result\n"
            "2. Plausible group variable\n"
            "3. Result inside groups\n"
            "4. Group composition\n"
        ),
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
            "## Discussion\n\n"
            "- Which number would be easiest to put in a report?\n"
            "- Which number would be more honest?\n"
            "- What is driving the reversal — composition or biology?\n"
        ),
        md(
            "## Takeaway\n\n"
            "Functions introduced: `groupby`, `.agg`, `pd.crosstab`, `value_counts`.\n\n"
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
    )
    + [
        md(
            "## The story\n\n"
            "Revenue exists for surviving startups. Failed startups often "
            "have missing revenue, or vanish from the dataset entirely. If "
            "you only analyze survivors, you are studying winners and "
            "calling it the population."
        ),
        md("## 1. Load the startup dataset"),
        code('startups = pd.read_csv("../data/startup_survivorship.csv")\nstartups.head()'),
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
            "## 9. The biased headline vs. the honest one\n\n"
            "What does the headline 'average startup revenue' look like "
            "from each table?"
        ),
        code(
            'biased = survivors_only["year3_revenue_millions"].mean()\n'
            'honest_zero_fill = startups["year3_revenue_millions"].fillna(0).mean()\n'
            'print(f"Survivor-only average revenue: {biased:.2f}M")\n'
            'print(f"All startups (failed = 0):     {honest_zero_fill:.2f}M")'
        ),
        md("## 10. Duplicate rows with `df.duplicated()`\n\nDuplicates are another row-level distortion."),
        code("startups.duplicated().sum()"),
        md("## 11. Remove duplicates with `df.drop_duplicates()`\n\nRemove duplicates only after checking what they represent."),
        code(
            'clean = startups.drop_duplicates()\n'
            'print(startups.shape, clean.shape)'
        ),
        md("## Mini-lab: missing failures"),
        code(
            'print(startups.isna().sum())\n'
            'print(startups["survived_3yr"].value_counts())\n'
            'survivors_only = startups.dropna(subset=["year3_revenue_millions"])\n'
            'print(startups.shape, survivors_only.shape)'
        ),
        md(
            "## Discussion\n\n"
            "- What would the dataset look like if it were scraped from "
            "success-story blog posts?\n"
            "- If we report the average revenue from `survivors_only`, what "
            "claim are we implicitly making about the failed startups?\n"
        ),
        md(
            "## Don't change data silently\n\n"
            "Prefer creating a new object over overwriting the original "
            "during EDA — your future self will thank you."
        ),
        code('survivors_only = startups.dropna(subset=["year3_revenue_millions"])'),
        md(
            "## Takeaway\n\n"
            "Functions introduced: `isna`, `isna().sum`, `fillna`, `dropna`, "
            "`duplicated`, `drop_duplicates`.\n\n"
            "**Concept learned: missing rows and missing values are evidence.**"
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
    )
    + [
        md(
            "## The story\n\n"
            "Most players spend little. A tiny group of 'whales' spends a "
            "lot. The 'average player' may not exist. Removing outliers "
            "here would delete the business model."
        ),
        md("## 1. Load the gaming dataset\n\nRows are players; columns include spend, sessions, and segment."),
        code('game = pd.read_csv("../data/gaming_outliers.csv")\ngame.head()'),
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
        md("## 8. What share of revenue comes from each segment?"),
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
            "## Takeaway\n\n"
            "Functions reinforced: `describe`, `value_counts`, `nunique`, "
            "`sort_values`, `groupby().agg`, `plot`.\n\n"
            "**Concept learned: outliers can be errors, edge cases, or the "
            "whole story.**"
        ),
    ]
)


NOTEBOOKS = {
    "01_datasaurus_always_plot.ipynb": datasaurus_cells,
    "02_simpsons_paradox.ipynb": simpsons_cells,
    "03_survivorship_bias.ipynb": survivorship_cells,
    "04_gaming_whales_outliers.ipynb": whales_cells,
}


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    for name, cells in NOTEBOOKS.items():
        nb = notebook(cells)
        path = out_dir / name
        path.write_text(json.dumps(nb, indent=1) + "\n")
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
