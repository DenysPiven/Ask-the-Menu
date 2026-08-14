#!/usr/bin/env python3
"""Parse a restaurant menu from ChoiceQR or Expirenza (expz.menu) into JSON + Markdown."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (compatible; AskTheMenu/1.0; +https://github.com/DenysPiven/Ask-the-Menu)"
)
TIMEOUT = 30
EXPZ_STATIC = "https://static.shaketopay.com.ua/menu/prod/cache/menu/{rid}/{lang}/{file}"
UUID_RE = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)

# ChoiceQR stores EU-style allergen codes (sometimes with a letter suffix).
ALLERGEN_MAP = {
    "1": "глютен",
    "1.1": "пшениця",
    "1.2": "жито",
    "1a": "пшениця",
    "1b": "жито",
    "1c": "ячмінь",
    "1d": "овес",
    "2": "ракоподібні",
    "3": "яйця",
    "4": "риба",
    "5": "арахіс",
    "6": "соя",
    "7": "молоко",
    "8": "горіхи",
    "8.1": "мигдаль",
    "8.3": "волоські горіхи",
    "8a": "мигдаль",
    "8b": "фундук",
    "8c": "волоські горіхи",
    "8d": "кеш'ю",
    "8e": "пекан",
    "8f": "бразильський горіх",
    "8g": "фісташки",
    "8h": "макадамія",
    "9": "селера",
    "10": "гірчиця",
    "11": "кунжут",
    "12": "діоксид сірки",
    "13": "люпин",
    "14": "молюски",
    "15": "мед",
}

CHOICEQR_DAYS = ["Нд", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"]
EXPZ_DAYS = {1: "Пн", 2: "Вт", 3: "Ср", 4: "Чт", 5: "Пт", 6: "Сб", 7: "Нд"}


class ParseError(RuntimeError):
    pass


def session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT, "Accept": "text/html,application/json"})
    return s


def html_text(value: Any) -> str:
    if not value:
        return ""
    text = BeautifulSoup(str(value), "html.parser").get_text(" ", strip=True)
    return re.sub(r"\s+", " ", text).strip()


def format_price(value: float | None, currency: str = "₴") -> str | None:
    if value is None:
        return None
    if abs(value - round(value)) < 1e-9:
        return f"{int(round(value))} {currency}"
    return f"{value:.2f} {currency}".replace(".", ",")


def money_uah(raw: Any, *, kopecks: bool) -> float | None:
    if raw is None or raw == "":
        return None
    try:
        number = float(raw)
    except (TypeError, ValueError):
        return None
    if kopecks:
        number /= 100.0
    return number


def map_allergen(code: Any) -> str:
    key = str(code).strip().lower()
    return ALLERGEN_MAP.get(key, str(code).strip())


def choiceqr_option_prices(group: dict[str, Any]) -> list[tuple[str, float | None]]:
    rows: list[tuple[str, float | None]] = []
    for opt in group.get("list") or []:
        name = html_text(opt.get("name"))
        if not name:
            continue
        rows.append((name, money_uah(opt.get("price"), kopecks=True)))
    return rows


def choiceqr_base_price(raw: dict[str, Any]) -> tuple[float | None, float | None]:
    """Use item price, or the cheapest required option (pizza size, etc.)."""
    base = money_uah(raw.get("price"), kopecks=True)
    required: list[float] = []
    for group in raw.get("menu_options") or []:
        if not group.get("required"):
            continue
        for _, price in choiceqr_option_prices(group):
            if price:
                required.append(price)
    if required and (not base):
        return min(required), max(required) if max(required) != min(required) else None
    return base, None


def choiceqr_options(raw: dict[str, Any]) -> list[str]:
    options: list[str] = []
    for group in raw.get("menu_options") or []:
        rows = choiceqr_option_prices(group)
        if not rows:
            continue
        if not group.get("required") and len(rows) > 8:
            options.append(f"{html_text(group.get('name')).rstrip(' :')} (топінги за доплату)")
            continue
        bits = []
        for name, price in rows:
            if price:
                bits.append(f"{name} ({format_price(price)})")
            else:
                bits.append(name)
        label = html_text(group.get("name")).rstrip(" :")
        options.append(f"{label}: {', '.join(bits)}" if label else ", ".join(bits))
    return options


def choiceqr_weight(raw: dict[str, Any]) -> str | None:
    weight = str(raw.get("weight") or "").strip()
    wtype = str(raw.get("weightType") or "").strip().lower()
    if not weight:
        return None
    if wtype == "mm" and weight.replace(".", "", 1).isdigit():
        cm = float(weight) / 10.0
        return f"{int(cm)} см" if abs(cm - round(cm)) < 1e-9 else f"{cm} см"
    if wtype and not any(ch.isalpha() for ch in weight):
        return f"{weight}{wtype}"
    return weight


def compress_hours(rows: list[tuple[str, str, str]]) -> list[dict[str, str]]:
    """Merge consecutive days that share the same open interval."""
    if not rows:
        return []
    groups: list[dict[str, str]] = []
    start_day, start_from, start_till = rows[0]
    prev_day = start_day
    for day, frm, till in rows[1:]:
        if frm == start_from and till == start_till:
            prev_day = day
            continue
        label = start_day if start_day == prev_day else f"{start_day}–{prev_day}"
        groups.append({"days": label, "from": start_from, "till": start_till})
        start_day, start_from, start_till = day, frm, till
        prev_day = day
    label = start_day if start_day == prev_day else f"{start_day}–{prev_day}"
    groups.append({"days": label, "from": start_from, "till": start_till})
    return groups


def hhmm(value: str | None) -> str:
    if not value:
        return ""
    return str(value).split(".")[0][:5]


# ---------------------------------------------------------------------------
# ChoiceQR
# ---------------------------------------------------------------------------


def is_choiceqr(html: str, url: str) -> bool:
    host = urlparse(url).netloc.lower()
    if "choiceqr.com" in host:
        return True
    return "__NEXT_DATA__" in html and ("choiceqr" in html.lower() or '"menu"' in html)


def load_next_data(html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("script", id="__NEXT_DATA__")
    if tag is None or not tag.string:
        raise ParseError("Сторінка не містить ChoiceQR __NEXT_DATA__")
    return json.loads(tag.string)


def choiceqr_app(html: str) -> dict[str, Any]:
    data = load_next_data(html)
    app = (data.get("props") or {}).get("app")
    if not isinstance(app, dict) or "menu" not in app:
        raise ParseError("Не схоже на меню ChoiceQR")
    return app


def fetch_choiceqr_apps(http: requests.Session, url: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Fetch the landing page, then every digital-menu section."""
    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    landing = http.get(url, timeout=TIMEOUT)
    landing.raise_for_status()
    first = choiceqr_app(landing.text)
    sections = first.get("sections") or []
    apps = [first]
    seen = {((first.get("currentSection") or {}).get("hurl") or "").lower()}
    for section in sections:
        hurl = (section.get("hurl") or "").strip()
        if not hurl or hurl.lower() in seen:
            continue
        seen.add(hurl.lower())
        # hurl looks like "section:menyu" — not a path, so do not use urljoin
        # (urljoin treats "section:" as a URL scheme).
        candidates = [
            f"{origin.rstrip('/')}/{hurl.lstrip('/')}",
            f"{origin.rstrip('/')}/online-menu?section={hurl}",
        ]
        app = None
        for section_url in candidates:
            try:
                response = http.get(section_url, timeout=TIMEOUT)
            except requests.RequestException:
                continue
            if response.status_code != 200:
                continue
            try:
                app = choiceqr_app(response.text)
                break
            except ParseError:
                continue
        if app is None:
            print(f"warning: skip section {hurl}", file=sys.stderr)
            continue
        apps.append(app)
    return first, apps


