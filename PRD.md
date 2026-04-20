# PRD — Meal Planner Agent

**Owner:** AP
**Status:** Prototype (v0.1) — built 2026-04-19
**Scope of this doc:** What the prototype must do, who it's for, and how we'll know it's working.

## Background

Weekly meal planning consumes ~30 minutes of working-memory-heavy thinking every Sunday. The cost isn't the cooking — it's deciding what to cook under simultaneous constraints (dietary restrictions, Casey's preferences, variety, macro targets tied to athletic performance, and what's actually been tested). This agent externalizes those constraints into a database so the decision becomes a 5-minute review instead of a 30-minute invention exercise.

## Goals

1. Reduce weekly meal planning to <5 minutes (from 30+).
2. Guarantee no plan violates gluten/dairy/egg restrictions.
3. Surface variety automatically (no repeats within 14 days).
4. Produce a shopping list that requires no additional thought to shop from.
5. Grow the trusted-recipe corpus organically as new meals are cooked.

## Non-goals (prototype)

- Calorie/macro optimization across the week
- Breakfast, snacks, or beverages
- Recipe scraping / URL parsing
- Grocery delivery handoff
- Any UI beyond CLI + markdown output

## Users

- **Primary:** AP (single user, local machine).
- **Secondary awareness:** Casey — a partner whose preferences are captured in `preferences` but who does not use the tool directly.

## User stories

- _As AP, after cooking a new recipe on Tuesday,_ I run `add_recipe.py` and log the recipe in under 2 minutes so it's eligible for future plans.
- _As AP, on Sunday evening,_ I run `plan_meals.py` and get 5 lunches, 5 dinners, and a shopping list in `weekly_plan.md` with no input required.
- _As AP, when I want to try a new ingredient (e.g., tempeh),_ I add it as a `try` preference and the planner will occasionally slot in a recipe that uses it.
- _As AP, when I discover a new substitution (e.g., aquafaba for eggs in baking),_ I add it to `substitutions` and the shopping list reflects it automatically.

## Functional requirements

### Data model
- **recipes** — name, ingredients (JSON array), macros (JSON object), tags (JSON object with cuisine/protein_type/cook_time_minutes/meal_type), last_cooked, rating 1–5, casey_approved, notes, source_url.
- **preferences** — food_item, category (`love` / `like` / `try` / `avoid`), applies_to (`me` / `casey` / `both`), notes.
- **substitutions** — original_ingredient, substitute, context.

### CLIs
- `init_db.py` — create schema + seed baseline avoids (gluten, dairy, eggs).
- `add_recipe.py` — conversational entry; only `name` required.
- `add_preference.py` — `food_item × category × applies_to`.
- `add_substitution.py` — `original → substitute` with optional context.
- `bulk_import.py` — ingest `data/recipes_seed.md` and `data/preferences_seed.md`.
- `plan_meals.py` — produce a weekly plan.

### Planner rules
1. Candidate recipes = rating >= 4 AND casey_approved.
2. Exclude any recipe whose ingredients contain an `avoid` food (for `me` or `both`) **when that avoid has no substitution defined**. If every avoid-match in the recipe has a substitution in the `substitutions` table, the recipe is eligible and the shopping list applies the swap. Hard-avoids with no substitution (mushrooms, salmon, seafood, tofu, etc.) continue to filter the recipe out.
3. Prefer recipes not cooked in the last 14 days.
4. Include 1–2 recipes featuring a `try` preference, when the pool allows.
5. 5 lunches + 5 dinners; 2 weekdays intentionally unfilled (flex for leftovers / takeout / improvise).
6. Shopping list is consolidated across all 10 recipes and rewrites entries when a matching substitution exists.

## Non-functional requirements

- Python 3 standard library only. No external installs.
- Local-first. SQLite file lives next to the scripts.
- Runs on macOS / Python 3.9+ without setup beyond `python init_db.py`.
- All CLIs survive mid-entry `Ctrl-C` without corrupting the DB.

## Success metrics

Prototype is working if, after 4 weeks of use:
- At least 20 recipes are in the database with ratings.
- Weekly planning time is under 5 minutes (measured subjectively).
- Zero dietary-restriction violations in generated plans.
- AP references `weekly_plan.md` during actual cooking (i.e., it's not write-only).

## Open questions

- Do we also surface a "recently cooked, skipping this week" list for transparency?
- Should breakfasts move into scope in v2, or stay manual?
- Integration point with `/planweek` skill — does the Sunday routine call this, or stay separate?
