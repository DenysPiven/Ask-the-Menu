# Ask the Menu

Парсер цифрових меню і підказка «що поїсти». Без API-ключів: дані з публічних сторінок ChoiceQR і Expirenza.

## Що вміє

- `parse_menu.py` — забирає меню, кладе `data/<name>.json` і читабельний `data/<name>.md`
- `ask_menu.py` — пошук за ключовими словами, фільтр розділу/ціни, підбір страви й напою

Джерела:

| Платформа | Приклад |
|---|---|
| **ChoiceQR** | [MIRO CAFE](https://miro.vn.ua/section:snidanki) (`miro.vn.ua`, `*.choiceqr.com`) |
| **Expirenza** (`expz.menu`) | [LongShot](https://expz.menu/order/921775e1-69a8-496d-8739-0293dd0cdcf5/menu?menuId=20141&tableCode=QZ2EJ) — JSON з `static.shaketopay.com.ua/menu/prod/cache/menu/<restaurantId>/uk/` |

У репозиторії вже є зліпки:

- `data/miro.json` / `data/miro.md` — MIRO CAFE, Вінниця, Келецька 57
- `data/longshot.json` / `data/longshot.md` — LongShot, Вінниця, Юності 18

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
