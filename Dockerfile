FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y gettext tzdata locales && rm -rf /var/lib/apt/lists/*

# Set the locale default to en_US.UTF-8
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8
ENV LANG="en_US.UTF-8"
ENV TZ="America/Los_Angeles"

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

RUN chmod +x /app/script/docker/entrypoint.sh

ENTRYPOINT ["/app/script/docker/entrypoint.sh"]