def parse_choiceqr(http: requests.Session, url: str) -> dict[str, Any]:
    first, apps = fetch_choiceqr_apps(http, url)
    place = first.get("place") or {}
    contact = place.get("contactInfo") or {}
    address = contact.get("address") or {}
    hours_rows: list[tuple[str, str, str]] = []
    for row in place.get("workTimeAll") or []:
        if not row.get("active"):
            continue
        day = CHOICEQR_DAYS[int(row.get("dayOfWeek", 0)) % 7]
        hours_rows.append((day, hhmm(row.get("from")), hhmm(row.get("till"))))

    items: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for app in apps:
        section_name = ""
        current = (app.get("currentSection") or {}).get("hurl")
        for section in app.get("sections") or []:
            if section.get("hurl") == current:
                section_name = section.get("name") or ""
                break
        cats = {c["_id"]: c.get("name") or "" for c in app.get("categories") or [] if c.get("_id")}
        for raw in app.get("menu") or []:
            name = html_text(raw.get("name"))
            if not name:
                continue
            item_id = str(raw.get("_id") or "")
            if item_id and item_id in seen_ids:
                continue
            if item_id:
                seen_ids.add(item_id)
            price, price_max = choiceqr_base_price(raw)
            item: dict[str, Any] = {
                "id": item_id or None,
                "section": section_name,
                "category": cats.get(raw.get("category"), "") or section_name,
                "name": name,
                "description": html_text(raw.get("description")),
                "price": price,
                "weight": choiceqr_weight(raw),
                "available": bool(raw.get("available", True)),
                "allergens": [map_allergen(code) for code in (raw.get("allergens") or [])],
                "tags": [
                    html_text(t.get("name") if isinstance(t, dict) else t)
                    for t in (raw.get("menu_labels") or [])
                ],
                "kcal": raw.get("kcal") or None,
                "options": choiceqr_options(raw),
            }
            if price_max:
                item["price_max"] = price_max
            items.append(item)

    return {
        "source": "choiceqr",
        "url": url,
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "place": {
            "name": place.get("name") or "",
            "type": place.get("type") or "",
            "address": address.get("prediction") or "",
            "city": address.get("city") or "",
            "phone": contact.get("phone") or "",
            "instagram": (contact.get("socialNetworks") or {}).get("instagram") or "",
            "currency": place.get("currencyLabel") or "₴",
        },
        "hours": compress_hours(hours_rows),
        "items": items,
    }


