# How do I use this thing?
This is not a full turnkey setup for Docker yet?


# Ollama local
```bash
# bash
curl -fsSL https://ollama.com/install.sh | sh
# docker
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -e OLLAMA_API_BASE_URL=http://host.docker.internal:11434 open-webui/open-webui
```

```ini
#service file addition
# https://github.com/ollama/ollama/issues/703
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
```
## validation
http://IP::11434
`Ollama is running`

# OpenWebUI (docker)
```bash
## ollama in docker
docker run -d -p 3000:8080 --gpus all -v open-webui:/app/backend/data --name open-webui ghcr.io/open-webui/open-webui:cuda

## external ollama
docker run -d -p 3000:8080 -e OLLAMA_BASE_URL=https://IP:11434 -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
```
wait for engine to build, update the config.ini for the bot

```ini
# Use OpenWebUI instead of direct Ollama API (enables advanced RAG features)
useOpenWebUI = True
# OpenWebUI server URL (e.g., http://localhost:3000)
openWebUIURL = http://IP:3000
```

## validation
http://IP:3000
make a new admin user.
validate you have models imported or that the system is working for query.
set api endpoint [OpenWebUI API](https://docs.openwebui.com/getting-started/api-endpoints)
to quickly get started, go to admin ->settings ->connections ->Manage OpenAI API Connections ->Auth Type None