FROM python:3.14-slim
ENV PYTHONUNBUFFERED=1

ENV PYTHONUNBUFFERED=1 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8 \
    TZ=America/Los_Angeles

RUN apt-get update && \
    apt-get install -y \
        build-essential \
        python3-dev \
        gettext \
        tzdata \
        locales \
        nano && \
    sed -i 's/^# *\(en_US.UTF-8 UTF-8\)/\1/' /etc/locale.gen && \
    locale-gen en_US.UTF-8 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first for better caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the application
COPY . /app
COPY config.template /app/config.ini

RUN chmod +x /app/script/docker/entrypoint.sh

# Add a non-root user and switch to it
# RUN useradd -m appuser && usermod -a -G dialout appuser
# USER appuser

# Expose Meshtastic TCP API port from the host
#EXPOSE 4403
# Meshing Around Web Dashboard port
#EXPOSE 8420

ENTRYPOINT ["/bin/bash", "/app/script/docker/entrypoint.sh"]
