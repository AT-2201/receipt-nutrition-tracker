import json
import os
from thefuzz import fuzz

# Load local nutrition database
DB_PATH = os.path.join("app", "nutrition_db.json")

with open(DB_PATH, "r") as f:
    NUTRITION_DB = json.load(f)


def find_best_match(item_name: str):
    """
    Fuzzy match the parsed item to the closest food name in the database.
    """
    best_match = None
    best_score = 0

    for food in NUTRITION_DB.keys():
        score = fuzz.partial_ratio(item_name.lower(), food.lower())
        if score > best_score:
            best_score = score
            best_match = food

    return best_match if best_score >= 60 else None


def convert_to_grams(quantity, unit):
    unit = unit.lower().replace(" ", "")

    # special-case for gallon → milk weight
    if unit in ["gal"]:
        return quantity * 3785  

    conversion = {
        "lb": 453.6 * quantity,
        "lbs": 453.6 * quantity,
        "oz": 28.35 * quantity,
        "kg": 1000 * quantity,
        "g": quantity,
        "pk": 100 * quantity,
        "ct": 100 * quantity,
        "unit": 100 * quantity,
        "loaf": 500 * quantity
    }

    return conversion.get(unit, 100 * quantity)


def compute_nutrition_for_item(item):
    """
    Given parsed data:
       { item_name, quantity, unit }
    Return: nutrition data using local DB.
    """

    name = item["item_name"]
    quantity = item["quantity"]
    unit = item["unit"]

    grams = convert_to_grams(quantity, unit)

    # Fuzzy match item name to DB
    matched_food = find_best_match(name)
    if not matched_food:
        return None

    per100 = NUTRITION_DB[matched_food]

    calories = (per100["calories"] / 100) * grams
    protein = (per100["protein"] / 100) * grams
    carbs = (per100["carbs"] / 100) * grams
    fat = (per100["fat"] / 100) * grams

    return {
        "item_name": matched_food,
        "quantity_grams": round(grams, 2),
        "calories": round(calories, 2),
        "protein": round(protein, 2),
        "carbs": round(carbs, 2),
        "fat": round(fat, 2)
    }

