# Notebook consistency review — 2026-07-15

Method: read all eight notebooks as they render after the build pipeline
(mini-labs stripped, Takeaway hoisted to the top), then cross-checked every
numeric claim in the prose against the committed executed outputs and the raw
data files. Findings are ordered by how much they would mislead a student;
each has a suggested fix. Nothing has been changed yet.

**Verified correct along the way** (no action needed): nb02's paradox numbers
(overall control 0.72 vs treatment 0.46; treatment wins both strata 0.35/0.28
and 0.90/0.83), all of nb03's imputation and two-stage numbers (1,769 filled
vs 634 real; corr 0.138→0.076; −0.017→+0.129; std 17.17→8.81; 26.4% × 20.31M
= 5.36M, ratio 3.79 ≈ "almost 4x"), nb05's correlations (full −0.029,
admitted −0.353), nb06's corr(baseline, change) = −0.527 and tail drifts
(+18.19 / −12.93), and nb04's mean 12.74 / median 3.16.

---

## P1 — narrative contradicts what the student actually sees

### 1. nb07 §6 "Find suspicious correlations" cannot find the suspect
`select_dtypes(include="number")` excludes bool columns, and both `churned`
and `refund_after_churn` are bool. The correlation table therefore shows only
`age`, `tenure_months`, `support_tickets`, `last_login_days_ago` — the
follow-up cell says "Pay special attention to anything that correlates
strongly with `churned`", but `churned` is not in the table, and neither is
the leak we are hunting. The section's task is impossible with its own
output; §7 then pivots to "smells like a leak — by name alone", which papers
over the gap.
**Fix:** cast the bools for this one computation, e.g.
`churn.assign(churned=churn["churned"].astype(int), refund_after_churn=...)`
or `select_dtypes(include=["number", "bool"]).astype(float).corr()` — then
the ~strong churned↔refund correlation actually appears and §7's crosstab
becomes a confirmation instead of a rescue.

