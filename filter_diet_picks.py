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
    "ostriv": "data/ostriv.json",
    "cherrylake": "data/cherrylake.json",
    "tiflis": "data/tiflis.json",
    "puzatahata": "data/puzatahata.json",
    "musafir": "data/musafir.json",
}

# Extra healthy cues beyond diet.json keywords
SOFT_PREFER = [
    "салат",
    "salad",
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
    "зелень",
    "овоч",
    "брокол",
    "шпинат",
    "огірк",
    "bowl",
    "боул",
    "поке",
    "poke",
    "hummus",
    "хумус",
    "вівсян",
    "куряч",
    "індич",
    "тост",
    "сендвіч",
    "сьомг",
    "кальмар",
    "суп",
    "бульйон",
    "борщ",
    "окрошк",
    "солянка",
    "рис",
    "гречк",
    "стейк",
    "філе",
    "шашлик",
    "гриль",
    "запечен",
    "парова",
    "паров",
    "соте",
    "медальйон",
    "макі",
    "суші",
    "гункан",
    "фунчоз",
    "локшин",
    "каша",
    "пюре",
    "йогурт",
    "моцарел",
    "рукол",
    "млин",
    "налисник",
    "вареник",
    "хінкал",
]

# Clear junk only — diagnosis cautions live in diet.json["caution"]
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
    "темпур",
    "фритюр",
    "хот-дог",
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
    "макфрі",
    "картопля фрі",
    "гамбургер",
    "маккріспі",
    "макнагетс",
    "афогато",
    "аффогато",
    "канеле",
    "печиво",
    "кацу",
    "стріпс",
    "крильц",
    "паніровк",
    "хрумка ззовні",
    "fish-and-chips",
    "fish and chips",
    "шот",
    "кальян",
    "настойк",
    "коньяк",
    "лікер",
    "ром ",
    "вермут",
    "бурбон",
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
    "вина",
    "винн",
    "ігрист",
    "шампан",
    "просекко",
    "prosecco",
    "cava",
    "коравн",
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
    "солянка",
    "крабов",
    "майонез",
    "цезар",
    "caesar",
    "копчен",
    "бекон",
    "салямі",
    "ковбас",
    "карбонар",
    "вершков",
    "bbq",
    "кебаб",
    "гірос",
    "giros",
    "піца",
    "pizza",
    "лазанья",
    "жульєн",
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
    # "Салат-фреш …" is food, not a juice
    if "салат" in name:
        return False
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
            "вина",
            "винн",
            "ігрист",
            "шампан",
            "коравн",
            "просекко",
            "prosecco",
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
            "breakfast",
            "baked",
            "перші",
            "хінкал",
            "мангал",
            "гарнір",
        )
    )
    # "МЕНЮ" / "БАРНЕ МЕНЮ" contain "меню" — don't let that cancel drinks
    if drink_cat and not food_cat:
        return True
    if drink_cat and any(
        x in cat for x in ("бар", "вин", "напої", "напій", "чай", "кава", "coffee", "ігрист", "коравн", "алк")
    ):
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


def caution_item(item: dict, caution_kw: list[str] | None = None) -> bool:
    b = blob_of(item)
    cat = norm(item.get("category"))
    if any(x in cat for x in ("роли", "гункан", "запечен", "сети")):
        return True
    cues = list(CAUTION_CUES)
    if caution_kw:
        cues.extend(caution_kw)
    return any(c in b for c in cues)


def drink_ok(item: dict) -> bool:
    name = norm(item.get("name"))
    cat = norm(item.get("category")) + " " + norm(item.get("section"))
    if any(
        d in name or d in cat
        for d in (
            "вино",
            "вина",
            "винн",
            "ігрист",
            "шампан",
            "просекко",
            "prosecco",
            "cava",
            "коравн",
            "пив",
            "wine",
            "beer",
            "віскі",
            "ром",
            "джин",
            "горілк",
            "коньяк",
            "лікер",
            "апероль",
            "мохіто",
            "коктейл",
            "глинт",
            "кальян",
        )
    ):
        return False
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
    if ("чай" in cat or "tea" in cat) and not any(d in name for d in DRINK_DROP):
        return True
    if "coffee" in cat or cat.strip() == "кава":
        return True
    return False


