FROM python:3.13-slim

WORKDIR /app

COPY requirements/runtime.txt .

RUN pip install --no-cache-dir -r runtime.txt

COPY app ./app
COPY src ./src
COPY config ./config

RUN mkdir -p logs

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]