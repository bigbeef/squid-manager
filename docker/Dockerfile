FROM docker.m.daocloud.io/python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV SQLITE_DB_PATH=/app/data/squid_manager.db
ENV SQUID_PASSWD_PATH=/app/squid/squid_passwd

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY src ./src

RUN mkdir -p /app/data /app/squid

EXPOSE 8000

CMD ["uvicorn", "src.app.web:app", "--host", "0.0.0.0", "--port", "8000"]