def classify(
    item: dict,
    prefer_kw: list[str],
    avoid_kw: list[str],
    caution_kw: list[str] | None = None,
) -> str:
    if is_merch(item) or item.get("available") is False:
        return "skip"

    name = norm(item.get("name"))
    caution_kw = caution_kw or []

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
        x in name
        for x in (
            "салат",
            "паста",
            "боул",
            "суп",
            "локшин",
            "фунчоз",
            "рис",
            "картопл",
            "стейк",
            "філе",
            "куряч",
            "риб",
            "лосос",
            "кревет",
            "овоч",
            "омлет",
            "яйц",
            "індич",
            "шашлик",
            "медальйон",
            "соте",
            "тосту",
            "тост ",
            "брускет",
            "хек",
        )
    ):
        return "skip"

    if any(x in name for x in ("big mac", "біг мак", "tacos", "такос")):
        return "avoid"

    # Sweet cheese pancakes — caution, not ban
    if any(x in name for x in ("варенич", "сирник")):
        return "caution"

    if name in ("грінки", "горішки", "начос"):
        return "avoid"

    if is_drink(item):
        return "drink" if drink_ok(item) else "avoid"

    if name == "боул":
        return "caution"
    if "брускет" in name and "асорті" in name:
        return "caution"
    if is_croissant(item):
        return croissant_bucket(item)

    if hard_avoided(item, avoid_kw):
        return "avoid"

    if soft_prefer(item, prefer_kw):
        # Tomato-forward salads — personal dislike
        if "салат" in name and any(
            x in name for x in ("грецьк", "томат", "помідор", "чері", "капрезе", "помідорний")
        ):
            return "avoid"
        if name.startswith("снек") or "снек-" in name:
            return "skip"
        return "caution" if caution_item(item, caution_kw) else "eat"

    # Tomato dislike — still skip tomato-forward salads when not otherwise preferred
    if any(x in name for x in ("томат", "помідор", "чері")):
        return "avoid"

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
            "хінкал",
            "мангал",
            "меню",
        )
    ):
        return "caution" if caution_item(item, caution_kw) else "eat"

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
    caution_kw = [k.lower() for k in (diet.get("caution") or {}).get("keywords") or []]

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Drop stale machine dumps from older runs
    for stale in OUT_DIR.glob("*.json"):
        stale.unlink()

    readme = [
        "# Що брати (за діагнозами)\n\n",
        f"Профіль: `{diet['id']}` — {diet['name']}.\n\n",
        "Без середземноморської дієти від лікаря. Рамка: Жільбер / нирка / СПК / гіпотиреоз + "
        "особисте (без кави, алко, томатів). Голодний > ідеальний.\n\n",
        "У кожному закладі: **їсти** / **з обережністю** / **пити**.\n\n",
        "> Не медична рекомендація.\n",
        "\nПерегенерація: `python3 filter_diet_picks.py`\n",
    ]

    summaries: dict[str, dict] = {}

    for slug, rel in PLACES.items():
        path = ROOT / rel
        data = json.loads(path.read_text(encoding="utf-8"))
        pname = place_name(data)
        addr = place_address(data)
        buckets: dict[str, list] = {"eat": [], "caution": [], "drink": [], "avoid": []}

        for it in data.get("items", []):
            label = classify(it, prefer_kw, avoid_kw, caution_kw)
            if label == "skip":
                continue
            entry = {
                "name": it.get("name"),
                "price": it.get("price"),
                "category": it.get("category") or it.get("section"),
                "description": (it.get("description") or "")[:200] or None,
            }
            entry = {k: v for k, v in entry.items() if v not in (None, "", [])}
            buckets[label].append(entry)

        for k in buckets:
            buckets[k] = dedupe(buckets[k])
            buckets[k].sort(key=lambda e: e["name"].lower())

        counts = {k: len(v) for k, v in buckets.items()}
        summaries[slug] = {"place": pname, "counts": counts}

        lines = [f"# {pname} — за діагнозами\n", f"Джерело: `{rel}`\n"]
        if addr:
            lines.append(f"{addr}\n")
        for title, key in [
            ("Їсти", "eat"),
            ("З обережністю", "caution"),
            ("Пити", "drink"),
        ]:
            lines.append(f"\n## {title}\n")
            items = buckets[key]
            if not items:
                lines.append("_немає явних збігів_\n")
                continue
            for e in items:
                cat = f" _{e['category']}_" if e.get("category") else ""
                lines.append(f"- **{e['name']}**{fmt_price(e.get('price'))}{cat}")
                if e.get("description"):
                    lines.append(f"  - {e['description'][:140]}")

        lines.append(f"\n## Краще не брати\n")
        lines.append(f"_усього відсіяно: {counts['avoid']}_\n")
        for e in buckets["avoid"][:12]:
            lines.append(f"- {e['name']}")
        if counts["avoid"] > 12:
            lines.append(f"- …і ще {counts['avoid'] - 12}")

        (OUT_DIR / f"{slug}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

        readme.append(f"\n## {pname}\n")
        if addr:
            readme.append(f"{addr}\n\n")
        readme.append(f"- [`{slug}.md`]({slug}.md)\n")
        readme.append(
            f"- їсти: **{counts['eat']}**, обережно: **{counts['caution']}**, "
            f"пити: **{counts['drink']}**, уникати: **{counts['avoid']}**\n"
        )
        if buckets["eat"]:
            readme.append("- топ їсти: " + ", ".join(e["name"] for e in buckets["eat"][:10]) + "\n")
        if buckets["caution"]:
            readme.append(
                "- обережно: " + ", ".join(e["name"] for e in buckets["caution"][:8]) + "\n"
            )
        if buckets["drink"]:
            readme.append("- пити: " + ", ".join(e["name"] for e in buckets["drink"][:6]) + "\n")

    (OUT_DIR / "README.md").write_text("".join(readme), encoding="utf-8")

    print(f"Wrote {OUT_DIR}")
    for slug, p in summaries.items():
        c = p["counts"]
        print(
            f"  {slug}: eat={c['eat']} caution={c['caution']} "
            f"drink={c['drink']} avoid={c['avoid']}"
        )


if __name__ == "__main__":
    main()
