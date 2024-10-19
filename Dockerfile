FROM python:3.12.7-slim

WORKDIR /app

ENV APP_PATH=/app/abcall-pqrs-microservice

# Instalar las dependencias necesarias, incluyendo pg_config
RUN apt-get update && apt-get install -y libpq-dev gcc

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 3000

CMD ["chalice", "local", "--host=0.0.0.0"]