# ---------------------------------------------------------------------------
# Expirenza / expz.menu / ShakeToPay
# ---------------------------------------------------------------------------


def expirenza_restaurant_id(url: str) -> str | None:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if "expz.menu" in host or "shaketopay.com.ua" in host:
        match = UUID_RE.search(parsed.path) or UUID_RE.search(url)
        if match:
            return match.group(0).lower()
    match = UUID_RE.search(parsed.path)
    if match and "expz" in url.lower():
        return match.group(0).lower()
    return None


def parse_expirenza(http: requests.Session, url: str, lang: str) -> dict[str, Any]:
    rid = expirenza_restaurant_id(url)
    if not rid:
        raise ParseError("Не вдалося витягнути restaurantId з URL Expirenza")
    qs = parse_qs(urlparse(url).query)
    menu_id = None
    if qs.get("menuId"):
        try:
            menu_id = int(qs["menuId"][0])
        except ValueError:
            menu_id = None

    info_url = EXPZ_STATIC.format(rid=rid, lang=lang, file="restaurant_menu_info.json")
    menu_url = EXPZ_STATIC.format(rid=rid, lang=lang, file="menu.json")
    info_resp = http.get(info_url, timeout=TIMEOUT)
    menu_resp = http.get(menu_url, timeout=TIMEOUT)
    if info_resp.status_code != 200 or menu_resp.status_code != 200:
        raise ParseError(
            f"Expirenza cache: info {info_resp.status_code}, menu {menu_resp.status_code}"
        )
    info = info_resp.json()
    payload = menu_resp.json()

    cats = {c["id"]: c.get("name") or "" for c in payload.get("categories") or []}
    tag_names = {t["id"]: t.get("name") or "" for t in payload.get("tags") or []}
    allergen_names = {a["id"]: a.get("name") or "" for a in payload.get("allergens") or []}

    hours_rows: list[tuple[str, str, str]] = []
    by_day = {int(r.get("dayOfWeek", 0)): r for r in info.get("settings") or []}
    for dow in range(1, 8):
        row = by_day.get(dow)
        if not row or not row.get("active"):
            continue
        hours_rows.append((EXPZ_DAYS[dow], hhmm(row.get("startTime")), hhmm(row.get("endTime"))))

    items: list[dict[str, Any]] = []
    for raw in payload.get("dishes") or []:
        if menu_id is not None and raw.get("menuId") not in (menu_id, None):
            continue
        if raw.get("active") is False:
            continue
        variants = raw.get("dishVariants") or []
        available = True
        if variants:
            available = any((not v.get("stopList")) and v.get("active", True) for v in variants)
        options = [html_text(v.get("description")) for v in variants if html_text(v.get("description"))]
        items.append(
            {
                "id": raw.get("id"),
                "section": cats.get(raw.get("categoryId"), "") or "Меню",
                "category": cats.get(raw.get("categoryId"), "") or "Меню",
                "name": html_text(raw.get("title") or raw.get("name")),
                "description": html_text(raw.get("description")),
                "price": money_uah(raw.get("minPrice"), kopecks=False),
                "price_max": money_uah(raw.get("maxPrice"), kopecks=False)
                if raw.get("maxPrice") not in (None, raw.get("minPrice"))
                else None,
                "weight": None,
                "available": available,
                "allergens": [
                    allergen_names.get(aid, str(aid))
                    for aid in (raw.get("allergenIds") or raw.get("allergens") or [])
                    if not isinstance(aid, dict)
                ],
                "tags": [tag_names[tid] for tid in (raw.get("tagIds") or []) if tid in tag_names],
                "kcal": None,
                "options": options,
            }
        )

    contacts = info.get("contacts") or []
    phone = ""
    if isinstance(contacts, list) and contacts:
        first_contact = contacts[0] if isinstance(contacts[0], dict) else {}
        phone = str(first_contact.get("phone") or first_contact.get("value") or "")

    return {
        "source": "expirenza",
        "url": url,
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "place": {
            "name": info.get("title") or "",
            "type": "cafe",
            "address": info.get("address") or "",
            "city": "",
            "phone": phone,
            "instagram": "",
            "currency": "₴",
        },
        "hours": compress_hours(hours_rows),
        "items": items,
        "restaurant_id": rid,
        "menu_id": menu_id,
    }


