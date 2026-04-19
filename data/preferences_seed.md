# Preferences Seed

Loaded by `python bulk_import.py`. Duplicates are skipped.

Baseline avoids (`gluten`, `dairy`, `eggs` for `me`) are seeded by `init_db.py`.
Because the avoid filter is a **substring match**, generic category names like
"dairy" don't catch specific ingredients like "butter". The lists below add
the specific ingredient names so recipes actually get filtered correctly.

Sections are `category / applies_to`:
- **category**: `love` | `like` | `try` | `avoid`
- **applies_to**: `me` | `casey` | `both`

---

## avoid / me

Dietary restrictions — expanded to specific ingredient names:

- wheat
- pasta
- bread
- couscous
- bulgur
- seitan
- butter
- cheese
- parmesan
- mozzarella
- cheddar
- feta
- ricotta
- yogurt
- sour cream
- heavy cream
- buttermilk
- cow's milk
- mayonnaise

Minimize (won't make at home; eat in small quantities if served):

- mushrooms
- black beans
- pinto beans
- salmon

## avoid / casey

From Meal Planning.md:

- seafood
- fish
- shrimp
- tuna
- cod
- halibut
- tofu
- mushrooms

## love / me

- roasted vegetables
- olive oil
- avocado

## try / me

- tempeh
- miso

## substitutions

Format: `original -> substitute (optional context)`. Note: `cow's milk` rather than
generic `milk` to avoid false-positives on `coconut milk`.

- butter -> ghee (savory dishes)
- butter -> coconut oil (baking)
- cow's milk -> oat milk
- heavy cream -> coconut cream
- yogurt -> coconut yogurt
- all-purpose flour -> 1:1 gluten-free flour (baking)
- eggs -> flax egg (baking, 1 tbsp ground flax + 3 tbsp water per egg)
- soy sauce -> tamari
- pasta -> gluten-free pasta
