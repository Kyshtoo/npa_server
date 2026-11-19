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

Для рабочего сервера задайте переменные окружения (значения ниже приведены
только как пример):

```text
DJANGO_SECRET_KEY=replace-with-a-long-random-value
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=npa.example.kg
DJANGO_CSRF_TRUSTED_ORIGINS=https://npa.example.kg
```

Выбор хостинга и домена пока не зафиксирован в ТЗ, поэтому
production-конфигурация намеренно не привязана к конкретному провайдеру.
