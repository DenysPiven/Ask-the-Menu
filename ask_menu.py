#!/usr/bin/env python3
"""Search a parsed menu JSON and suggest what to eat (optionally with a drink)."""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path
from typing import Any

DRINK_HINTS = (
    "напої",
    "напиток",
    "кава",
    "кофе",
    "coffee",
    "tea",
    "чай",
    "матча",
    "matcha",
    "бар",
    "вино",
    "wine",
    "пиво",
    "beer",
    "коктейл",
    "cocktail",
    "shake",
    "шейк",
    "сік",
    "лимонад",
    "soda",
    "вода",
    "hand brew",
    "прохолодн",
    "milk shake",
    "горівк",
    "віскі",
    "ром",
    "джин",
    "бурбон",
    "ігрист",
)

NOT_FOOD_HINTS = (
    "merch",
    "мерч",
    "equipment",
    "обладнання",
    "beans",
    "зерно",
    "кавові зерн",
    "coffee beans",
)

BREAKFAST_HINTS = ("снідан", "breakfast", "сирник", "омлет", "тост", "гранол", "яйц")
DESSERT_HINTS = (
    "десерт",
    "випічк",
    "baked",
    "кейк",
    "печив",
    "брауні",
    "чізкейк",
    "cookie",
    "тістеч",
)
MEAL_HINTS = (
    "снідан",
    "breakfast",
    "lunch",
    "салат",
    "боул",
    "бургер",
    "паста",
    "піц",
    "pizza",
    "основн",
    "гаряч",
    "суп",
    "перші",
    "сендвіч",
    "тост",
    "омлет",
    "равіолі",
    "bowl",
    "закуск",
    "рол",
    "суші",
)


