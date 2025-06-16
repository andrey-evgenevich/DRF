FROM python:3.12

WORKDIR /app

RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    apt-get clean && \
    rm -rf /varlib/apt/list/*


COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

ENV SECRET_KEY=${SECRET_KEY}
ENV CELERY_BROKER_URL="redis://redis:6379/0"
ENV CELERY_BACKEND="redis://redis:6379/0"

RUN mkdir -p /app/media

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
