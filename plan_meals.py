"""Generate a weekly meal plan (5 lunches + 5 dinners) and a consolidated shopping list.

Selection rules:
  - Recipes must be rated >= 4 AND casey_approved.
  - Exclude any recipe whose ingredients contain a food in the 'avoid' category for 'me' or 'both'.
  - Prioritize recipes not cooked in the last 14 days.
  - Include 1-2 recipes that feature a 'try' preference food, when available.
  - 2 weekdays are left flexible (leftovers / takeout / improvise).
"""
import sqlite3
import json
import os
import random
from datetime import date

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'meal_planner.db')
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weekly_plan.md')

LUNCHES_NEEDED = 5
DINNERS_NEEDED = 5
TRY_CAP = 2
STALE_DAYS = 14


# --- DB loaders ---

def load_avoid_list(conn):
    c = conn.cursor()
    c.execute(
        "SELECT food_item FROM preferences WHERE category='avoid' AND applies_to IN ('me', 'both')"
    )
    return [row[0].lower() for row in c.fetchall()]


def load_try_list(conn):
    c = conn.cursor()
    c.execute("SELECT food_item FROM preferences WHERE category='try'")
    return [row[0].lower() for row in c.fetchall()]


def load_substitutions(conn):
    c = conn.cursor()
    c.execute('SELECT original_ingredient, substitute, context FROM substitutions')
    return [(row[0].lower(), row[1], row[2]) for row in c.fetchall()]


def fetch_candidate_recipes(conn, avoid_list):
    c = conn.cursor()
    c.execute(
        '''
        SELECT id, name, ingredients, macros, tags, last_cooked, rating, notes, source_url
        FROM recipes
        WHERE rating >= 4 AND casey_approved = 1
        '''
    )
    recipes = []
    for row in c.fetchall():
        ingredients = json.loads(row[2]) if row[2] else []
        if contains_any(ingredients, avoid_list):
            continue
        recipes.append({
            'id': row[0],
            'name': row[1],
            'ingredients': ingredients,
            'macros': json.loads(row[3]) if row[3] else {},
            'tags': json.loads(row[4]) if row[4] else {},
            'last_cooked': row[5],
            'rating': row[6],
            'notes': row[7],
            'source_url': row[8],
        })
    return recipes


# --- Selection helpers ---

def contains_any(ingredients, needles):
    if not needles:
        return False
    haystack = ' '.join(ingredients).lower()
    return any(n in haystack for n in needles)


def days_since(date_str):
    if not date_str:
        return 10 ** 6
    try:
        return (date.today() - date.fromisoformat(date_str)).days
    except ValueError:
        return 10 ** 6


def eligible_for_meal(recipe, meal_type):
    mt = recipe['tags'].get('meal_type')
    if not mt:
        return True  # untagged recipes are eligible for any slot
    return mt.lower() in (meal_type, 'both')


def pick_meals(pool, meal_type, needed, try_list, taken_ids, try_slots_remaining):
    """Pick `needed` recipes from the pool for this meal type, preferring stale-recent and try-list matches."""
    available = [r for r in pool if r['id'] not in taken_ids and eligible_for_meal(r, meal_type)]
    fresh = [r for r in available if days_since(r['last_cooked']) >= STALE_DAYS]
    recent = [r for r in available if days_since(r['last_cooked']) < STALE_DAYS]

    random.shuffle(fresh)
    random.shuffle(recent)

    picks = []

    # Pull in a 'try' recipe first if we have budget and there's one in the fresh pool
    if try_slots_remaining > 0 and try_list:
        try_picks = [r for r in fresh if contains_any(r['ingredients'], try_list)]
        if try_picks:
            picks.append(try_picks[0])

    for r in fresh + recent:
        if len(picks) >= needed:
            break
        if r['id'] not in {p['id'] for p in picks}:
            picks.append(r)

    return picks[:needed]


# --- Shopping list ---

def apply_substitution(ingredient, substitutions):
    """Return (display_name, original_or_None). Substitution triggers when the original ingredient name appears."""
    ing_lower = ingredient.lower()
    for original, substitute, context in substitutions:
        if original in ing_lower:
            ctx = f" — {context}" if context else ""
            return f"{substitute} (sub for {original}{ctx})", original
    return ingredient, None


