# Critical Review of the Eight Notebooks

A cell-by-cell audit of the notebooks **as students actually see them** — i.e. after
the generator pipeline (`strip_section_subtext` → `strip_mini_labs` →
`hoist_takeaway`) has run — cross-checked against the executed outputs committed in
the `.ipynb` files. Three questions guided the review:

1. Is there any circular or unfinished logic?
2. Is it clear to beginners *why* we do this, from a data-science / AI perspective?
3. Should any functions be removed or added?

Findings are ranked **P0** (a notebook's own output contradicts its story),
**P1** (unfinished/circular logic a student will notice), **P2** (clarity and
crediting), **P3** (polish). Every fix goes through `_build_notebooks.py`, never
the `.ipynb` files.

---

## P0 — The notebook's own output contradicts its narrative

### 1. Notebook 02 (Simpson's): the flip only happens in one of the two groups

The story cell promises: *"Inside both risk groups, the treatment performs
better."* The executed output says otherwise:

| | control | treatment | treatment better? |
|---|---|---|---|
| overall | 0.797 | 0.334 | no (huge gap) |
| high_risk | **0.300** | **0.288** | **no — still worse** |
| low_risk | 0.840 | 0.863 | yes (barely) |

The paradox as generated is only half there: stratifying shrinks the enormous
overall gap to near-parity, but the treatment does *not* win inside high_risk.
A student who reads the numbers carefully will catch the notebook in a false
claim — the worst possible outcome for a lesson about honest analysis.

**Fix options:** (a) regenerate `simpsons_paradox_treatment.xlsx` so the
treatment genuinely wins in both strata (the classic kidney-stone shape), or
(b) soften the story text to match reality ("the 46-point gap nearly vanishes
once you stratify"). Option (a) is the real Simpson's paradox and worth the
data regeneration.

### 2. Notebook 05 (Collider): the narrative describes the wrong effect

The cell after the two correlations says: *"Notice the correlation flips sign
or weakens dramatically."* The actual outputs are:

- Full pool: **−0.029** (essentially zero)
- Admitted only: **−0.353**

Nothing flips and nothing weakens — a relationship that *didn't exist* is
**created** by selection. That is arguably the more striking version of collider
bias, and the text should say exactly that: "two independent traits become
strongly negatively correlated once you only look at admitted students."

### 3. Notebook 03 (Survivorship): duplicate demo runs on data with zero duplicates

Sections 11–12 teach `duplicated()` / `drop_duplicates()`, but
`startups.duplicated().sum()` outputs `0`, and the before/after shapes print
identically: `(2400, 6) (2400, 6)`. The demo demonstrates nothing happening.

**Fix options:** (a) plant 3–5 genuine duplicate rows in
`startup_survivorship.json` (a plausible story: the same startup scraped from
two press lists — which even ties into the §10 merge lesson), or (b) frame the
zero explicitly as the *good* outcome: "0 is what you want to see — but check
every time." Option (a) gives the functions something real to do.

---

## P1 — Circular or unfinished logic

### Notebook 00 (Inspect & Clean)

- **The broken thing is never shown fixed.** §9 proves the poisoning:
  `select_dtypes(include="number")` returns nothing useful. §10 cleans the row
  and fixes the dtypes — but only shows `df.dtypes`. The loop never closes.
  Add one payoff line re-running `df.select_dtypes(include="number").head()`
  (or `.mean()`) so students see the exact call that failed now succeed.
- **The cleaned DataFrame is abandoned.** After §10, the notebook pivots to toy
  tables and `df` is never touched again. The payoff line above also fixes this.
- **Boolean masking is used but never explained.** §10 filters with
  `df[df["dataset"] != "test"]` and gallery item 1 uses
  `people[(people["age"] >= 0) & (people["age"] <= 120)]` — compound masks with
  `&` and mandatory parentheses — yet row-filtering-by-condition is never named
  or credited anywhere in the course. For beginners this is the single most
  important pandas idiom. Worth one short unnumbered cell and a Takeaway credit.

### Notebook 02 (Simpson's)

- §6 and §8 run the *identical* `groupby(["risk_group","treatment_arm"])["success"].mean()`;
  §8 only appends `.unstack()`. That's intentional (teaching `unstack`), but as
  rendered nothing says so — consider heading wording like "Reshape the same
  answer with `unstack()`" so it doesn't read as a new computation.
- **No plot.** One notebook after "Always plot," the Simpson's lesson — the most
  visual paradox in statistics — is all tables. A two-line grouped bar chart of
  the `unstack()` result (`.plot(kind="bar")`) would practice the sermon.

### Notebook 03 (Survivorship)

- **The zero-fill contradiction.** The generator's §6 text warns that filling
  missing revenue with 0 "implies the startup earned nothing — but maybe revenue
  was simply unrecorded." That warning is stripped by the pipeline (see P2), so
  the rendered notebook silently jumps to §9 where the zero-fill number is
  labeled `honest_zero_fill` / "the honest one." The §5 crosstab actually
  *justifies* the fill (revenue is missing **exactly** when the startup failed:
  1766/1766 and 0/634), but that connection is never stated. One sentence after
  §5 — "missingness here means *failed*, so treating missing revenue as 0 is
  defensible" — turns an apparent contradiction into the lesson.
- `describe()` is used in §6 one notebook *before* nb04 formally introduces it
  (see the crediting table in P2).

### Notebook 04 (Whales)

- **§9 is a dangling heading.** As rendered, "## 9. Should we remove the whales?"
  has no body, no code, and is followed directly by Discussion. The pipeline
  stripped the answer — the errors / rare-valid-users / the-business-itself
  trichotomy, which is this notebook's entire decision framework. Add the heading
  to `PRESERVE_SUBTEXT_HEADINGS` (or make it unnumbered so the body survives).
- **The honest number is never computed.** `describe()` shows mean $12.74 vs
  median $3.16 — a 4× gap — and the Discussion asks "What number would be more
  honest to report?" but the notebook never names or computes the median. Add
  `game["monthly_spend"].median()` next to the mean (see function additions).

### Notebook 05 (Collider)

- **The `data_source` clue is dropped mid-thought.** §2 says a source column
  "reveals how rows entered the table," shows the counts (4000 `applicant_pool`
  + 1000 `admitted_students_file`), and never mentions it again. This column is
  actually the notebook's best evidence — the table was stitched together from
  two differently-selected sources. One follow-up sentence would land it.
- **`interview_score` is never used** anywhere in the notebook. Either give it a
  role (it's presumably part of the admission rule) or note that a real audit
  would ask about it.
- **§6 compound conditions have no story.** Two `.query(...).shape` calls print
  bare tuples that are never interpreted and don't connect to the collider
  narrative. Either tie them in ("this is the actual admission rule — how many
  got through the doorway?") or cut the section.

### Notebook 06 (Regression to the Mean)

- **`extremes` is built and never used.** §4's heading says "to compare against
  the middle," `pd.concat` builds the both-tails group, `.shape` prints — and the
  comparison never happens. Complete it (one cell:
  `extremes["change"].abs().mean()` vs the middle 80%'s), or cut the section.
  Completing it is better: it's the notebook's only use of `pd.concat`, which
  currently has no payoff.
- **§7 exactly duplicates §6.** §6 shows the 3×3 correlation matrix (which
  already contains baseline↔change = −0.527); §7 re-prints the 2×2 subset of the
  same matrix. The generator's explanation for §7 (change scores are negatively
  coupled to baseline *automatically*, because the noise subtracts out) is
  stripped by the pipeline, so what renders is an unexplained repeat. Preserve
  the body text (that's the actual insight) or merge §7 into §6.
- Minor: the extreme-group size changes from 20 (§2) to 100 (§3) to 60 (§4) with
  no rationale — pick one, or say why.

### Notebook 07 (Leakage)

- **The column-audit framework is stripped.** §2's body — classify every column
  as identifier / outcome / predictor / date / proxy / leak — is this notebook's
  core method, and the pipeline removes it, leaving a bare heading over
  `list(churn.columns)`. Add `## 2. Column audit with `df.columns`` to
  `PRESERVE_SUBTEXT_HEADINGS`. (The later "Why each drop" cell survives, so the
  taxonomy currently only appears *after* the drops it should have motivated.)
- **`to_datetime` has no payoff.** §5 converts `signup_date` and the dates are
  never used again. One line — `churn["signup_date"].dt.year.value_counts()` or
  a min/max range check — shows *why* proper datetimes matter and adds the `.dt`
  accessor to the course (see additions).
- Minor: §6 `numeric.corr(numeric_only=True)` — the `numeric_only` flag is
  redundant right after `select_dtypes(include="number")`; it quietly suggests
  the select step didn't work.

---

## P2 — Root cause + beginner clarity from a DS/AI perspective

### The stripping pipeline is deleting load-bearing teaching

Most P1 items above share one cause: `strip_section_subtext` removes the body of
every numbered heading not in `PRESERVE_SUBTEXT_HEADINGS`, and several bodies
carried the actual insight, not decoration. Recommended additions to the
preserve list (or convert these headings to unnumbered so the rule doesn't apply):

| Heading | What is lost as rendered |
|---|---|
| nb04 `## 9. Should we remove the whales?` | The whole errors/edge-cases/business trichotomy (dangling heading) |
| nb07 `## 2. Column audit with df.columns` | The identifier/outcome/predictor/proxy/leak taxonomy |
| nb06 `## 7. Change scores need suspicion` | Why baseline↔change correlation is automatic (mathematical coupling) |
| nb03 `## 6. Fill carefully with df.fillna()` | The zero-fill-can-be-wrong warning that §9 later depends on |
| nb06 `## 3. Compare change in the extreme groups` | The prediction (lows rise, highs fall) that makes the output a test rather than a fact |
| nb00 `## 4. Random glance with df.sample()` | Why sample beats head on sorted data ("stage-managed evidence") |

Also: the Mini-lab cells still live in the generator but are always stripped —
dead weight; delete them from the cell lists or stop stripping them.

### Why-this-matters gaps (the AI/DS motivation question)

The bias stories are strong, but the bridge to *models* is mostly implicit. Each
notebook needs at most one sentence, in the story cell:

- **nb00** — the title and hook image say "poisoned data" (an AI-security term),
  but the text never mentions models. Add: a model trained on garbage learns
  garbage; deliberate data poisoning is exactly this, done on purpose to an AI
  training set.
- **nb07** — leakage is the #1 practical ML failure mode, and the story stops at
  "look powerfully predictive." Add: a model trained on a leaky column looks
  excellent offline and fails on day one in production, because the leak doesn't
  exist at prediction time.
- **nb05** — perfect ML tie-in available: a loan-default model trained only on
  *approved* loans is trained behind the doorway; that's collider bias in every
  production training set. One line in "Collection questions."
- **nb06** — ties directly to A/B tests and "we intervened on the worst cases and
  they improved": the control-group question in the Discussion is good; naming
  A/B testing would anchor it.
- **nb02** — optional: aggregate model metrics can hide per-group reversals
  (fairness auditing is stratification).
- **nb01** — already strong. One soft spot: the Anscombe cell uses
  `np.polyfit` — a mid-notebook `import numpy` and a regression fit before
  students know what regression is. The panel labels carry it, but one framing
  line ("the dashed line is the straight line a model would fit") would help.

### "Always plot" is preached once and then skipped

nb01's thesis is *always plot*; then nb02, nb03, and nb07 contain zero plots.
nb02 is the clearest miss (grouped bars of the stratified rates). nb03 could
plot survivor-vs-full revenue distributions in ~3 lines. nb07 is defensible
without one. Even fixing only nb02 removes the mixed message.

---

## P2 — Function audit (currently 45 credited; goal: meet or exceed 40)

### Suggested additions (high value, low learner load) → brings total to ~49

| Function | Where | Why |
|---|---|---|
| `median` | nb04, next to the mean | Answers the notebook's own Discussion question; the $12.74-vs-$3.16 punchline deserves code |
| `between` | nb00 gallery item 1 | `people["age"].between(0, 120)` is the idiomatic range check, more readable than the chained mask |
| `.dt` accessor (e.g. `dt.year`) | nb07 §5 payoff | Gives `to_datetime` a reason to exist in the lesson |
| Boolean masking `df[cond]` | nb00 (name + credit it) | Already used in §10 and the gallery; the most fundamental idiom in the course is currently uncredited |

### Suggested removals

None. Per the standing instruction, unique primaries (`loc`, `iloc`, `concat`,
…) stay. The only deletion candidate found is a *crediting* artifact:
nb03 lists `` `isna().sum` `` as its own introduced item — it's a chain of two
already-credited functions, so it pads the count without teaching anything new.
Remove it from the Takeaway line (keep the code).

### Crediting inconsistencies (introduced-vs-reinforced chain is muddled)

| Function | Current chain | Problem / fix |
|---|---|---|
| `corr` | nb01 "featured", nb05 **introduced**, nb06 **introduced** | Introduced twice. Make nb01 introduce; nb05/nb06 reinforce |
| `value_counts` | nb00 gallery, nb02 **introduced**, nb03 **introduced**, nb04 reinforced | Introduced three times. Introduce once (nb00 or nb02), reinforce after |
| `pd.crosstab` | nb02 **introduced**, nb03 **introduced**, nb07 reinforced | Introduce in nb02 only |
| `sort_values` | used in nb03 code (uncredited), nb04 "reinforced", nb06 **introduced** | Backwards: it's reinforced before it's introduced. Introduce at first use (nb03) or in nb04, then reinforce |
| `describe` | **used in nb03 §6**, introduced nb04 | Order violation. Either credit it in nb03, or change nb03 §6 to `.mean()` |
| `nunique` | **used in nb01** (hide-unused-axes cell), introduced nb04 | Same pattern; harmless in a comment-adjacent role, but worth knowing |
| `plot` | nb01 featured, nb04 reinforced; used in nb05/nb06 uncredited | Never formally "introduced" anywhere; nb01 should own it |
| nb07 Takeaway | one merged "introduced / reinforced" list | A beginner can't tell what's new. Split: new = `pd.read_html`, `to_datetime`, `drop`; reinforced = the rest |

---

## P3 — Polish

- nb01: `import numpy as np` happens mid-notebook inside the Anscombe cell;
  course convention puts imports in the Imports cell.
- nb01: `dino.groupby("dataset")[["x","y"]].corr()` renders a 26-row MultiIndex
  table for what is one number per dataset — consider noting "read the x↔y
  off-diagonal" or unstacking to one column, since beginners will not know where
  to look.
- nb05 §8 (`loc` with mask) re-does §3's `query` filter; intentional contrast,
  but no surviving text says "same result, two idioms" — one clause would do.
- Generator hygiene: Mini-lab cells are dead code (always stripped); the
  `interview_score` column in the collider data is unused (see P1).

---

## Suggested order of attack

1. **P0.1** Regenerate nb02 trial data so the flip is genuine (or reword the story).
2. **P0.3** Plant duplicates in the startup JSON (or reframe the zero).
3. **P0.2** Rewrite the nb05 correlation sentence to "selection *creates* a correlation."
4. **P1** Close the loops: nb00 re-run `select_dtypes`; nb06 finish the `extremes`
   comparison; nb04 un-dangle §9; nb07 date payoff.
5. **P2** Extend `PRESERVE_SUBTEXT_HEADINGS` per the table; add the one-line AI
   bridges; add the nb02 bar chart.
6. **P2** Function crediting cleanup + additions (`median`, `between`, `.dt`,
   boolean masking).
7. **P3** at leisure.