# ---------------------------------------------------------------------------
# Glovo (McDonald's etc.)
# ---------------------------------------------------------------------------

GLOVO_PRODUCT_RE = re.compile(
    r'"description":"(?P<desc>(?:\\.|[^"\\])*)"'
    r',"externalId":"(?P<ext>[^"]+)"'
    r',"id":"(?P<id>[^"]+)"'
    r',"imageId":"[^"]+"'
    r',"imageUrl":"[^"]+"'
    r',"name":"(?P<name>[^"]+)"'
    r',"price":(?P<price>\d+)',
)

DESC_META_RE = re.compile(
    r"(?P<weight>\d+(?:[.,]\d+)?\s*(?:г|мл|шт))\s*\|\s*(?P<kcal>\d+)\s*ккал",
    re.I,
)


def unescape_js_string(value: str) -> str:
    try:
        return json.loads(f'"{value}"')
    except json.JSONDecodeError:
        return value.replace('\\"', '"').replace("\\n", "\n")


def glovo_rsc_text(html: str) -> str:
    chunks: list[str] = []
    for payload in re.findall(r'self\.__next_f\.push\(\[1,"((?:\\.|[^"\\])*)"\]\)', html):
        chunks.append(unescape_js_string(payload))
    return "\n".join(chunks)


def glovo_category(name: str, description: str) -> str:
    blob = f"{name} {description}".casefold()
    if "благодійн" in blob:
        return "Благодійність"
    if "хеппі" in blob or "іграшка" in blob or blob.startswith("книга"):
        return "Хеппі Міл"
    if any(x in blob for x in ("салат",)):
        return "Салати"
    if any(x in blob for x in ("рол",)):
        return "Роли"
    if any(x in blob for x in ("нагетс", "стріпс", "крильц", "чікен бокс")):
        return "Курка"
    if any(x in blob for x in ("фрі", "картопл", "соус", "мед", "вівсян")):
        return "Картопля, каша та соуси"
    if any(
        x in blob
        for x in (
            "флурі",
            "санд",
            "шейк",
            "пиріг",
            "мафін",
            "круасан",
            "попс",
            "морозив",
            "grimace",
        )
    ):
        return "Десерти"
    if any(
        x in blob
        for x in (
            "кола",
            "фанта",
            "спрайт",
            "сік",
            "вода",
            "mcfizz",
            "айс ",
        )
    ):
        return "Холодні напої"
    if any(
        x in blob
        for x in ("американо", "лате", "капуч", "мокко", "чай", "флет", "какао", "еспресо")
    ):
        return "Кава та чай"
    return "Бургери"


def parse_glovo(http: requests.Session, url: str) -> dict[str, Any]:
    response = http.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    text = glovo_rsc_text(response.text)
    if not text:
        raise ParseError("Сторінка Glovo без каталогу (__next_f)")

    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for match in GLOVO_PRODUCT_RE.finditer(text):
        item_id = match.group("id")
        if item_id in seen:
            continue
        seen.add(item_id)
        name = html_text(match.group("name"))
        description = html_text(unescape_js_string(match.group("desc")))
        if "благодійн" in name.casefold() or "благодійн" in description.casefold():
            continue
        category = glovo_category(name, description)
        weight = None
        kcal = None
        meta = DESC_META_RE.search(description)
        if meta:
            weight = re.sub(r"\s+", "", meta.group("weight"))
            kcal = int(meta.group("kcal"))
            description = DESC_META_RE.sub("", description).strip(" .")
        items.append(
            {
                "id": item_id,
                "section": category,
                "category": category,
                "name": name,
                "description": description,
                "price": money_uah(match.group("price"), kopecks=False),
                "weight": weight,
                "available": True,
                "allergens": [],
                "tags": [],
                "kcal": kcal,
                "options": [],
            }
        )
    if not items:
        raise ParseError("У Glovo не знайдено позицій меню")

    parsed = urlparse(url)
    place_name = "McDonald's"
    title = re.search(r"<title>([^<]+)</title>", response.text, re.I)
    if title and "McDonald" in title.group(1):
        place_name = "McDonald's"
    city = ""
    if "vinnyts" in parsed.path.lower() or "-vnt" in parsed.path.lower():
        city = "Vinnytsia"

    return {
        "source": "glovo",
        "url": url,
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "place": {
            "name": place_name,
            "type": "fastfood",
            "address": "Вінниця" if city else "",
            "city": city,
            "phone": "",
            "instagram": "",
            "currency": "₴",
        },
        "hours": [],
        "items": items,
    }


