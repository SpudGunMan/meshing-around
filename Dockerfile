FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y gettext && rm -rf /var/lib/apt/lists/*


WORKDIR /app
COPY . /app
COPY requirements.txt .

RUN pip install -r requirements.txt
COPY . .

COPY config.template /app/config.ini

COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
