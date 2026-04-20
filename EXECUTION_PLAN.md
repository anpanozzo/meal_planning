# Execution Plan — Meal Planner Agent

## Phase 0 — Foundation (DONE, 2026-04-19)

- [x] Create `meal-planner/` under the Obsidian vault
- [x] Write schema (`recipes`, `preferences`, `substitutions`) with CHECK constraints
- [x] `init_db.py` — idempotent DB setup + seed baseline avoids
- [x] `add_recipe.py` / `add_preference.py` / `add_substitution.py` — interactive CLIs
- [x] `plan_meals.py` — selection + shopping list + markdown output
- [x] `README.md` + `PRD.md`

## Phase 1 — Seed the corpus (NEXT, target 1 week)

Goal: get to a place where `plan_meals.py` produces a usable plan without re-adding recipes each session.

- [ ] Build `bulk_import.py` — parse `data/recipes_seed.md` + `data/preferences_seed.md`
- [ ] Draft `data/recipes_seed.md` with 15–20 known-good recipes (pull from the vault's Functional Medicine recipe file and anything else AP has made + liked)
- [ ] Draft `data/preferences_seed.md` — Casey's likes/dislikes, AP's `try` list, any additions beyond baseline avoids
- [ ] Seed substitutions: GF flour swaps, dairy-free milks, egg replacers
- [ ] Run `bulk_import.py`; spot-check DB contents
- [ ] Run `plan_meals.py`; review `weekly_plan.md` with AP

**Exit criteria:** At least 12 recipes are eligible (rating ≥ 4, casey_approved) and plan_meals produces 5 lunches + 5 dinners without fallback warnings.

## Phase 2 — Weekly adoption (target 4 weeks)

- [ ] Use `plan_meals.py` every Sunday for 4 consecutive weeks
- [ ] After each cook, log via `add_recipe.py` (or update rating if a repeat)
- [ ] Track subjective planning time — is it actually <5 min?
- [ ] Track which recipes get repeated vs ignored — are 4+ ratings too generous?
- [ ] Decide: does this get called from `/planweek`, or stay standalone?

**Exit criteria:** 4 consecutive Sundays of use, corpus at 20+ recipes, zero restriction violations.

## Phase 3 — Refine (as-needed)

Triggered by friction, not a calendar. Candidates:

- [ ] Add a `why` summary to the plan output (e.g., "repeats Thai Curry because nothing else in pool was stale enough")
- [ ] Allow "skip this recipe" flag on the plan, regenerate
- [ ] Weekly macros rollup in the plan header
- [ ] Pull source URLs from the Functional Medicine recipes file automatically
- [ ] Integration with `/planweek` — e.g., offer "generate meal plan?" during the Sunday routine

## Decision log

- **2026-04-19 — JSON in TEXT columns for ingredients/macros/tags.** Simpler than normalized tables; queryability is not yet a bottleneck. Revisit if we need to query by ingredient.
- **2026-04-19 — Rating ≥ 4 AND casey_approved as hard filter.** "Like" but not "love" recipes can still be added; they just need to earn their way in via rating.
- **2026-04-19 — Substring match for avoid filtering.** Good enough for a prototype; will miss weird cases ("dairy-free milk" would still contain "dairy" substring). If it causes a false positive in practice, switch to tokenized match.
- **2026-04-19 — 14 days as the "stale" threshold.** Arbitrary but round. Revisit after 4 weeks of use.
- **2026-04-19 — Substitutions waive the avoid filter.** If an avoid ingredient has a defined substitution, the recipe is not dropped — the shopping list applies the sub instead. Rationale: AP routinely substitutes dairy/gluten/eggs and doesn't want those to block meal selection. Hard-avoids (mushrooms, salmon, seafood, tofu) have no substitutions and continue to drop recipes. To re-enable strict filtering for a specific avoid, delete its substitution row.

## Risks

- **Corpus too small at launch → planner returns fewer than 5 meals per slot.** Mitigation: Phase 1 explicitly seeds 15+ recipes before declaring done.
- **Substring-matching false positives on avoid list.** Mitigation: review weekly_plan.md before shopping; fix with tokenization if it bites.
- **Casey's preferences drift and don't get updated.** Mitigation: include a "anything new for Casey?" prompt in the /planweek Sunday routine (future).
