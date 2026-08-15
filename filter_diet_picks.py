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

# Extra healthy cues beyond diet.json keywords
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
    "скрембл",
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
    "тост",
    "сендвіч",
    "сьомг",
    "кальмар",
    "гранол",
    "суп",
    "бульйон",
    "борщ",
    "окрошк",
    "рис",
    "гречк",
    "стейк",
    "філе",
    "шашлик",
    "гриль",
    "запечен",
    "соте",
    "медальйон",
    "макі",
    "суші",
    "гункан",
    "фунчоз",
    "локшин",
    "каша",
    "йогурт",
    "моцарел",
    "рукол",
    "шпинат",
]

# Only clear junk / heavy / alcohol — not every imperfect dish
HARD_AVOID = [
    "бургер",
    "burger",
    "big mac",
    "нагетс",
    "наггетс",
    "макфлур",
    "чізбургер",
    "біг тейсті",
    "біг мак",
    "твістер",
    "макчікен",
    "філе-о-фіш",
    "фіш рол",
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
    "вершковий соус",
    "на вершках",
    "вершковому соус",
    "сирний соус",
    "майонез",
    "цезар",
    "caesar",
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
    "long island",
    "long iceland",
    "long beach",
    "кетчуп",
    "чілі кон",
    "chili con",
    "гноккі",
    "ньокі",
    "начос",
    "хешбраун",
    "хеш-браун",
    "макфрі",
    "картопля фрі",
    "гамбургер",
    "маккріспі",
    "макнагетс",
    "афогато",
    "аффогато",
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
    "жульєн",
    "bbq",
    "кебаб",
    "гірос",
    "giros",
    "карамел",
    "сироп",
    "шот",
    "кальян",
    "англійський сніданок",
    "чікен бокс",
    "снек рол",
    "кремі барбекю",
    "цибулев",
    "fish-and-chips",
    "fish and chips",
    "шніцель",
    "кордон блю",
    "настойк",
    "коньяк",
    "лікер",
    "ром ",
    "вермут",
    "бурбон",
    "реберц",
    "кентукі",
    "такос",
    "tacos",
    "сирні кульк",
    "кабанос",
    "бастурм",
]

DRINK_KEEP = [
    "американо",
    "americano",
    "еспресо",
    "espresso",
    "допіо",
    "doppio",
    "рістрет",
    "капучино",
    "капучіно",
    "cappuccino",
    "латте",
    "лате",
    "latte",
    "flat white",
    "флет",
    "лонг блек",
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
    "колдбрю",
    "cold brew",
    "пуровер",
    "v60",
    "ходжича",
    "кава",
    "фреш",
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
    "аффогато",
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
    "bubble",
    "бабл",
    "маршмелоу",
    "мокко",
    "глясе",
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
    "додатки",
    "соус ",
]

# Croissant shop: protein fillings = useful enough when options are scarce
CROISSANT_OK = (
    "лосос",
    "тунец",
    "тунець",
    "кревет",
    "каперс",
    "індич",
    "курка",
    "курк",
    "овоч",
)
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
    "маскарпоне",
    "персик",
    "малин",
    "вишн",
    "фісташ",
    "цезар",
    "гірос",
    "giros",
)

CAUTION_CUES = [
    "теріякі",
    "teriyaki",
    "кисло-солодк",
    "філадельфія",
    "чедер",
    "чеддер",
    "хамон",
    "прошуто",
    "прошутто",
    "шинк",
    "вугор",
    "вугрем",
    "свинин",
    "яловичин",
    "м'ясн",
    "мʼясн",
    "бастурм",
    "кабанос",
    "сирні кульк",
    "горішк",
    "картопля по-селянськ",
    "по-тайськ",
    "азійськ",
    "спайс",
    "гарячий рол",
    "запечений рол",
    "запечені суші",
    "jumbo",
    "сет",
    "плато",
    "асорті",
    "телятин",
    "карпачо",
    "айдахо",
    "пиріжечк",
]


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
    cat = norm(item.get("category"))
    section = norm(item.get("section"))
    name = norm(item.get("name"))
    # Only category/section/name — never description (food often mentions "соус")
    if any(x in cat for x in ("merch", "обладнання", "додатки")):
        return True
    # Pure sauce add-on categories, not "картопля, каша та соуси"
    if cat.strip() in ("соус", "соуси") or cat.startswith("соуси"):
        return True
    if "соус" in cat and not any(x in cat for x in ("каша", "картопл", "страв", "снідан", "гаряч")):
        return True
    if "bean" in cat or "зерн" in cat or "coffee beans" in section:
        return True
    blob = f"{name} {cat} {section}"
    return any(m in blob for m in MERCH_SKIP if m != "соус ")


