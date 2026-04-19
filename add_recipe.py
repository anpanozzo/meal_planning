"""Interactive CLI to add a recipe. All fields except name are optional."""
import sqlite3
import json
import os
from datetime import date

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'meal_planner.db')


def ask(label, optional=True, default=None):
    suffix = "" if not optional else "  [Enter to skip]"
    val = input(f"{label}{suffix}: ").strip()
    return val if val else default


def ask_required(label):
    while True:
        val = input(f"{label} (required): ").strip()
        if val:
            return val
        print("  This field can't be empty.")


def ask_int(label, min_val=None, max_val=None):
    while True:
        raw = ask(label)
        if raw is None:
            return None
        try:
            n = int(raw)
        except ValueError:
            print("  Not a valid integer — try again or press Enter to skip.")
            continue
        if min_val is not None and n < min_val:
            print(f"  Must be >= {min_val}.")
            continue
        if max_val is not None and n > max_val:
            print(f"  Must be <= {max_val}.")
            continue
        return n


def ask_float(label):
    while True:
        raw = ask(label)
        if raw is None:
            return None
        try:
            return float(raw)
        except ValueError:
            print("  Not a valid number — try again or press Enter to skip.")


def ask_yn(label):
    raw = ask(label + " (y/n)")
    if raw is None:
        return None
    return raw.strip().lower().startswith('y')


def ask_list(label):
    raw = ask(label + "  [comma-separated]")
    if not raw:
        return []
    return [x.strip() for x in raw.split(',') if x.strip()]


def ask_date(label):
    raw = ask(label + "  [YYYY-MM-DD or 'today']")
    if not raw:
        return None
    if raw.lower() == 'today':
        return date.today().isoformat()
    try:
        date.fromisoformat(raw)
        return raw
    except ValueError:
        print(f"  Couldn't parse '{raw}' as a date. Leaving blank.")
        return None


def add_recipe():
    print("\n--- Add a recipe ---\n")
    name = ask_required("Recipe name")
    ingredients = ask_list("Ingredients")

    print("\nMacros per serving:")
    macros = {}
    for key, label in (
        ('protein_g', '  Protein (g)'),
        ('carbs_g', '  Carbs (g)'),
        ('fat_g', '  Fat (g)'),
        ('calories', '  Calories'),
    ):
        v = ask_float(label)
        if v is not None:
            macros[key] = v

    print("\nTags:")
    tags = {}
    cuisine = ask("  Cuisine (e.g., mediterranean, thai)")
    if cuisine:
        tags['cuisine'] = cuisine
    protein_type = ask("  Protein type (e.g., chicken, tofu, lentils)")
    if protein_type:
        tags['protein_type'] = protein_type
    cook_time = ask_int("  Cook time (minutes)")
    if cook_time is not None:
        tags['cook_time_minutes'] = cook_time
    meal_type = ask("  Meal type (lunch / dinner / both / breakfast)")
    if meal_type:
        tags['meal_type'] = meal_type.lower()

    print()
    last_cooked = ask_date("Last cooked")
    rating = ask_int("Rating (1-5)", min_val=1, max_val=5)
    casey_approved = ask_yn("Casey approved?")
    notes = ask("Notes")
    source_url = ask("Source URL")

    casey_val = 1 if casey_approved is True else (0 if casey_approved is False else None)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        '''
        INSERT INTO recipes
            (name, ingredients, macros, tags, last_cooked, rating, casey_approved, notes, source_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            name,
            json.dumps(ingredients) if ingredients else None,
            json.dumps(macros) if macros else None,
            json.dumps(tags) if tags else None,
            last_cooked,
            rating,
            casey_val,
            notes,
            source_url,
        ),
    )
    conn.commit()
    recipe_id = c.lastrowid
    conn.close()
    print(f"\nSaved '{name}' as recipe #{recipe_id}.")


if __name__ == '__main__':
    try:
        add_recipe()
    except (KeyboardInterrupt, EOFError):
        print("\nAborted — nothing saved.")
