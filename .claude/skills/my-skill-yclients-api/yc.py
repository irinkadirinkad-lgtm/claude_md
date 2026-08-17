#!/usr/bin/env python3
"""Клиент YClients API для сессий Claude (читать данные напрямую, без Apps Script).

Ключи НИКОГДА не хранятся в репозитории. Порядок поиска:
  1. переменные окружения YC_PARTNER_TOKEN / YC_USER_TOKEN / YC_COMPANY_ID
  2. файл, указанный в YC_KEYS (json: {"partner": "...", "user": "...", "company": 328251})
  3. ~/.yclients.json того же формата (кладётся во временный контейнер сессии, не в git)

Использование из терминала:
    python3 yc.py get /goods/328251?page=1&count=1     # сырой ответ любого GET
    python3 yc.py goods                                # весь каталог товаров (постранично)
    python3 yc.py good <good_id|артикул|часть названия> # карточка(и) со ВСЕМИ полями
    python3 yc.py storages                             # склады
    python3 yc.py whoami                               # проверка ключей

Только чтение. Любая запись (POST/PUT/DELETE) — отдельно и только после согласования с Ириной.
"""
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://api.yclients.com/api/v1"
ACCEPT = "application/vnd.yclients.v2+json"
PACE_SEC = 0.25  # YClients: 5 запросов/с официально — держим ≤4


def keys():
    p, u = os.environ.get("YC_PARTNER_TOKEN"), os.environ.get("YC_USER_TOKEN")
    c = os.environ.get("YC_COMPANY_ID")
    if p and u:
        return {"partner": p, "user": u, "company": int(c or 328251)}
    for path in [os.environ.get("YC_KEYS"), str(pathlib.Path.home() / ".yclients.json")]:
        if path and pathlib.Path(path).exists():
            k = json.loads(pathlib.Path(path).read_text())
            k.setdefault("company", 328251)
            return k
    raise SystemExit(
        "Нет ключей YClients. Положи их в ~/.yclients.json:\n"
        '  {"partner": "<PARTNER_TOKEN>", "user": "<USER_TOKEN>", "company": 328251}\n'
        "Где взять: Apps Script проекта интеграции → Настройки проекта → Свойства скрипта."
    )


_K = None


def get(path, params=None):
    """GET к API. Возвращает распарсенный JSON, кидает исключение на ошибке."""
    global _K
    _K = _K or keys()
    url = BASE + path
    if params:
        url += ("&" if "?" in path else "?") + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer %s, User %s" % (_K["partner"], _K["user"]),
        "Accept": ACCEPT,
        "Content-Type": "application/json",
    })
    for attempt in range(3):
        try:
            time.sleep(PACE_SEC)
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:500]
            if e.code == 429 and attempt < 2:      # троттлинг — подождать и повторить
                time.sleep(3 * (attempt + 1))
                continue
            raise SystemExit("HTTP %s на %s\n%s" % (e.code, url, body))


def company():
    global _K
    _K = _K or keys()
    return _K["company"]


def goods(pause_pages=True):
    """Весь каталог товаров. /goods отдаёт ~25 позиций на страницу, count не расширяет."""
    out, page = [], 1
    while page <= 200:
        rows = get("/goods/%s" % company(), {"page": page, "count": 100}).get("data") or []
        if not rows:
            break
        out.extend(rows)
        page += 1
    return out


def find(needle):
    """Товары по good_id, точному артикулу или части названия (регистр не важен)."""
    s = str(needle).strip().lower()
    hit = []
    for g in goods():
        if (str(g.get("good_id")) == s or str(g.get("article", "")).lower() == s
                or s in str(g.get("title", "")).lower()):
            hit.append(g)
    return hit


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "whoami"
    if cmd == "get":
        print(json.dumps(get(argv[2]), ensure_ascii=False, indent=2)[:8000])
    elif cmd == "goods":
        g = goods()
        print("всего товаров: %d" % len(g))
        print(json.dumps(g[:3], ensure_ascii=False, indent=2))
    elif cmd == "good":
        hit = find(argv[2])
        print("совпадений: %d" % len(hit))
        print(json.dumps(hit[:5], ensure_ascii=False, indent=2))
    elif cmd == "storages":
        print(json.dumps(get("/storages/%s" % company()), ensure_ascii=False, indent=2))
    elif cmd == "whoami":
        d = get("/company/%s" % company()).get("data") or {}
        print("OK: %s (id %s), %s" % (d.get("title"), d.get("id"), d.get("city")))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
