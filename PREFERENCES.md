# Adding Food Preferences

How to tell the planner what you and Casey like, dislike, or want to try.

## Where preferences live

- **`data/preferences_seed.md`** — canonical, version-controlled. Edit this.
- **`meal_planner.db`** — what the planner reads. Generated from the seed file via `bulk_import.py`.

Edit the seed file, run `bulk_import.py`, commit, push. The DB is reproducible from the seed.

## The three fields

Every preference is three pieces of info:

| Field | Values | Meaning |
|---|---|---|
| `food_item` | any string | ingredient or food name, e.g., `mushrooms`, `heavy cream`, `tempeh` |
| `category` | `love` / `like` / `try` / `avoid` | how the planner should treat it |
| `applies_to` | `me` / `casey` / `both` | whose preference this is |

### What each category does

- **`avoid`** — filters the recipe out of meal planning, **unless** a matching substitution exists (see next section).
- **`try`** — planner slots 1–2 recipes per week that contain these ingredients.
- **`love`** / **`like`** — informational for now. May influence prioritization later.

### What each `applies_to` does

- **`me`** — Abby's preference.
- **`casey`** — Casey's preference.
- **`both`** — shared.

All three (`me`, `casey`, `both`) apply to the avoid filter — Casey eats what Abby cooks, so his avoids filter the same as Abby's. Use `both` when it's genuinely shared (saves a line).

## Avoid vs. substitute — the important nuance

The avoid filter is **substitution-aware**. If an avoid has a matching substitution, the recipe stays eligible and the shopping list applies the swap.

| Want the recipe dropped | Set as `avoid`, do NOT add a substitution |
| Want the recipe kept with a swap | Set as `avoid` AND add a substitution |

**Current hard avoids** (drop the recipe): mushrooms, salmon, seafood, fish, shrimp, tuna, cod, halibut, tofu, black beans, pinto beans.

**Current soft avoids** (recipe stays, ingredient gets swapped): butter, cheese variants, yogurt, cow's milk, heavy cream, pasta, wheat, eggs, and their variants.

To flip a soft avoid into hard, delete its row in `## substitutions`. To flip hard into soft, add a substitution.

## Worked examples

### Casey hates fennel

Edit `data/preferences_seed.md`:

```markdown
## avoid / casey
- seafood
- fish
- fennel          ← new line
```

Then:
```
python3 bulk_import.py
git add data/preferences_seed.md
git commit -m "Add fennel to Casey avoids"
git push
```

### Abby wants to try farro

```markdown
## try / me
- tempeh
- miso
- farro           ← new line
```

Planner will try to slot in a recipe with farro next week.

### Add a substitution so a soft-avoided ingredient gets swapped

```markdown
## substitutions
- fennel -> celery (in soups)
```

Now recipes with fennel stay eligible; shopping list says "celery (sub for fennel)".

### Section doesn't exist yet (e.g., no `## love / casey`)

Just add it:

```markdown
## love / casey
- steak
- sweet potatoes
```

Header format is always `## category / applies_to`.

## Shortcuts (no git involved)

`python3 add_preference.py` — interactive CLI, writes only to the DB. Use when you don't care about version-controlling this particular entry. **These entries are lost if the DB is rebuilt from the seed file.** Prefer editing `preferences_seed.md` when possible.

`python3 add_substitution.py` — same pattern for substitutions.

## Gotchas

1. **Substring matching.** The avoid filter case-insensitively checks whether each avoid string appears anywhere in any ingredient. `cheese` catches `parmesan cheese` AND `cream cheese`. That's usually what you want, but watch for false positives on unusual words.
2. **Specific beats generic.** Use `cow's milk` rather than `milk` so you don't accidentally filter out recipes with `coconut milk` or `almond milk`.
3. **`bulk_import.py` is idempotent.** Duplicates (same food + category + applies_to) are skipped. Safe to re-run.
4. **Don't edit the DB directly.** Use the seed file. The DB is derived.
5. **Baseline avoids are re-seeded on rebuild.** `gluten`, `dairy`, `eggs` for `me` come from `init_db.py`. If you want to remove one of those, edit `init_db.py` itself — don't just delete from the DB (it'll come back on next `init_db.py` run).
