# How do I use this thing?
This is not a full turnkey setup yet?


For Ollama to work, the command line `ollama run 'model'` needs to work properly. Ensure you have enough RAM and your GPU is working as expected. The default model for this project is set to `gemma3:270m`. Ollama can be remote [Ollama Server](https://github.com/ollama/ollama/blob/main/docs/faq.md#how-do-i-configure-ollama-server) works on a pi58GB with 40 second or less response time.


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

## Docs
Note for LLM in docker with [NVIDIA](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/docker-specialized.html). Needed for the container with ollama running? 

---

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
useOpenWebUI = False
# OpenWebUI server URL (e.g., http://localhost:3000)
openWebUIURL = http://localhost:3000
# OpenWebUI API key/token (required when useOpenWebUI is True)
openWebUIAPIKey = sk-xxxx (see below for help)
```

## Validation
http://IP:3000
make a new admin user.
validate you have models imported or that the system is working for query.
make a new user for the bot

## API Key
- upper right settings for the user
- settings -> account
- get/create the API key for the user

## Docs
set api endpoint [OpenWebUI API](https://docs.openwebui.com/getting-started/api-endpoints)

---