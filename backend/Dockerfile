FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["sh", "-c", "echo INICIANDO_SIGIA && echo Ejecutando_Alembic && python -m alembic upgrade head && echo Alembic_OK && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]