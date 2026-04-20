# Overview 
Nothing sends me into an annoyed state then being asked "What do you want for dinner?" and yet eating is my favorite hobby. (_And I am not alone... [It's so much more than cooking](https://theweek.com/articles/864481/much-more-than-cooking))_

Because meal planning is time-consuming and repetitive how might I create a personal workflow that preserves nourishment and joy, but removes the frustration?

# Problem

Meal planning is cognitively expensive. Every week requires holding multiple constraints in working memory simultaneously:

- Dietary restrictions (gluten-free, dairy-free, egg-free)
- Partner preferences
- Macro/nutrition goals tied to athletic performance
- Variety (not repeating recent meals)
- What's actually been tested and works
- Ingredient substitutions for dietary restrictions

The decision fatigue displaces energy from the parts of cooking that are actually enjoyable: shopping, cooking, and eating.

# Solution

A local, database-backed agent that:

- Maintains a growing library of recipes you've personally cooked and rated
- Captures structured preferences (love / like / willing to try / avoid)
- Knows ingredient substitutions
- Generates a weekly plan for lunches and dinners
- Outputs a consolidated shopping list

The agent only suggests meals from a trusted database (recipes you've actually made) with occasional stretch suggestions from the "willing to try" list.

# Scope

## In Scope (Prototype)

- SQLite database with recipes, preferences, substitutions
- CLI tools to add/update records
- Weekly meal plan generator (5 lunches + 5 dinners, 2 flex days)
- Shopping list generation in markdown
- Gluten-free, dairy-free, egg-free filtering baseline

## Out of Scope (Prototype)

- Breakfast planning
- Snacks
- Calorie/macro auto-calculation (use what's provided)
- Grocery delivery integration
- Mobile UI
- Multi-user accounts
- Recipe scraping from URLs

# Future (v2+)

- Auto-import recipes from URLs
- Macro balancing across the week
- Seasonal ingredient awareness
- Cost estimation
- Pantry inventory tracking
- Voice interface
- Web or mobile UI
- Integration with grocery delivery services

# Success Criteria

Prototype is successful if:

- Weekly meal planning takes under 5 minutes instead of 30+
- Shopping list is generated automatically and usable as-is
- No meal suggestions violate dietary restrictions
- Recipes cooked in the last 14 days are not repeated
- The database grows organically as new recipes are cooked

# User

Single user (me) plus awareness of partner preferences. Designed for local use on my machine.

# Tech Stack

- **Language:** Python 3 (standard library only for prototype)
- **Database:** SQLite
- **Interface:** CLI scripts
- **Orchestration:** Claude Code
- **Knowledge base:** Obsidian vault (optional, for recipe notes)

# Repo Structure

```
meal-planner/
├── README.md
├── PRD.md
├── EXECUTION_PLAN.md
├── meal_planner.db
├── init_db.py
├── add_recipe.py
├── add_preference.py
├── add_substitution.py
├── bulk_import.py
├── plan_meals.py
├── weekly_plan.md          # generated output
└── data/
    ├── recipes_seed.md     # for bulk import
    └── preferences_seed.md
```

# Workflow

1. **After cooking a new recipe:** Run `python add_recipe.py` to log it.
2. **Weekly (Sunday):** Run `python plan_meals.py` to generate the week's plan.
3. **Review:** Open `weekly_plan.md`, adjust if needed, take the shopping list to the store.
4. **As preferences evolve:** Edit `data/preferences_seed.md` and run `python bulk_import.py` (or use `python add_preference.py` / `python add_substitution.py` for quick DB-only adds). See [PREFERENCES.md](PREFERENCES.md) for the full guide.

# Principles

- **Trust the database.** The agent never invents recipes; it only pulls from what's been cooked or explicitly added.
- **Lightweight over comprehensive.** Schema evolves as needs emerge; don't over-engineer upfront.
- **Local-first.** No cloud dependencies. Everything runs on-device.
- **Claude Code is a collaborator, not a dependency.** Scripts should work standalone once generated.
