"""Bulk import recipes, preferences, and substitutions from files in ./data/.

Sources (all optional — any that are missing are skipped):
  - data/Recipe Database.csv    — primary recipe source (canonical format)
  - data/recipes_seed.md        — legacy markdown recipe format (still supported)
  - data/preferences_seed.md    — preferences + substitutions

CSV columns expected (missing columns are fine):
  Recipe Name, Protein per Serving (g), Serving Size, Total Calories, Carbs (g), Fat (g),
  Recipe URL, Meal Type, Cooking Time, Difficulty, Flavor Profile, GF/DF Compatible,
  Ingredients, Notes, Rating, Casey Approved, Last Cooked

`Ingredients` should be a comma-separated list. Without it, plan_meals.py can't filter
on avoid-foods or generate a shopping list.

`Rating` and `Casey Approved` are optional. If missing, recipes import as unrated and
won't be eligible for plan_meals until you rate them (via add_recipe.py or by adding
columns to the CSV).

Preference/substitution format (data/preferences_seed.md):
  ## love / me
  - salmon
  ## avoid / both
  - mushrooms
  ## substitutions
  - butter -> ghee (savory dishes)

Duplicates are skipped (recipes by name; preferences by food_item+category+applies_to).
"""
import sqlite3
import json
import os
import re
import csv
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, 'meal_planner.db')
CSV_PATH = os.path.join(HERE, 'data', 'Recipe Database.csv')
RECIPES_MD_PATH = os.path.join(HERE, 'data', 'recipes_seed.md')
PREFS_PATH = os.path.join(HERE, 'data', 'preferences_seed.md')

TAG_KEYS = {'cuisine', 'protein_type', 'cook_time_minutes', 'meal_type'}
MACRO_KEYS = {'protein_g', 'carbs_g', 'fat_g', 'calories'}
INT_TAGS = {'cook_time_minutes'}


# --- CSV reader ---

def parse_cook_time(raw):
    """'35 min' -> 35, '5 min prep + overnight' -> 5, '' -> None."""
    if not raw:
        return None
    m = re.search(r'(\d+)', raw)
    return int(m.group(1)) if m else None


def parse_float(raw):
    if raw is None or raw == '':
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def parse_int(raw, lo=None, hi=None):
    if raw is None or raw == '':
        return None
    try:
        n = int(float(raw))
    except ValueError:
        return None
    if lo is not None and n < lo:
        return None
    if hi is not None and n > hi:
        return None
    return n


def parse_yn(raw):
    if raw is None or raw == '':
        return None
    s = raw.strip().lower()
    if s in ('y', 'yes', 'true', '1'):
        return 1
    if s in ('n', 'no', 'false', '0'):
        return 0
    return None


def normalize_meal_type(raw):
    if not raw:
        return None
    s = raw.strip().lower()
    # "Lunch/Dinner" -> "both"; "Dinner" -> "dinner"; "Breakfast/Snack" -> "breakfast"
    if 'lunch' in s and 'dinner' in s:
        return 'both'
    if 'dinner' in s:
        return 'dinner'
    if 'lunch' in s:
        return 'lunch'
    if 'breakfast' in s:
        return 'breakfast'
    return s


