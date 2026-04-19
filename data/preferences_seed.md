# Preferences Seed

Use this file to bulk-import preferences and substitutions via `python bulk_import.py`.

Sections are `##`-headed with the form `category / applies_to`:
- **category**: `love` | `like` | `try` | `avoid`
- **applies_to**: `me` | `casey` | `both`

The baseline avoids (gluten, dairy, eggs) for `me` are already seeded by `init_db.py` —
no need to re-list them here. Add everything else below.

Duplicates are skipped on import, so it's safe to re-run.

---

## love / me
- salmon
- roasted vegetables
- olive oil
- avocado

## love / casey
<!-- fill in Casey's loves -->

## avoid / casey
<!-- fill in Casey's dislikes, e.g. mushrooms, cilantro -->

## avoid / both
<!-- foods neither of you will eat -->

## try / me
- tempeh
- miso
- sardines

## substitutions

Format: `original ingredient -> substitute (optional context)`

- butter -> ghee (savory dishes)
- butter -> coconut oil (baking)
- milk -> oat milk
- all-purpose flour -> 1:1 gluten-free flour (baking)
- eggs -> flax egg (baking, 1 tbsp ground flax + 3 tbsp water per egg)
- soy sauce -> tamari
- pasta -> gluten-free pasta