def build_shopping_list(recipes, substitutions):
    items = {}  # display_name -> set of recipe names
    for r in recipes:
        for ing in r['ingredients']:
            display, _original = apply_substitution(ing, substitutions)
            items.setdefault(display, set()).add(r['name'])
    return items


# --- Output ---

def format_recipe_block(idx, r):
    lines = [f"### {idx}. {r['name']}"]
    tag_bits = []
    for k in ('cuisine', 'protein_type', 'cook_time_minutes'):
        if k in r['tags']:
            label = 'cook' if k == 'cook_time_minutes' else k
            val = f"{r['tags'][k]} min" if k == 'cook_time_minutes' else r['tags'][k]
            tag_bits.append(f"{label}: {val}")
    if tag_bits:
        lines.append('_' + ' · '.join(tag_bits) + '_')
    if r['macros']:
        m = r['macros']
        macro_bits = []
        for k, lbl in (('calories', 'cal'), ('protein_g', 'P'), ('carbs_g', 'C'), ('fat_g', 'F')):
            if k in m:
                macro_bits.append(f"{m[k]} {lbl}")
        if macro_bits:
            lines.append("Macros: " + ', '.join(macro_bits))
    if r['last_cooked']:
        lines.append(f"Last cooked: {r['last_cooked']} ({days_since(r['last_cooked'])} days ago)")
    if r['source_url']:
        lines.append(f"Source: {r['source_url']}")
    if r['notes']:
        lines.append(f"Notes: {r['notes']}")
    lines.append("")
    return '\n'.join(lines)


def write_plan(lunches, dinners, shopping_list, avoid_list, try_list):
    today = date.today()
    out = [f"# Weekly Meal Plan — {today.isoformat()}", ""]
    out.append(f"_Filters: rating >= 4, casey_approved, avoiding: {', '.join(avoid_list) or 'none'}._")
    if try_list:
        out.append(f"_Trying to incorporate: {', '.join(try_list)}._")
    out.append("")

    out.append("## Lunches")
    out.append("")
    for i, r in enumerate(lunches, 1):
        out.append(format_recipe_block(i, r))

    out.append("## Dinners")
    out.append("")
    for i, r in enumerate(dinners, 1):
        out.append(format_recipe_block(i, r))

    out.append("## 2 flex days")
    out.append("")
    out.append("Leftovers, takeout, or improvise. Use these when the week gets messy.")
    out.append("")

    out.append("## Shopping list")
    out.append("")
    if not shopping_list:
        out.append("_(no ingredients listed on any selected recipe — add ingredients in add_recipe.py)_")
    else:
        for item in sorted(shopping_list.keys(), key=str.lower):
            sources = sorted(shopping_list[item])
            out.append(f"- [ ] {item}  _for: {', '.join(sources)}_")
    out.append("")

    with open(OUTPUT_PATH, 'w') as f:
        f.write('\n'.join(out))


# --- Entry point ---

def main():
    conn = sqlite3.connect(DB_PATH)
    avoid_list = load_avoid_list(conn)
    try_list = load_try_list(conn)
    substitutions = load_substitutions(conn)
    recipes = fetch_candidate_recipes(conn, avoid_list)
    conn.close()

    if not recipes:
        print("No eligible recipes in the database yet.")
        print(f"Filters: rating >= 4, casey_approved = 1, avoiding: {', '.join(avoid_list) or 'none'}.")
        print("Run `python add_recipe.py` a few times, then re-run this.")
        return

    taken = set()
    lunches = pick_meals(recipes, 'lunch', LUNCHES_NEEDED, try_list, taken, TRY_CAP)
    taken.update(r['id'] for r in lunches)

    lunch_try_used = sum(1 for r in lunches if contains_any(r['ingredients'], try_list))
    dinner_try_budget = max(0, TRY_CAP - lunch_try_used)

    dinners = pick_meals(recipes, 'dinner', DINNERS_NEEDED, try_list, taken, dinner_try_budget)

    shopping_list = build_shopping_list(lunches + dinners, substitutions)
    write_plan(lunches, dinners, shopping_list, avoid_list, try_list)

    print(f"Selected {len(lunches)} lunches and {len(dinners)} dinners from {len(recipes)} eligible recipes.")
    if len(lunches) < LUNCHES_NEEDED or len(dinners) < DINNERS_NEEDED:
        print(f"Note: wanted {LUNCHES_NEEDED} lunches / {DINNERS_NEEDED} dinners but the pool was thin.")
    print(f"Wrote: {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
