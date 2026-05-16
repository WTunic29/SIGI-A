FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["sh", "-c", "echo 'INICIANDO SIGI-A...' && echo 'DATABASE_URL existe?' && test -n \"$DATABASE_URL\" && echo 'DATABASE_URL OK' || echo 'DATABASE_URL NO EXISTE' && echo 'Ejecutando Alembic...' && python -m alembic upgrade head && echo 'Alembic OK, iniciando Uvicorn...' && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]