def is_drink(item: dict) -> bool:
    cat = norm(item.get("category")) + " " + norm(item.get("section"))
    name = norm(item.get("name"))
    # Alcoholic "ice tea" cocktails
    if any(x in name for x in ("long island", "long iceland", "long beach", "ice tea", "айс ті")):
        if "матча" not in name and "matcha" not in name and "кава" not in cat:
            # long island etc. are cocktails
            if any(x in name for x in ("long island", "long iceland", "long beach")):
                return True
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
            "milk shake",
            "crazy shake",
            "горілк",
            "віскі",
            "коньяк",
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
            "перші",
        )
    )
    if drink_cat and not food_cat:
        return True
    return any(
        k in name
        for k in (
            "американо",
            "еспресо",
            "капучино",
            "капучіно",
            "латте",
            "лате",
            "flat white",
            "флет",
            "чай",
            "вода",
            "лимонад",
            "кола",
            "матча",
            "кава",
            "допіо",
            "колдбрю",
            "пуровер",
            "фреш",
            "комбуча",
        )
    )


def is_croissant(item: dict) -> bool:
    return "круасан" in norm(item.get("name")) or "croissant" in norm(item.get("name"))


def croissant_bucket(item: dict) -> str:
    name = norm(item.get("name"))
    if any(b in name for b in CROISSANT_BAD):
        return "avoid"
    if any(o in name for o in CROISSANT_OK):
        return "caution" if "круасан" in name else "eat"
    return "avoid"


def fries_hit(blob: str) -> bool:
    return any(
        x in blob
        for x in (
            "картопля фрі",
            "макфрі",
            "фрі ",
            " фрі",
            "фрі,",
            "фрі.",
            "карт. фрі",
        )
    ) or blob.strip().endswith("фрі")


def avoid_kw_hit(blob: str, avoid_kw: list[str]) -> bool:
    for a in avoid_kw:
        if a not in blob:
            continue
        if a in ("вершков", "вершков соус") and "вершкове масло" in blob and "соус" not in blob:
            continue
        if a == "фрі":
            if fries_hit(blob):
                return True
            continue
        if a == "шоколад" and "шоколадн" not in blob and "з шоколадом" not in blob:
            # plain "какао" etc. handled elsewhere
            if "шоколад" in blob:
                return True
            continue
        return True
    return False


def hard_avoided(item: dict, avoid_kw: list[str]) -> bool:
    b = blob_of(item)
    name = norm(item.get("name"))
    if fries_hit(b):
        return True
    if any(a in b for a in HARD_AVOID):
        return True
    if avoid_kw_hit(b, avoid_kw):
        return True
    if any(x in name for x in ("кацу", "крок", "темпур", "нагет", "флурі")):
        return True
    return False


def soft_prefer(item: dict, prefer_kw: list[str]) -> bool:
    b = blob_of(item)
    return any(p in b for p in prefer_kw + SOFT_PREFER)


def caution_item(item: dict) -> bool:
    b = blob_of(item)
    cat = norm(item.get("category"))
    if any(x in cat for x in ("роли", "гункан", "запечен", "сети")):
        return True
    return any(c in b for c in CAUTION_CUES)


