# Проект: Автоматизация финансовых операций (салон + магазин косметики)

Репозиторий: `Yclients_integration_tables_application`
Приложение/форма → Google-таблица → YClients

## Google Таблица «Финансовые операции — рабочая таблица»
https://docs.google.com/spreadsheets/d/1gt3dtbbx-JigKtlPA9AdicRNewMDy29M86xaFSvgbaU/edit
- Лист 1 (журнал): Дата, Поставщик, ID поставщика, Статья платежа, ID статьи платежа, Касса, ID кассы, Комментарий, Номер телефона клиента, Сумма ₽, Отправлено в YClients
- Лист «Справочники»: Тип, Название, ID

## Форма ввода — Google Apps Script Web App (привязан к этой же таблице)
Ссылка: https://script.google.com/macros/s/AKfycbwb4Xb2u8WNO9bHOes1MihWH8FeI5jExClurhtVQpkpSVgP-Yw2anyVuow6upo-39w/exec
- Code.gs: справочники (поставщики/статьи/кассы) как массивы + getReferenceData(), addReferenceItem(), addEntry(), testAuth()
- index.html: розовая минималистичная форма — Дата и время (одно поле datetime-local), Поставщик, Статья платежа, Касса (у каждого «➕ Добавить новое…» → пишет в лист «Справочники»), Комментарий, Сумма. Одна кнопка «Добавить запись».
- Протестировано и работает.

## Доступы к YClients
Хранятся в Apps Script → Project Settings → Script Properties (НЕ в коде, НЕ в репозитории):
PARTNER_TOKEN, COMPANY_ID=32825, YC_LOGIN, YC_PASSWORD, USER_TOKEN (уже получен через testAuth()).
Технический пользователь YClients создан специально для интеграции (не личный аккаунт).

## Справочники — сверены с YClients
- Статьи платежа: 39 пунктов с реальными ID
- Кассы: 6 пунктов, ID подтверждены
- Контрагенты: список подтверждён

## API YClients
- POST /api/v1/finance_transactions/{company_id} — создание операции
  поля: expense_id, amount, account_id, client_id, supplier_id, master_id, comment, date ("YYYY-MM-DD HH:MM:SS")
- Авторизация: Authorization: Bearer {partner_token}, User {user_token}
- user_token: POST /api/v1/auth {login, password}

## Отдельно — НЕ часть этой цепочки
Файл «Планировщик расходов» — дашборд с формулами, не журнал. Не связываем напрямую (риск сломать формулы). В будущем (низкий приоритет) — подтянуть туда итоги формулами.

## Текущий статус и задачи
Живой статус (что сделано / что осталось) — смотреть в `CLAUDE.md` репозитория `Yclients_integration_tables_application`, не здесь.
