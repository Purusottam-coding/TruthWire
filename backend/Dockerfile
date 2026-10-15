FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

COPY apps/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY packages /app/packages
COPY apps/api /app/apps/api

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "apps.api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