### 2. nb07 §4 `astype` demo is a no-op on this file
`churn.info()` right after loading already shows `churned` (and
`refund_after_churn`) as `bool` — `read_html` parsed them. So §4's rationale
("a yes/no stored as text sorts alphabetically and quietly breaks
comparisons") describes a problem this file does not have, and the
`astype("bool")` call changes nothing a student can observe.
**Fix:** either store `churned` as `"yes"/"no"` text in the generated HTML
data so the conversion is real, or re-target §4 at a column that genuinely
needs casting.

### 3. nb07 ending overstates the leak's predictive power
"Why this matters to an AI engineer" says `refund_after_churn` "can predict
churn almost perfectly". The crosstab says otherwise: of 471 churners, only
167 got a refund (304 did not). The true statement is one-directional — every
refund implies churn (167/167, zero refunds among non-churners), i.e. perfect
precision but ~35% recall.
**Fix:** reword to the one-way claim ("every customer with a refund churned —
the feature is a certificate of churn when present"), which is also the more
instructive shape for a leak.

### 4. nb00 §7–§8 say `object`, the output says `str`
The environment runs pandas 3, where text columns load as the `str` dtype.
`df.info()` prints `str(3)` and `df.dtypes` prints `str` — but §8's text
says "`x` and `y` … show up as `object` (text)". A student scanning the
output for "object" will not find it.
**Fix:** update the wording to "show up as `str`/text instead of numbers"
(optionally noting older pandas prints `object`).

### 5. nb04 hook image contradicts the notebook's own data
The whales infographic claims "Top 1% = 50%+ of total spend" and "the rest
(95%+) ~20%". The dataset the students then analyze gives whales (1% of
players) **30.1%** of revenue, dolphins 36.0%, minnows **34.0%**. The
notebook's §8 table sits directly under a poster asserting different numbers;
an attentive student will notice.
**Fix options:** regenerate the image without specific percentages, regenerate
the data so whales really carry ~50%, or add a caption noting the poster
shows a typical industry pattern while this dataset is milder.

---

## P2 — logical loose ends

### 6. nb06 §4 promises a comparison that never happens
"Concatenate the two extreme tails **to compare against the middle**" — the
`extremes` frame is built, its shape printed, and it is never touched again.
No middle group is ever constructed.
**Fix:** either add the payoff cell (mean change of extremes vs. the middle
1,000 students — the middle should drift ≈ 0, which strengthens the lesson)
or trim the sentence to stop promising the comparison.

### 7. nb03 finds duplicates, then keeps analyzing the duplicated table
§12–13 teach `duplicated()`/`drop_duplicates()` ("duplicates silently
double-count whatever you sum or average"), but every later computation (the
imputation-danger cell, the two-stage model) still uses the un-deduped
`startups`. Two wrinkles: (a) the notebook contradicts its own advice right
after giving it; (b) the planted duplicates are failed rows with null
revenue, so they cannot demonstrate the stated harm — revenue sums and means
are unchanged, and `p_survive` moves only from 26.42% to 26.38%.
**Fix:** simplest is to reorder — find/drop duplicates before §10 and use
`clean` afterwards; or add one honest sentence at §13 ("here the duplicates
are failed rows with no revenue, so the totals above survive — but check
before assuming that").

### 8. nb05 loose ends (currently hidden from the site, still in the repo)
- `interview_score` is in the data and never referenced by any cell. Either
  use it (it is a natural third variable for §6's compound conditions) or it
  reads as an unused prop.
- §9's why-sentence claims `iloc` "confirm[s] the table matches what the
  label-based `loc` returned above", but the output shows different columns
  (`applicant_id`…`interview_score`) over all rows, not §8's
  ability/portfolio over admitted rows. The confirmation it promises is not
  possible from that output.
- §6's two `query` results (shapes only) get no interpreting sentence — the
  one heading in the course whose output is never read.

### 9. nb05 `data_source` labels are subtly misleading
`applicant_pool` (4,000 rows) contains only the *rejected* applicants;
`admitted_students_file` (1,000) holds all the admitted ones. The true
applicant pool is the union. §2 presents `data_source` as "how rows entered
the table", which is right, but a student who filters
`data_source == "applicant_pool"` believing it is the full pool gets a
group with corr −0.169 (selection on *non*-admission — the complement
doorway). **Fix:** rename the source values (e.g. `rejected_applicants`) or
add one sentence in §2 saying the full pool = both sources combined.

### 10. nb07 small dangling threads
- `age` has 122 missing values (visible in `info()`); they are never
  mentioned until they silently explain §9's `dropna()` row count
  (3,018 → 2,896). One clause in §9 would close the loop.
- `signup_date` is converted with `to_datetime` in §5 and then never used.
  A one-line payoff (e.g. earliest/latest signup, or tie into the leakage
  audit: "is any date *after* the churn event?") would justify the section
  beyond the type conversion.

---

## P3 — consistency nits

11. **nb01 and nb02 both open with `read_excel`** since the datasaurus data
    moved to `.xlsx` — CLAUDE.md's one-reader-per-notebook rule is broken.
    If distinct readers still matter, nb02 could move to another format
    (no primary reader is left unused except `read_html`, taken by nb07 —
    so either accept the duplicate or use e.g. `read_csv` with a non-default
    separator/compression as its own lesson).
12. **nb01's Takeaway says "Functions featured"** where every other notebook
    says "Functions introduced" (the site parser handles both; only a
    consistency nit).
13. **nb01's hook image shows the dinosaur** (and the other shapes) above the
    story cell that says "you never see the dinosaur" until you plot. The
    hoisted Takeaway already spoils conclusions by design, so this may be
    intended — flagging so it is a decision, not an accident.
14. **White-font Discussion answers are only invisible on light backgrounds.**
    In dark-mode renderers (VS Code, JupyterLab dark, GitHub's dark notebook
    view) `#ffffff` text on a dark background is fully readable. The Pages
    site is light, so the mechanism works there; if students open the .ipynb
    in dark editors, the answers are exposed.
15. **Hiding nb05 removes its function chips from the site index** —
    `pd.read_feather`, `query`, `loc`, `iloc` no longer appear anywhere on
    the published page, so the site's visible function coverage drops by
    four. If collider stays hidden long-term, consider whether `query`/`loc`/
    `iloc` should be introduced in another notebook.
16. **A few why-use sentences still predate the new rule** (state the reason
    and what the output should show): nb02 §2 ("Identify the comparison, the
    outcome, and the possible confounder" — could name `risk_group` as the
    suspected confounder), nb03 §4 ("Survivorship analysis starts with the
    outcome distribution"), nb06 §2 ("Sorting reveals the selected
    extremes"). All borderline rather than wrong.
