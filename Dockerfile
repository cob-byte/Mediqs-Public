FROM python:3.10.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

COPY . .

CMD python manage.py migrate \
    && python manage.py collectstatic --noinput \
    && python -m gunicorn Mediqs.wsgi:application --bind 0.0.0.0:${PORT:-8000}
