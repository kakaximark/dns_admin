FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    chmod -R a+rwx /app

EXPOSE 8080

CMD ["python", "app.py"]
