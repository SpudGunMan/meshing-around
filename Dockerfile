FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY mesh_bot.py bot.toml ./
COPY botcore/ ./botcore/
COPY plugins.d/ ./plugins.d/
RUN mkdir -p data
ENTRYPOINT ["python", "mesh_bot.py"]
