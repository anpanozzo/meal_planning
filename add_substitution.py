"""Interactive CLI to add an ingredient substitution rule."""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'meal_planner.db')


def ask_required(label):
    while True:
        val = input(f"{label}: ").strip()
        if val:
            return val
        print("  Can't be empty.")


def add_substitution():
    print("\n--- Add a substitution ---\n")
    original = ask_required("Original ingredient")
    substitute = ask_required("Substitute")
    context = input("Context (e.g., baking, savory dishes; optional): ").strip() or None

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        'INSERT INTO substitutions (original_ingredient, substitute, context) VALUES (?, ?, ?)',
        (original, substitute, context),
    )
    conn.commit()
    sub_id = c.lastrowid
    conn.close()
    print(f"\nSaved substitution #{sub_id}: {original} -> {substitute}" + (f" ({context})" if context else "") + ".")


if __name__ == '__main__':
    try:
        add_substitution()
    except (KeyboardInterrupt, EOFError):
        print("\nAborted — nothing saved.")
