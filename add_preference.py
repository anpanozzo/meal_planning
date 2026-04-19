"""Interactive CLI to add a food preference."""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'meal_planner.db')

CATEGORIES = ('love', 'like', 'try', 'avoid')
APPLIES_TO = ('me', 'casey', 'both')


def ask_required(label):
    while True:
        val = input(f"{label}: ").strip()
        if val:
            return val
        print("  Can't be empty.")


def ask_choice(label, choices):
    prompt = f"{label} ({'/'.join(choices)}): "
    while True:
        raw = input(prompt).strip().lower()
        if raw in choices:
            return raw
        print(f"  Must be one of: {', '.join(choices)}")


def add_preference():
    print("\n--- Add a preference ---\n")
    food_item = ask_required("Food item")
    category = ask_choice("Category", CATEGORIES)
    applies_to = ask_choice("Applies to", APPLIES_TO)
    notes = input("Notes (optional, Enter to skip): ").strip() or None

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        'INSERT INTO preferences (food_item, category, applies_to, notes) VALUES (?, ?, ?, ?)',
        (food_item, category, applies_to, notes),
    )
    conn.commit()
    pref_id = c.lastrowid
    conn.close()
    print(f"\nSaved preference #{pref_id}: {food_item} -> {category} / {applies_to}.")


if __name__ == '__main__':
    try:
        add_preference()
    except (KeyboardInterrupt, EOFError):
        print("\nAborted — nothing saved.")