def parse_recipes_csv(path):
    if not os.path.exists(path):
        print(f"[csv] No file at {path} — skipping.")
        return []

    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        recipes = []
        for row in reader:
            name = (row.get('Recipe Name') or '').strip()
            if not name:
                continue

            ingredients_raw = row.get('Ingredients') or ''
            ingredients = [x.strip() for x in ingredients_raw.split(',') if x.strip()]

            macros = {}
            for key, col in (
                ('protein_g', 'Protein per Serving (g)'),
                ('carbs_g', 'Carbs (g)'),
                ('fat_g', 'Fat (g)'),
                ('calories', 'Total Calories'),
            ):
                v = parse_float(row.get(col))
                if v is not None:
                    macros[key] = v

            tags = {}
            mt = normalize_meal_type(row.get('Meal Type'))
            if mt:
                tags['meal_type'] = mt
            ct = parse_cook_time(row.get('Cooking Time'))
            if ct is not None:
                tags['cook_time_minutes'] = ct
            flavor = (row.get('Flavor Profile') or '').strip()
            if flavor:
                tags['cuisine'] = flavor  # approximate — flavor profile stands in for cuisine
            diff = (row.get('Difficulty') or '').strip()
            if diff:
                tags['difficulty'] = diff

            # Fold supplementary fields into notes so nothing is lost
            note_parts = []
            if row.get('Notes'):
                note_parts.append(row['Notes'].strip())
            if row.get('GF/DF Compatible'):
                note_parts.append(f"GF/DF: {row['GF/DF Compatible'].strip()}")
            notes = ' | '.join(note_parts) if note_parts else None

            recipes.append({
                'name': name,
                'ingredients': ingredients,
                'macros': macros,
                'tags': tags,
                'last_cooked': (row.get('Last Cooked') or '').strip() or None,
                'rating': parse_int(row.get('Rating'), lo=1, hi=5),
                'casey_approved': parse_yn(row.get('Casey Approved')),
                'notes': notes,
                'source_url': (row.get('Recipe URL') or '').strip() or None,
            })
        return recipes


# --- Markdown recipe reader (legacy) ---

