#!/usr/bin/env python3
"""Filter saved venue menus through data/diet.json into data/diet_picks/."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIET_PATH = ROOT / "data" / "diet.json"
OUT_DIR = ROOT / "data" / "diet_picks"

PLACES = {
    "miro": "data/miro.json",
    "longshot": "data/longshot.json",
    "mcdonalds": "data/mcdonalds.json",
    "woods": "data/woods.json",
    "lvivcroissants": "data/lvivcroissants.json",
}

SOFT_PREFER = [
    "салат",
    "salad",
    "томат",
    "авокадо",
    "лосос",
    "тунец",
    "тунець",
    "риб",
    "кревет",
    "омлет",
    "яйц",
    "тофу",
    "нут",
    "фасол",
    "квасол",
    "зелень",
    "овоч",
    "брокол",
    "шпинат",
    "огірк",
    "оливк",
    "bowl",
    "боул",
    "поке",
    "poke",
    "грецьк",
    "greek",
    "hummus",
    "хумус",
    "табуле",
    "кіноа",
    "вівсян",
    "капрезе",
    "брускет",
    "гаспачо",
    "куряч",
    "індич",
    "фітнес",
    "тост з",
    "сьомг",
    "сємга",
    "кальмар",
    "гранол",
]

HARD_AVOID = [
    "бургер",
    "burger",
    "фрі",
    "нагетс",
    "наггетс",
    "макфлур",
    "чізбургер",
    "біг тейсті",
    "біг мак",
    "твістер",
    "макчікен",
    "філе-о-фіш",
    "темпур",
    "фритюр",
    "ковбас",
    "сосиск",
    "бекон",
    "bacon",
    "сало",
    "хот-дог",
    "піца",
    "pizza",
    "лазанья",
    "карбонар",
    "вершки",
    "вершковий соус",
    "на вершках",
    "сирний соус",
    "чедер",
    "чеддер",
    "майонез",
    "цезар",
    "caesar",
    "теріякі",
    "teriyaki",
    "вафл",
    "панкейк",
    "пончик",
    "тірам",
    "чизкейк",
    "чізкейк",
    "брауні",
    "шоколадн",
    "морозиво",
    "мілкшейк",
    "shake",
    "шейк",
    "паста ",
    "паста з",
    "паста по",
    "локшин",
    "торт",
    "десерт",
    "глинтвейн",
    "глінтвейн",
    "кола",
    "sprite",
    "fanta",
    "лимонад",
    "енергетик",
    "energy",
    "пив",
    "вино",
    "wine",
    "beer",
    "віскі",
    "текіл",
    "джин",
    "горілк",
    "коктейл",
    "мохіто",
    "апероль",
    "aperol",
    "кетчуп",
    "чілі кон",
    "chili con",
    "гноккі",
    "ньокі",
    "рамен",
    "вок ",
    "том ям",
    "сирники",
    "оладк",
    "млинц",
    "начос",
    "хешбраун",
    "макфрі",
    "картопля фрі",
    "гамбургер",
    "маккріспі",
    "макнагетс",
    "прошуто",
    "прошутто",
    "шинк",
    "салямі",
    "афогато",
    "канеле",
    "печиво",
    "банановий хліб",
    "крок-месьє",
    "крок месьє",
    "кацу",
    "стріпс",
    "крильц",
    "паніровк",
    "хрумка ззовні",
    "ролл",
    "роли",
    "суші",
    "макі",
    "гункан",
    "жульєн",
    "свинин",
    "паштет",
    "сирне плато",
    "bbq",
    "кебаб",
    "гірос",
    "карамел",
    "сироп",
    "шот",
    "кальян",
    "англійський сніданок",
    "чікен бокс",
    "снек рол",
    "кремі барбекю",
    "вугор",
    "вугрем",
    "філадельфія",
    "jumbo roll",
    "асорті м'ясне",
    "асорті мʼясне",
    "сет лонг",
    "кисло-солодк",
    "хамон",
]

DRINK_KEEP = [
    "американо",
    "americano",
    "еспресо",
    "espresso",
    "doppio",
    "рістрет",
    "капучино",
    "cappuccino",
    "латте",
    "latte",
    "flat white",
    "флет",
    "чай",
    "tea",
    "матча",
    "matcha",
    "вода",
    "water",
    "мінеральн",
    "фільтр",
    "filter",
    "batch brew",
    "аеропрес",
    "кемекс",
    "колд брю",
    "cold brew",
    "кава",
]

DRINK_DROP = [
    "лимонад",
    "кола",
    "sprite",
    "fanta",
    "shake",
    "шейк",
    "мілкшейк",
    "коктейл",
    "пив",
    "вино",
    "wine",
    "beer",
    "віскі",
    "ром",
    "джин",
    "горілк",
    "мохіто",
    "апероль",
    "глинт",
    "енергетик",
    "energy",
    "сироп",
    "раф",
    "фрапе",
    "frappe",
    "афогато",
    "карамел",
    "ваніл",
    "вишнев",
    "choco",
    "тонік",
    "tonic",
    "фрут баскет",
    "шот",
    "shot",
    "cloud",
    "комбуча",
    "cascara",
    "сет ",
    "полунич",
    "оранж",
    "orange",
    "фрукт",
]

MERCH_SKIP = [
    "merch",
    "мерч",
    "equipment",
    "обладнання",
    "кавові зерн",
    "coffee beans",
    "фільтр папір",
    "млинок",
    "grinder",
    "термос",
    "чашк",
]

# Bakery: croissants are off-diet, but fish ones are least-bad
CROISSANT_OK = ("лосос", "тунец", "тунець", "кревет", "каперс")
CROISSANT_BAD = (
    "bbq",
    "кебаб",
    "теріякі",
    "чизбургер",
    "бургер",
    "pork",
    "шоколад",
    "солодк",
    "карамел",
    "крем-сир",
    "королівськ",
    "філадельфія",
)


def norm(s: str | None) -> str:
    return (s or "").lower()


def place_name(data: dict) -> str:
    p = data.get("place")
    if isinstance(p, dict):
        return p.get("name") or "Unknown"
    return p or data.get("name") or "Unknown"


def place_address(data: dict) -> str:
    p = data.get("place")
    if isinstance(p, dict):
        return p.get("address") or ""
    return ""


def blob_of(item: dict) -> str:
    return " ".join(norm(item.get(k)) for k in ("name", "description", "category", "section"))


def is_merch(item: dict) -> bool:
    b = blob_of(item)
    cat = norm(item.get("category"))
    if "merch" in cat or "bean" in cat or "обладнання" in cat or "зерн" in cat:
        return True
    return any(m in b for m in MERCH_SKIP)


def is_drink(item: dict) -> bool:
    cat = norm(item.get("category")) + " " + norm(item.get("section"))
    drink_cat = any(
        x in cat
        for x in (
            "напої",
            "напій",
            "drink",
            "coffee",
            "кава",
            "чай",
            "tea",
            "бар",
            "коктейл",
            "пиво",
            "вино",
            "hand brew",
            "холодні напої",
            "безалкогольн",
            "б/а",
            "алк",
            "шот",
        )
    )
    food_cat = any(
        x in cat
        for x in (
            "страви",
            "снідан",
            "салат",
            "суп",
            "десерт",
            "піца",
            "паста",
            "бургер",
            "гарячі",
            "закуск",
            "рол",
            "меню",
            "breakfast",
            "baked",
        )
    )
    if drink_cat and not food_cat:
        return True
    name = norm(item.get("name"))
    return any(
        k in name
        for k in (
            "американо",
            "еспресо",
            "капучино",
            "латте",
            "flat white",
            "чай",
            "вода",
            "лимонад",
            "кола",
            "матча",
            "кава",
        )
    )


def is_croissant(item: dict) -> bool:
    return "круасан" in norm(item.get("name")) or "croissant" in norm(item.get("name"))


def croissant_bucket(item: dict) -> str:
    name = norm(item.get("name"))
    if any(b in name for b in CROISSANT_BAD):
        return "avoid"
    if any(o in name for o in CROISSANT_OK):
        return "caution"
    return "avoid"


def avoid_kw_hit(blob: str, avoid_kw: list[str]) -> bool:
    """Match diet avoid keywords with a few false-positive guards."""
    for a in avoid_kw:
        if a not in blob:
            continue
        # "вершкове масло" on avocado toast ≠ cream sauce
        if a == "вершков" and "вершкове масло" in blob and "вершки" not in blob and "вершковий" not in blob:
            continue
        # "фрі" alone should not fire on unrelated words; HARD_AVOID covers fries
        if a == "фрі" and not any(x in blob for x in ("фрі ", " фрі", "картопля фрі", "макфрі", "карт. фрі")):
            if "фрі" == blob.strip() or blob.endswith("фрі") or "фрі," in blob:
                return True
            continue
        return True
    return False


def hard_avoided(item: dict, avoid_kw: list[str]) -> bool:
    b = blob_of(item)
    name = norm(item.get("name"))
    # Always honor hard / diet avoid keywords (no force-keep override)
    if any(a in b for a in HARD_AVOID):
        return True
    if avoid_kw_hit(b, avoid_kw):
        return True
    # fried / cream cues in name
    if any(x in name for x in ("кацу", "крок", "фрі", "темпур", "нагет")):
        return True
    return False


def soft_prefer(item: dict, prefer_kw: list[str]) -> bool:
    b = blob_of(item)
    return any(p in b for p in prefer_kw + SOFT_PREFER)


def drink_ok(item: dict) -> bool:
    name = norm(item.get("name"))
    if any(d in name for d in DRINK_DROP):
        return False
    if any(k in name for k in DRINK_KEEP):
        if any(
            x in name
            for x in (
                "карамел",
                "ваніл",
                "вишнев",
                "солона",
                "крем",
                "сироп",
                "choco",
                "полунич",
                "оранж",
            )
        ):
            return False
        return True
    # generic "Кава (в асортименті)" / "Чай (в асортименті)"
    if name.startswith("кава") or name.startswith("чай"):
        return True
    return False


def classify(item: dict, prefer_kw: list[str], avoid_kw: list[str]) -> str:
    if is_merch(item) or item.get("available") is False:
        return "skip"
    name = norm(item.get("name"))
    # Woods-style "Боул" with mixed options — pick salmon/shrimp, skip eel
    if name == "боул":
        return "caution"
    # Mixed bruschetta boards often include ham — OK only as a share / pick salmon ones
    if "брускет" in name and "асорті" in name:
        return "caution"
    # McD fried-chicken salad: better than a burger, still not ideal
    if "салат" in name and "чікен" in name:
        return "caution"
    if is_croissant(item):
        return croissant_bucket(item)
    if hard_avoided(item, avoid_kw):
        return "avoid"
    if is_drink(item):
        return "drink" if drink_ok(item) else "avoid"
    if soft_prefer(item, prefer_kw):
        return "eat"
    return "skip"


def fmt_price(price) -> str:
    if isinstance(price, (int, float)):
        return f" — {price:g} ₴"
    if price is not None:
        return f" — {price} ₴"
    return ""


def dedupe(items: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for e in items:
        key = e["name"].strip().lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(e)
    return out


def main() -> None:
    diet = json.loads(DIET_PATH.read_text(encoding="utf-8"))
    prefer_kw = [k.lower() for k in diet["prefer"]["keywords"]]
    avoid_kw = [k.lower() for k in diet["avoid"]["keywords"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    all_out = {
        "diet_id": diet["id"],
        "diet_name": diet["name"],
        "source_profile": "data/diet.json",
        "note": (
            "Автоматичний відбір під адаптоване середземноморське харчування "
            "(Жільбер, нирка, щитоподібна, СРК). Не медична рекомендація. "
            "caution = найменш погане в закладі, де майже все поза дієтою."
        ),
        "places": {},
    }

    readme = [
        "# Що брати за дієтою\n\n",
        f"Профіль: `{diet['id']}` — {diet['name']}.\n\n",
        "У кожному закладі: **їсти** / **з обережністю** / **пити** / **краще не брати**.\n\n",
        "> Не медична рекомендація. При загостренні СРК — омлет, рис, курятина без соусів.\n",
        "\nПерегенерація: `python3 filter_diet_picks.py`\n",
    ]

    for slug, rel in PLACES.items():
        path = ROOT / rel
        data = json.loads(path.read_text(encoding="utf-8"))
        pname = place_name(data)
        addr = place_address(data)
        buckets: dict[str, list] = {"eat": [], "caution": [], "drink": [], "avoid": []}

        for it in data.get("items", []):
            label = classify(it, prefer_kw, avoid_kw)
            if label == "skip":
                continue
            entry = {
                "name": it.get("name"),
                "price": it.get("price"),
                "category": it.get("category") or it.get("section"),
                "description": (it.get("description") or "")[:240] or None,
                "weight": it.get("weight"),
            }
            entry = {k: v for k, v in entry.items() if v not in (None, "", [])}
            buckets[label].append(entry)

        for k in buckets:
            buckets[k] = dedupe(buckets[k])
            buckets[k].sort(key=lambda e: e["name"].lower())

        place_out = {
            "place": pname,
            "address": addr,
            "source": rel,
            "counts": {k: len(v) for k, v in buckets.items()},
            **buckets,
        }
        all_out["places"][slug] = place_out
        (OUT_DIR / f"{slug}.json").write_text(
            json.dumps(place_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

        lines = [f"# {pname} — під дієту\n", f"Джерело: `{rel}`\n"]
        if addr:
            lines.append(f"{addr}\n")
        for title, key in [
            ("Їсти", "eat"),
            ("З обережністю", "caution"),
            ("Пити", "drink"),
            ("Краще не брати", "avoid"),
        ]:
            lines.append(f"\n## {title}\n")
            items = buckets[key]
            if not items:
                lines.append("_немає явних збігів_\n")
                continue
            limit = 100 if key != "avoid" else 50
            for e in items[:limit]:
                cat = f" _{e['category']}_" if e.get("category") else ""
                lines.append(f"- **{e['name']}**{fmt_price(e.get('price'))}{cat}")
                if e.get("description") and key != "avoid":
                    lines.append(f"  - {e['description'][:160]}")
            if len(items) > limit:
                lines.append(f"\n_…ще {len(items) - limit} у `{slug}.json`_\n")
        (OUT_DIR / f"{slug}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

        readme.append(f"\n## {pname}\n")
        if addr:
            readme.append(f"{addr}\n\n")
        readme.append(f"- [`{slug}.md`]({slug}.md) / [`{slug}.json`]({slug}.json)\n")
        c = place_out["counts"]
        readme.append(
            f"- їсти: **{c['eat']}**, обережно: **{c['caution']}**, "
            f"пити: **{c['drink']}**, уникати: **{c['avoid']}**\n"
        )
        if buckets["eat"]:
            readme.append("- топ їсти: " + ", ".join(e["name"] for e in buckets["eat"][:8]) + "\n")
        if buckets["caution"]:
            readme.append(
                "- обережно: " + ", ".join(e["name"] for e in buckets["caution"][:6]) + "\n"
            )
        if buckets["drink"]:
            readme.append("- пити: " + ", ".join(e["name"] for e in buckets["drink"][:6]) + "\n")

    (OUT_DIR / "all.json").write_text(
        json.dumps(all_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (OUT_DIR / "README.md").write_text("".join(readme), encoding="utf-8")

    print(f"Wrote {OUT_DIR}")
    for slug, p in all_out["places"].items():
        c = p["counts"]
        print(
            f"  {slug}: eat={c['eat']} caution={c['caution']} "
            f"drink={c['drink']} avoid={c['avoid']}"
        )
        print("    EAT:", [e["name"] for e in p["eat"][:8]])
        if p["caution"]:
            print("    CAUTION:", [e["name"] for e in p["caution"][:6]])
        print("    DRINK:", [e["name"] for e in p["drink"][:6]])


if __name__ == "__main__":
    main()
