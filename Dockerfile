FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y gettext tzdata locales && rm -rf /var/lib/apt/lists/*

# Set the locale default to en_US.UTF-8
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8
ENV LANG=en_US.UTF-8 
ENV TZ="America/Los_Angeles"

WORKDIR /app
COPY . /app
COPY requirements.txt .

RUN pip install -r requirements.txt
COPY . .

COPY config.ini /app/config.ini
COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
