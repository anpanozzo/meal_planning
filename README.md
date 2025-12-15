# Overview 
Nothing sends me into a rage like "What's for dinner?" and yet eating is my favorite hobby. (_And I am not alone... [It's so much more than cooking](https://theweek.com/articles/864481/much-more-than-cooking))_

Because meal planning is time-consuming and repetitive how might I create a meal planning workflow that preserves nourishment and joy, but removes the frustration?

# Problem
I need to eat 150g of protein per day for lean body composition and glowing skin. It's time-consuming to find recipes that taste good, match my eating preferances, while delivering the protein and skin-healthy nutrients I need. Right now I only know how to make things that may or may not get me those results. Then if I add another person into the mix it's harder. Adding multiple people's preferences is an omission now.

# Solution
Build a curated recipe collection where each recipe is evaluated and tagged for:
- Protein content (aiming for 150g/day total across 3 meals + 1 snack)
- Skin-healthy ingredients (collagen-supporting, anti-inflammatory, antioxidant-rich)
- Taste and flavor (warm, satisfying, enjoyable)
- Cooking skill match (recipes I know how to make or can learn easily)

Then generate one day meal plans (3 meals + 1 snack) from this trusted collection that I know will deliver results.

______________________

# Files to Create

- [x] **Recipe Database** - Source of truth with recipe data needed to get results
- [x] **Daily Menu Template** - Sharable format for 3 meals + 1 snack

# Recipe Database Structure

## For hitting 150g protein/day:
- Recipe name
- Protein per serving (grams)
- Serving size
- Total calories
- Carbs (g), Fat (g) - optional but helpful

## For glowing skin:
- Skin-healthy: Yes/No
- Skin benefits tags: (collagen-supporting, anti-inflammatory, antioxidant-rich, omega-3, vitamin C, hydrating)
- Key skin ingredients: (specific foods like salmon, berries, leafy greens, etc.)

## For usability:
- Recipe URL
- Meal type: (breakfast, lunch, dinner, snack)
- Cooking time
- Difficulty: (easy, medium, hard)
- Flavor profile: (warm & comforting, light & fresh, etc.)
- GF/DF compatible: Yes/No
- Notes: (any adjustments needed)

---

# Requirements 
- Meal plan summary should be short 
- Meal plan should include a list of the instructions for prep 
- Generate a list of ingrendients to shop. Make it compatible with Apple reminders app
- Create a source of truth file likely CSV or MD that holds foods to make as well as their caloric and macro makeup and URLs
- Allow user to send an email to of the menu recap 
- Menu recap should be only the title of the meal, the URL (if available) amount of protein and if its glowing skin (what do I need to research for glowing skin?)


## INPUTS _(note: adjust later - change based on the user. not for mvp)_

## Food Sensitivities
These are foods that cause GI distress when consumed. It's best to avoid these at all costs. Recipes can have them just call out that adjustments need to be made
- gluten 
- wheat 
- cow's milk 
- eggs

## Foods To Minimize
I will not make these at home but will eat them in small quantities if made properly 
- mushrooms 
- black beans 
- pinto beans
- salmon 
