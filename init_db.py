"""Initialize the meal planner SQLite database and seed baseline preferences."""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'meal_planner.db')

SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        ingredients TEXT,
        macros TEXT,
        tags TEXT,
        last_cooked DATE,
        rating INTEGER CHECK (rating BETWEEN 1 AND 5),
        casey_approved BOOLEAN,
        notes TEXT,
        source_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS preferences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        food_item TEXT NOT NULL,
        category TEXT NOT NULL CHECK (category IN ('love', 'like', 'try', 'avoid')),
        applies_to TEXT NOT NULL CHECK (applies_to IN ('me', 'casey', 'both')),
        notes TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS substitutions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_ingredient TEXT NOT NULL,
        substitute TEXT NOT NULL,
        context TEXT
    )
    """,
]

BASELINE_AVOIDS = [
    ('gluten', 'avoid', 'me', 'Dietary restriction'),
    ('dairy', 'avoid', 'me', 'Dietary restriction'),
    ('eggs', 'avoid', 'me', 'Dietary restriction'),
]


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    for ddl in SCHEMA:
        c.execute(ddl)

    for food, cat, applies, note in BASELINE_AVOIDS:
        c.execute(
            'SELECT id FROM preferences WHERE food_item=? AND category=? AND applies_to=?',
            (food, cat, applies),
        )
        if not c.fetchone():
            c.execute(
                'INSERT INTO preferences (food_item, category, applies_to, notes) VALUES (?, ?, ?, ?)',
                (food, cat, applies, note),
            )

    conn.commit()

    print(f"Database initialized at: {DB_PATH}\n")
    print("=" * 60)
    print("SCHEMA")
    print("=" * 60)
    for table in ('recipes', 'preferences', 'substitutions'):
        print(f"\n[{table}]")
        c.execute(f"PRAGMA table_info({table})")
        for cid, name, ctype, notnull, dflt, pk in c.fetchall():
            bits = [f"  {name}", ctype]
            if pk:
                bits.append("PRIMARY KEY")
            if notnull:
                bits.append("NOT NULL")
            if dflt is not None:
                bits.append(f"DEFAULT {dflt}")
            print(' '.join(bits))

    print("\n" + "=" * 60)
    print("SEED PREFERENCES")
    print("=" * 60)
    c.execute('SELECT food_item, category, applies_to, notes FROM preferences ORDER BY id')
    for food, cat, applies, notes in c.fetchall():
        note_str = f"  ({notes})" if notes else ""
        print(f"  {food} -> {cat} / {applies}{note_str}")

    conn.close()
    print("\nReady. Next: `python add_recipe.py` or `python plan_meals.py`.")


if __name__ == '__main__':
    init_db()
