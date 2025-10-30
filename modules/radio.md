# Radio Module: Meshages TTS (Text-to-Speech) Setup

The radio module supports audible mesh messages using the [KittenTTS](https://github.com/KittenML/KittenTTS) engine. This allows the bot to generate and play speech from text, making mesh alerts and messages audible on your device.

## Features

- Converts mesh messages to speech using KittenTTS.

## Installation

1. **Install Python dependencies:**

   - `kittentts` is the TTS engine.

`pip install https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl`

2. **Install PortAudio (required for sounddevice):**

   - **macOS:**  
     ```sh
     brew install portaudio
     ```
   - **Linux (Debian/Ubuntu):**  
     ```sh
     sudo apt-get install portaudio19-dev
     ```
   - **Windows:**  
     No extra step needed; `sounddevice` will use the default audio driver.

## Configuration

- Enable TTS in your `config.ini`:
  ```ini
  [radioMon]
  meshagesTTS = True
  ```

## Usage

When enabled, the bot will generate and play speech for mesh messages using the selected voice.  
No additional user action is required.

## Troubleshooting

- If you see errors about missing `sounddevice` or `portaudio`, ensure you have installed the dependencies above.
- On macOS, you may need to allow microphone/audio access for your terminal.
- If you have audio issues, check your system’s default output device.

## References

- [KittenTTS GitHub](https://github.com/KittenML/KittenTTS)
- [KittenTTS Model on HuggingFace](https://huggingface.co/KittenML/kitten-tts-nano-0.2)
- [sounddevice documentation](https://python-sounddevice.readthedocs.io/)

---