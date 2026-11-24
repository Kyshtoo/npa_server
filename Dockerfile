FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

ARG APP_UID=1000
ARG APP_GID=1000

RUN groupadd --gid "${APP_GID}" app \
    && useradd --uid "${APP_UID}" --gid app --home-dir /app --shell /usr/sbin/nologin app

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir -r /app/requirements.txt

COPY --chown=app:app . /app
RUN mkdir -p /app/data /app/media /app/staticfiles \
    && chown -R app:app /app/data /app/media /app/staticfiles

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/catalog/manifest/', timeout=3)"

ENTRYPOINT ["/bin/sh", "/app/docker-entrypoint.sh"]
