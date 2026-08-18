# Ask the Menu

Парсер цифрових меню і підказка «що поїсти». Меню закладів — з публічних сторінок ChoiceQR, Expirenza, Glovo і Duck Hub. Сільпо — окремо, через офіційний MCP (магазин, не заклад).

## Що вміє

- `parse_menu.py` — забирає меню, кладе `data/<name>.json` і читабельний `data/<name>.md`
- `ask_menu.py` — пошук за ключовими словами, фільтр розділу/ціни, підбір страви й напою

Джерела:

| Платформа | Приклад |
|---|---|
| **ChoiceQR** | [MIRO CAFE](https://miro.vn.ua/section:snidanki) (`miro.vn.ua`, `*.choiceqr.com`) |
| **Expirenza** (`expz.menu`) | [LongShot](https://expz.menu/order/921775e1-69a8-496d-8739-0293dd0cdcf5/menu?menuId=20141&tableCode=QZ2EJ) — JSON з `static.shaketopay.com.ua/menu/prod/cache/menu/<restaurantId>/uk/` |
| **Glovo** | [McDonald's Вінниця](https://glovoapp.com/uk/ua/vinnytsia/stores/mcdonald-s-vnt) |
| **Duck Hub** | [Woods Вінниця](https://woods.duck-hub.com/menu) |

У репозиторії вже є зліпки:

| Файл | Що це |
|---|---|
| `data/<place>.json` + `.md` | повне меню закладу |
| `data/diet.json` + `.md` | профіль дієти (дім / заклади / заборони) |
| [`data/diet_picks/`](data/diet_picks/README.md) | що брати в кожному закладі |
| `.cursor/mcp.json` | MCP **Сільпо** (`https://mcp.silpo.ua/mcp`) |

Перегенерація відбору: `python3 filter_diet_picks.py`

## Сільпо (MCP)

Це продуктові, не цифрове меню кафе. У Cursor (десктоп) сервер уже прописаний у `.cursor/mcp.json`. Після OAuth на `auth.silpo.ua` агент бачить tools на кшталт `silpo_find_products_batch` і `silpo_add_or_update_cart_products`.

**Cloud Agent** цей файл не підхоплює. Додай той самий URL у [cursor.com/agents](https://cursor.com/agents) → MCP:

```json
{
  "name": "silpo",
  "type": "http",
  "url": "https://mcp.silpo.ua/mcp"
}
```

Документація: [ai-factory.silpo.ua/docs/mcp](https://ai-factory.silpo.ua/docs/mcp).

## Встановлення

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Парсинг

```bash
python parse_menu.py https://miro.vn.ua/section:snidanki -n miro

python parse_menu.py \
  "https://expz.menu/order/921775e1-69a8-496d-8739-0293dd0cdcf5/menu?menuId=20141&tableCode=QZ2EJ" \
  -n longshot

python parse_menu.py \
  "https://glovoapp.com/uk/ua/vinnytsia/stores/mcdonald-s-vnt" \
  -n mcdonalds

python parse_menu.py https://woods.duck-hub.com/menu -n woods

python parse_menu.py \
  "https://glovoapp.com/uk/ua/vinnytsia/stores/lvivcroissants-vnt" \
  -n lvivcroissants
```

Для ChoiceQR скрипт проходить усі розділи закладу (сніданки, меню, напої, бар…), не лише той, що в URL.

Expirenza: `menu.json` + `restaurant_menu_info.json` з кешу ShakeToPay. `restaurantId` — UUID з `/order/<id>/`. `menuId` з query відсікає зайві картки, якщо їх кілька.

## Що поїсти

```bash
# пошук
python ask_menu.py data/miro.json лосось
python ask_menu.py data/longshot.json сирники --max 300

# лише розділ
python ask_menu.py data/miro.json --section сніданки
python ask_menu.py data/longshot.json --section coffee --max 150

# підказка + напій
python ask_menu.py data/longshot.json --suggest --drink
python ask_menu.py data/miro.json боул --suggest --drink --max 450
```

`--section` шукає підрядок у назві розділу або категорії. `--max` — стеля ціни в гривнях. `--suggest` вибирає кілька страв зі зрізу після фільтрів; `--drink` додає напій (кава до сніданку, лимонад/чай до ролів тощо).

## JSON

Кожен файл — заклад + плоский список `items`:

```json
{
  "source": "choiceqr",
  "place": { "name": "MIRO CAFE", "address": "…", "currency": "₴" },
  "hours": [{ "days": "Пн–Сб", "from": "10:00", "till": "21:00" }],
  "items": [
    {
      "section": "СНІДАНКИ",
      "category": "СНІДАНКИ",
      "name": "Фітнес-сніданок",
      "description": "Овсянка з шпинатом, лосось…",
      "price": 395,
      "weight": "400г",
      "available": true,
      "allergens": ["яйця", "риба", "молоко", "кунжут"]
    }
  ]
}
```
