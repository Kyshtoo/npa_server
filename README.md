# Сервер каталога НПА

Django REST API и административная панель для мобильного приложения
Кыргызской геологической службы.

## Локальный запуск

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py setup_roles
python manage.py runserver 0.0.0.0:8000
```

Административная панель: `http://127.0.0.1:8000/admin/`.

## Основные API

- `GET /api/categories/` — активные категории;
- `GET /api/categories/<id>/documents/` — опубликованные документы категории;
- `GET /api/documents/<id>/` — документ, структура и PDF;
- `GET /api/search/?q=текст&lang=ru` — поиск;
- `GET /api/catalog/manifest/` — версия и размер обновления;
- `GET /api/catalog/export/` — полный каталог для офлайн-режима.

## Редакторы

Команда `python manage.py setup_roles` создаёт группу **Редакторы НПА**.
Добавьте сотрудника в эту группу через Django Admin. Редактор может создавать,
исправлять и публиковать каталог, но не управляет пользователями и не удаляет
документы целиком.

## Word и PDF

На странице списка документов в админ-панели есть кнопка **Импорт из Word**.
Импорт распознаёт разделы, главы, статьи и пункты, но результат обязательно
нужно проверить. Официальные PDF добавляются внутри карточки документа.

## Офлайн-сборка

Для ручного экспорта встроенного JSON:

```powershell
python manage.py export_catalog catalog.json
```

## Проверка

```powershell
python manage.py check
python manage.py makemigrations --check
python manage.py test
```

## Запуск на Ubuntu через Docker

Production-контейнер использует Gunicorn и публикуется только на локальном
адресе `127.0.0.1:8001`. Наружу API должен открывать Nginx.

```bash
cp .env.example .env
openssl rand -hex 48
```

Скопируйте результат второй команды в `DJANGO_SECRET_KEY` файла `.env`.
Если `id -u` или `id -g` возвращают не `1000`, также исправьте `APP_UID` и
`APP_GID`. Затем:

```bash
mkdir -p data media staticfiles
docker compose -f docker-compose.production.yml up -d --build
docker compose -f docker-compose.production.yml ps
curl http://127.0.0.1:8001/api/catalog/manifest/
```

Постоянные данные не находятся внутри контейнера:

- `data/db.sqlite3` — база данных;
- `media/` — загруженные Word/PDF-файлы;
- `staticfiles/` — статика административной панели.

Для создания администратора:

```bash
docker compose -f docker-compose.production.yml exec api \
  python manage.py createsuperuser
```

Пример upstream для Nginx: `http://127.0.0.1:8001`. После подключения HTTPS
установите в `.env` значения `DJANGO_SECURE_COOKIES=1` и
`DJANGO_SECURE_SSL_REDIRECT=1`, затем перезапустите контейнер.

Готовый шаблон виртуального хоста находится в
`deploy/nginx-npa-api.conf`. Он не изменяет конфигурацию существующего сайта
`geology-ecatalog.net.kg` и использует отдельный поддомен.