# ---------------------------------------------------------------------------
# Markdown
# ---------------------------------------------------------------------------


def to_markdown(menu: dict[str, Any]) -> str:
    place = menu.get("place") or {}
    currency = place.get("currency") or "₴"
    lines = [f"# {place.get('name') or 'Меню'}", ""]
    meta = [place.get("address"), place.get("phone")]
    extra = [x for x in meta if x]
    if extra:
        lines.append(" · ".join(extra))
        lines.append("")
    if menu.get("hours"):
        hours = ", ".join(f"{h['days']} {h['from']}–{h['till']}" for h in menu["hours"])
        lines.append(f"Години: {hours}")
        lines.append("")
    lines.append(f"Джерело: {menu.get('source')} ({menu.get('url')})")
    lines.append(f"Оновлено: {menu.get('fetched_at')}")
    lines.append(f"Позицій: {len(menu.get('items') or [])}")
    lines.append("")

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for item in menu.get("items") or []:
        key = (item.get("section") or "Меню", item.get("category") or item.get("section") or "Меню")
        grouped.setdefault(key, []).append(item)

    current_section = None
    for (section, category), items in grouped.items():
        if section != current_section:
            lines.append(f"## {section}")
            lines.append("")
            current_section = section
        if category and category != section:
            lines.append(f"### {category}")
            lines.append("")
        for item in items:
            price = format_price(item.get("price"), currency)
            if item.get("price_max"):
                price = f"{price}–{format_price(item['price_max'], currency)}"
            bits = [x for x in (price, item.get("weight")) if x]
            title = item.get("name") or "—"
            suffix = f" — {', '.join(bits)}" if bits else ""
            mark = "" if item.get("available", True) else " *(немає)*"
            lines.append(f"- **{title}**{suffix}{mark}")
            if item.get("description"):
                lines.append(f"  {item['description']}")
            extras = []
            if item.get("allergens"):
                extras.append("алергени: " + ", ".join(item["allergens"]))
            if item.get("tags"):
                extras.append("теги: " + ", ".join(item["tags"]))
            if item.get("options"):
                extras.append("опції: " + "; ".join(item["options"]))
            if extras:
                lines.append("  *" + " · ".join(extras) + "*")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def detect_and_parse(http: requests.Session, url: str, lang: str) -> dict[str, Any]:
    if expirenza_restaurant_id(url) and (
        "expz.menu" in url or "shaketopay.com.ua" in url
    ):
        return parse_expirenza(http, url, lang)
    if "glovoapp.com" in urlparse(url).netloc.lower():
        return parse_glovo(http, url)

    response = http.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    html = response.text
    if is_choiceqr(html, url):
        return parse_choiceqr(http, url)
    if expirenza_restaurant_id(url):
        return parse_expirenza(http, url, lang)
    raise ParseError(
        "Не впізнано джерело. Підтримуються ChoiceQR, Expirenza (expz.menu) "
        "та Glovo (glovoapp.com)."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Парсить меню ChoiceQR, Expirenza або Glovo у data/<name>.json та .md"
    )
    parser.add_argument("url", help="URL цифрового меню")
    parser.add_argument("-n", "--name", required=True, help="ім'я файлів у data/, напр. miro")
    parser.add_argument("-o", "--out-dir", default="data", help="каталог для збереження")
    parser.add_argument("--lang", default="uk", help="мова кешу Expirenza (за замовчуванням uk)")
    args = parser.parse_args(argv)

    stem = re.sub(r"[^a-zA-Z0-9._-]+", "-", args.name).strip("-") or "menu"
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    http = session()
    try:
        menu = detect_and_parse(http, args.url, args.lang)
    except (requests.RequestException, ParseError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    json_path = out_dir / f"{stem}.json"
    md_path = out_dir / f"{stem}.md"
    json_path.write_text(json.dumps(menu, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(to_markdown(menu), encoding="utf-8")
    print(f"Saved {json_path} ({len(menu.get('items') or [])} items)")
    print(f"Saved {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