def drink_ok(item: dict) -> bool:
    name = norm(item.get("name"))
    if any(d in name for d in DRINK_DROP):
        return False
    if any(x in name for x in ("long island", "long iceland", "long beach")):
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
                "маршмелоу",
                "сінабон",
                "апельсинов",
                "ананасов",
            )
        ):
            return False
        return True
    if name.startswith("кава") or name.startswith("чай") or name in (
        "зелений",
        "чорний",
        "ройбуш",
        "трав’яний",
        "травяний",
        "фруктовий",
        "обліпиховий крафт",
    ):
        return True
    # category-only teas named by variety
    cat = norm(item.get("category"))
    if ("чай" in cat or "tea" in cat) and not any(d in name for d in DRINK_DROP):
        return True
    if "coffee" in cat or cat.strip() == "кава":
        return True
    return False


def classify(item: dict, prefer_kw: list[str], avoid_kw: list[str]) -> str:
    if is_merch(item) or item.get("available") is False:
        return "skip"

    name = norm(item.get("name"))

    # Condiments / add-ons are not meals
    if name.startswith("соус") or name in (
        "мед",
        "лимон",
        "імбир",
        "м'ята",
        "мʼята",
        "вершки",
        "маршмелоу",
    ):
        return "skip"
    if "соус" in name and not any(
        x in name for x in ("салат", "паста", "боул", "суп", "локшин", "фунчоз", "рис з")
    ):
        return "skip"

    # Explicit junk names even if they look like "food"
    if any(x in name for x in ("big mac", "біг мак", "tacos", "такос")):
        return "avoid"

    # Sweet breakfast dumplings etc.
    if any(x in name for x in ("варенич", "сирник", "млинец", "млинц")):
        return "avoid"

    # Bar snacks that aren't a meal
    if name in ("грінки", "горішки", "начос"):
        return "avoid"

    # Drinks first — don't let food avoid-keywords kill plain tea/coffee
    if is_drink(item):
        return "drink" if drink_ok(item) else "avoid"

    if name == "боул":
        return "caution"
    if "брускет" in name and "асорті" in name:
        return "caution"
    if "салат" in name and "чікен" in name:
        return "caution"
    if is_croissant(item):
        return croissant_bucket(item)

    if hard_avoided(item, avoid_kw):
        return "avoid"

    if soft_prefer(item, prefer_kw):
        return "caution" if caution_item(item) else "eat"

    # Broad healthy baseline: real food categories that aren't junk
    cat = norm(item.get("category")) + " " + norm(item.get("section"))
    if any(
        x in cat
        for x in (
            "снідан",
            "breakfast",
            "салат",
            "суп",
            "перші",
            "гарячі страви",
            "гарячі страви та гарніри",
            "основн",
            "боул",
            "закуск",
            "гарнір",
            "риб",
            "курка",
            "картопля, каша",
        )
    ):
        return "caution" if caution_item(item) else "eat"

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
        "mode": diet.get("mode", "healthy_baseline"),
        "note": (
            "Ширший відбір: середземноморська база + просто корисна їжа в закладах "
            "(супи, гриль, прості суші, курка, яйця). Не медична рекомендація. "
            "caution = норм, але не ідеал (соус, жирніше м’ясо, круасан тощо)."
        ),
        "places": {},
    }

    readme = [
        "# Що брати (корисна база)\n\n",
        f"Профіль: `{diet['id']}` — {diet['name']}.\n\n",
        "Режим ширший: не лише ідеальні боули, а **будь-яка нормальна їжа** без фритюру/солодкого/алко.\n\n",
        "У кожному закладі: **їсти** / **з обережністю** / **пити** / **краще не брати**.\n\n",
        "> Не медична рекомендація. Голодний > ідеальний. При СПК — бульйон, рис, яйце.\n",
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

        lines = [f"# {pname} — корисна база\n", f"Джерело: `{rel}`\n"]
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
            limit = 120 if key != "avoid" else 50
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
            readme.append("- топ їсти: " + ", ".join(e["name"] for e in buckets["eat"][:10]) + "\n")
        if buckets["caution"]:
            readme.append(
                "- обережно: " + ", ".join(e["name"] for e in buckets["caution"][:8]) + "\n"
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
        print("    EAT:", [e["name"] for e in p["eat"][:10]])
        if p["caution"]:
            print("    CAUTION:", [e["name"] for e in p["caution"][:8]])
        print("    DRINK:", [e["name"] for e in p["drink"][:6]])


if __name__ == "__main__":
    main()
