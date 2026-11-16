# Контекст для агента

Коли користувач питає «що як», «що їсти» або про раціон — спочатку читай:

1. `data/diet.md` і `data/diet.json` — профіль Denys
2. `data/diet_picks/` — що брати в закладах
3. Сільпо — **продуктовий магазин, не заклад**. Каталог і кошик тільки через MCP `silpo` (`https://mcp.silpo.ua/mcp`). Не парсити silpo.ua як меню кафе.

Зараз вдома ремонт, плити немає: лише готові перекуси. Повноцінна їжа — у закладах (LongShot поруч). Каву й алко не п’є, томати не любить.

## MCP Сільпо

- Балабонуси в кошику завжди списувати повністю (`bonusRequested = bonusAvailable`), не питаючи.
- Desktop / цей репозиторій: `.cursor/mcp.json`
- **Cloud Agent цей сервер сам не підхоплює.** Його треба додати в [cursor.com/agents](https://cursor.com/agents) → MCP → HTTP URL `https://mcp.silpo.ua/mcp`, потім OAuth (телефон + OTP). Після логіну в цьому чаті з’являться tools `silpo_*`.

## Git

- Коміти від імені `Denys Piven <pivden2000@gmail.com>`. Агент себе ніде не згадує: ні в авторі, ні в `Co-Authored-By`, ні в посиланнях на сесію, ні в тексті коміту.
- Одразу в `master` і `git push origin master`. Без pull request і без feature-гілок (див. `.cursor/rules/git-workflow.mdc`).
