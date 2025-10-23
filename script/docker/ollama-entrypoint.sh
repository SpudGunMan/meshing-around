#!/bin/bash

# Start Ollama in the background.
/bin/ollama serve &
# Record Process ID.
pid=$!

# Pause for Ollama to start.
sleep 5

echo "🔴 Retrieve gemma3:270m model..."
ollama pull gemma3:270m
echo "🟢 Done!"

# Wait for Ollama process to finish.
wait $pid