def load_menu(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "items" not in data:
        raise ValueError(f"{path} не схожий на результат parse_menu.py")
    return data


def norm(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).casefold().strip()


def haystack(item: dict[str, Any]) -> str:
    # Options are toppings/modifiers and cause false hits (every pizza "has" лосось).
    parts = [
        item.get("name"),
        item.get("description"),
        item.get("section"),
        item.get("category"),
        " ".join(item.get("tags") or []),
        " ".join(item.get("allergens") or []),
    ]
    return norm(" ".join(str(p) for p in parts if p))


def blob_for_type(item: dict[str, Any]) -> str:
    return norm(f"{item.get('section')} {item.get('category')} {item.get('name')}")


def is_drink(item: dict[str, Any]) -> bool:
    blob = blob_for_type(item)
    return any(hint in blob for hint in DRINK_HINTS)


def is_not_food(item: dict[str, Any]) -> bool:
    blob = blob_for_type(item)
    return any(hint in blob for hint in NOT_FOOD_HINTS)


def is_food(item: dict[str, Any]) -> bool:
    return not is_drink(item) and not is_not_food(item)


def is_dessert(item: dict[str, Any]) -> bool:
    blob = blob_for_type(item)
    return any(hint in blob for hint in DESSERT_HINTS)


def is_meal(item: dict[str, Any]) -> bool:
    blob = blob_for_type(item)
    return any(hint in blob for hint in MEAL_HINTS)


def matches_section(item: dict[str, Any], section: str | None) -> bool:
    if not section:
        return True
    needle = norm(section)
    return needle in norm(item.get("section")) or needle in norm(item.get("category"))


def within_max(item: dict[str, Any], max_price: float | None) -> bool:
    if max_price is None:
        return True
    price = item.get("price")
    if price is None:
        return False
    return float(price) <= max_price + 1e-9


def score_item(item: dict[str, Any], keywords: list[str]) -> int:
    if not keywords:
        return 1
    text = haystack(item)
    name = norm(item.get("name"))
    score = 0
    for word in keywords:
        if word in name:
            score += 8
        elif word in text:
            score += 3
    if all(word in text for word in keywords):
        score += 5
    return score


def format_item(item: dict[str, Any], currency: str = "₴") -> str:
    def price_s(value: Any) -> str:
        if value is None:
            return ""
        if abs(float(value) - round(float(value))) < 1e-9:
            return f"{int(round(float(value)))} {currency}"
        return f"{float(value):.2f} {currency}".replace(".", ",")

    price = price_s(item.get("price"))
    if item.get("price_max"):
        price = f"{price}–{price_s(item['price_max'])}"
    bits = [b for b in (price, item.get("weight")) if b]
    where = " / ".join(x for x in (item.get("section"), item.get("category")) if x)
    line = item.get("name") or "—"
    if bits:
        line += " — " + ", ".join(bits)
    if where:
        line += f"  [{where}]"
    if not item.get("available", True):
        line += " (немає)"
    if item.get("description"):
        line += f"\n    {item['description']}"
    return line


def pick_drink(drinks: list[dict[str, Any]], food: dict[str, Any] | None) -> dict[str, Any] | None:
    if not drinks:
        return None
    food_blob = blob_for_type(food) if food else ""
    prefer: tuple[str, ...]
    if any(h in food_blob for h in BREAKFAST_HINTS) or not food:
        prefer = ("кава", "coffee", "матча", "чай", "фільтр", "капуч", "лат")
    elif any(h in food_blob for h in ("рол", "суші", "піц", "бургер", "pizza")):
        prefer = ("лимонад", "чай", "пиво", "сік", "вода", "cola")
    else:
        prefer = ("кава", "лимонад", "чай", "матча")
    ranked = []
    for drink in drinks:
        blob = haystack(drink)
        bonus = sum(4 for p in prefer if p in blob)
        ranked.append((bonus, drink))
    ranked.sort(key=lambda pair: (-pair[0], pair[1].get("price") or 10**9))
    top_bonus = ranked[0][0]
    pool = [d for bonus, d in ranked if bonus == top_bonus][:8]
    return random.choice(pool)


def suggest(
    items: list[dict[str, Any]],
    *,
    drinks: list[dict[str, Any]] | None = None,
    with_drink: bool,
    rng_seed: int | None,
) -> list[str]:
    if rng_seed is not None:
        random.seed(rng_seed)
    foods = [i for i in items if is_food(i) and i.get("available", True)]
    drink_pool = [i for i in (drinks or items) if is_drink(i) and i.get("available", True)]
    pool = foods or [i for i in items if i.get("available", True)]
    meals = [i for i in pool if is_meal(i) and not is_dessert(i)]
    if meals:
        pool = meals
    elif any(not is_dessert(i) for i in pool):
        pool = [i for i in pool if not is_dessert(i)]
    if not pool:
        return ["Нічого підходящого не знайдено."]

    def lunch_distance(item: dict[str, Any]) -> float:
        price = float(item.get("price") or 0)
        return abs(price - 280.0)

    pool = sorted(pool, key=lunch_distance)
    shortlist = pool[:12]
    picks = random.sample(shortlist, k=min(3, len(shortlist)))
    lines = ["Можна взяти:"]
    for item in picks:
        lines.append(f"• {format_item(item)}")
        if with_drink:
            drink = pick_drink(drink_pool, item)
            if drink:
                lines.append(f"  напій: {format_item(drink)}")
    if with_drink and not drink_pool:
        lines.append("(немає напоїв у меню)")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Пошук і підказка «що поїсти» з JSON, який зробив parse_menu.py"
    )
    parser.add_argument("menu", help="шлях до data/miro.json (або іншого)")
    parser.add_argument("query", nargs="*", help="ключові слова (лосось, сирники, vegan…)")
    parser.add_argument("--section", help="фільтр за розділом/категорією (підрядок)")
    parser.add_argument("--max", type=float, dest="max_price", help="максимальна ціна, ₴")
    parser.add_argument("--suggest", action="store_true", help="підказати, що взяти")
    parser.add_argument("--drink", action="store_true", help="разом з --suggest підібрати напій")
    parser.add_argument("--seed", type=int, help="фіксоване зерно для --suggest")
    args = parser.parse_args(argv)

    path = Path(args.menu)
    try:
        menu = load_menu(path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    place = menu.get("place") or {}
    currency = place.get("currency") or "₴"
    keywords = [norm(w) for w in args.query if norm(w)]

    filtered: list[dict[str, Any]] = []
    for item in menu.get("items") or []:
        if not matches_section(item, args.section):
            continue
        if not within_max(item, args.max_price):
            continue
        if keywords and score_item(item, keywords) <= 0:
            continue
        filtered.append(item)

    if keywords:
        filtered.sort(key=lambda it: (-score_item(it, keywords), it.get("price") or 0))

    header = place.get("name") or path.stem
    print(header)
    if place.get("address"):
        print(place["address"])
    print()

    if args.suggest:
        drink_src = [
            item
            for item in menu.get("items") or []
            if within_max(item, args.max_price)
        ]
        for line in suggest(
            filtered,
            drinks=drink_src,
            with_drink=args.drink,
            rng_seed=args.seed,
        ):
            print(line)
        print()
        print(f"(з {len(filtered)} позицій після фільтрів)")
        return 0

    if not filtered:
        print("Нічого не знайдено.")
        return 0

    print(f"Знайдено {len(filtered)}:")
    for item in filtered:
        print(f"• {format_item(item, currency)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