def parse_recipes_md(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        text = f.read()

    blocks = re.split(r'^##\s+', text, flags=re.MULTILINE)
    recipes = []
    for block in blocks[1:]:
        lines = block.strip().splitlines()
        if not lines:
            continue
        name = lines[0].strip()
        if name.lower().startswith('example'):
            continue  # skip the example recipes in the stub
        fields = {}
        for line in lines[1:]:
            line = line.strip()
            if not line or line.startswith('#') or ':' not in line:
                continue
            key, val = line.split(':', 1)
            fields[key.strip().lower()] = val.strip()
        recipes.append(build_recipe_from_md(name, fields))
    return recipes


def build_recipe_from_md(name, fields):
    r = {'name': name}
    raw_ing = fields.get('ingredients', '')
    r['ingredients'] = [x.strip() for x in raw_ing.split(',') if x.strip()] if raw_ing else []

    macros = {}
    raw_macros = fields.get('macros', '')
    if raw_macros:
        for chunk in raw_macros.split(','):
            if '=' not in chunk:
                continue
            k, v = chunk.split('=', 1)
            k = k.strip().lower()
            if k in MACRO_KEYS:
                try:
                    macros[k] = float(v.strip())
                except ValueError:
                    pass
    r['macros'] = macros

    tags = {}
    for k in TAG_KEYS:
        if k in fields and fields[k]:
            v = fields[k]
            if k in INT_TAGS:
                try:
                    tags[k] = int(v)
                except ValueError:
                    continue
            else:
                tags[k] = v.lower() if k == 'meal_type' else v
    r['tags'] = tags

    r['last_cooked'] = fields.get('last_cooked') or None
    try:
        r['rating'] = int(fields.get('rating')) if fields.get('rating') else None
    except ValueError:
        r['rating'] = None
    casey = fields.get('casey_approved', '').lower()
    r['casey_approved'] = 1 if casey in ('y', 'yes', 'true', '1') else (0 if casey in ('n', 'no', 'false', '0') else None)
    r['notes'] = fields.get('notes') or None
    r['source_url'] = fields.get('source_url') or None
    return r


# --- Insertion ---

def insert_recipes(conn, recipes):
    c = conn.cursor()
    inserted = skipped = 0
    for r in recipes:
        c.execute('SELECT id FROM recipes WHERE name = ?', (r['name'],))
        if c.fetchone():
            skipped += 1
            continue
        c.execute(
            '''
            INSERT INTO recipes
                (name, ingredients, macros, tags, last_cooked, rating, casey_approved, notes, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                r['name'],
                json.dumps(r['ingredients']) if r['ingredients'] else None,
                json.dumps(r['macros']) if r['macros'] else None,
                json.dumps(r['tags']) if r['tags'] else None,
                r['last_cooked'],
                r['rating'],
                r['casey_approved'],
                r['notes'],
                r['source_url'],
            ),
        )
        inserted += 1
    conn.commit()
    return inserted, skipped


# --- Preferences + substitutions ---

def parse_prefs_and_subs(path):
    prefs = []
    subs = []
    if not os.path.exists(path):
        return prefs, subs

    with open(path) as f:
        text = f.read()

    sections = re.split(r'^##\s+', text, flags=re.MULTILINE)
    for section in sections[1:]:
        lines = section.strip().splitlines()
        if not lines:
            continue
        header = lines[0].strip().lower()
        body = [ln.strip() for ln in lines[1:] if ln.strip().startswith('-')]

        if header == 'substitutions':
            for ln in body:
                item = ln.lstrip('-').strip()
                if '->' not in item:
                    continue
                orig, rest = item.split('->', 1)
                orig = orig.strip()
                context = None
                sub = rest.strip()
                if '(' in sub and sub.endswith(')'):
                    sub_part, ctx_part = sub.rsplit('(', 1)
                    sub = sub_part.strip()
                    context = ctx_part.rstrip(')').strip() or None
                subs.append((orig, sub, context))
        else:
            m = re.match(r'(love|like|try|avoid)\s*/\s*(me|casey|both)\b', header)
            if not m:
                continue
            category, applies_to = m.group(1), m.group(2)
            for ln in body:
                food = ln.lstrip('-').strip()
                if food and not food.startswith('<!--'):
                    prefs.append((food, category, applies_to))
    return prefs, subs


def insert_prefs(conn, prefs):
    c = conn.cursor()
    inserted = skipped = 0
    for food, cat, applies in prefs:
        c.execute(
            'SELECT id FROM preferences WHERE food_item=? AND category=? AND applies_to=?',
            (food, cat, applies),
        )
        if c.fetchone():
            skipped += 1
            continue
        c.execute(
            'INSERT INTO preferences (food_item, category, applies_to) VALUES (?, ?, ?)',
            (food, cat, applies),
        )
        inserted += 1
    conn.commit()
    return inserted, skipped


def insert_subs(conn, subs):
    c = conn.cursor()
    inserted = skipped = 0
    for orig, sub, ctx in subs:
        c.execute(
            'SELECT id FROM substitutions WHERE original_ingredient=? AND substitute=? AND IFNULL(context, "")=IFNULL(?, "")',
            (orig, sub, ctx),
        )
        if c.fetchone():
            skipped += 1
            continue
        c.execute(
            'INSERT INTO substitutions (original_ingredient, substitute, context) VALUES (?, ?, ?)',
            (orig, sub, ctx),
        )
        inserted += 1
    conn.commit()
    return inserted, skipped


# --- Entry point ---

def main():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Run `python init_db.py` first.")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)

    csv_recipes = parse_recipes_csv(CSV_PATH)
    md_recipes = parse_recipes_md(RECIPES_MD_PATH)
    all_recipes = csv_recipes + md_recipes
    r_in, r_skip = insert_recipes(conn, all_recipes)
    print(f"[recipes] parsed {len(csv_recipes)} from CSV + {len(md_recipes)} from MD → inserted {r_in}, skipped {r_skip} (duplicates)")

    # Warn if any imported recipes have no rating — they won't be eligible for plan_meals
    unrated = sum(1 for r in all_recipes if r.get('rating') is None)
    if unrated:
        print(f"[recipes] {unrated} recipe(s) imported with no rating — add `Rating` and `Casey Approved` columns to the CSV, or run add_recipe.py to rate.")

    prefs, subs = parse_prefs_and_subs(PREFS_PATH)
    p_in, p_skip = insert_prefs(conn, prefs)
    print(f"[preferences] parsed {len(prefs)} → inserted {p_in}, skipped {p_skip}")
    s_in, s_skip = insert_subs(conn, subs)
    print(f"[substitutions] parsed {len(subs)} → inserted {s_in}, skipped {s_skip}")

    conn.close()
    print("\nDone. Next: `python plan_meals.py` (requires rated recipes).")


if __name__ == '__main__':
    main()
