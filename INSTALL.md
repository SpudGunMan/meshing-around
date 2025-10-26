# INSTALL.md

## Table of Contents

- [Manual Install](#manual-install)
- [Docker Installation](#docker-installation)
- [Requirements](#requirements)
- [install.sh](#installsh)
  - [Purpose](#purpose)
  - [Usage](#usage)
  - [What it does](#what-it-does)
  - [When to use](#when-to-use)
  - [Note](#note)
- [update.sh](#updatesh)
  - [Purpose](#purpose-1)
  - [Usage](#usage-1)
  - [What it does](#what-it-does-1)
  - [When to use](#when-to-use-1)
  - [Note](#note-1)
- [launch.sh](#launchsh)
  - [Purpose](#purpose-2)
  - [How to Use](#how-to-use)
  - [What it does](#what-it-does-2)
  - [Note](#note-2)

---

## Manual Install

Install all required dependencies using pip:

```sh
pip install -r requirements.txt
```

Copy the configuration template and edit as needed:

```sh
cp config.template config.ini
```

---

## Docker Installation

See [script/docker/README.md](script/docker/README.md) for Docker-based setup instructions.  
Docker is recommended for Windows or if you want an isolated environment.

---

## Requirements

- **Python 3.8 or later** (Python 3.13+ supported in Docker)
- All dependencies are listed in `requirements.txt` and can be installed with:
  ```sh
  pip install -r requirements.txt
  ```
- To enable emoji in the Debian/Ubuntu console:
  ```sh
  sudo apt-get install fonts-noto-color-emoji
  ```
- For Ollama LLM support, see the prompts during `install.sh` or visit [https://ollama.com](https://ollama.com).

---

## install.sh

### Purpose

`install.sh` automates installation, configuration, and service setup for the Meshing Around Bot project. It is designed for Linux systems (Debian/Ubuntu/Raspberry Pi and embedded devices).

### Usage

Run from the project root directory:

```sh
bash install.sh
```

To uninstall:

```sh
bash install.sh --nope
```

### What it does

- Checks for existing installations and permissions.
- Optionally moves the project to `/opt/meshing-around`.
- Installs Python and pip if missing (unless on embedded systems).
- Adds the current user (or a dedicated `meshbot` user) to necessary groups for serial and Bluetooth access.
- Copies and configures systemd service files for running the bot as a service.
- Sets up configuration files, updating latitude/longitude automatically.
- Offers to create and activate a Python virtual environment, or install dependencies system-wide.
- Installs optional components (emoji fonts, Ollama LLM) if desired.
- Sets permissions for log and data directories.
- Optionally installs and enables the bot as a systemd service.
- Provides post-installation notes and commands in `install_notes.txt`.
- Offers to reboot the system to complete setup.

### When to use

- For first-time installation of the Meshing Around Bot.
- When migrating to a new device or environment.
- After cloning or updating the repository to set up dependencies and services.

### Note

- You may be prompted for input during installation (e.g., for embedded mode, virtual environment, or optional features).
- Review and edit the script if you have custom requirements or are running on a non-standard system.

---

## update.sh

### Purpose

`update.sh` is an update and maintenance script for the Meshing Around Bot project. It automates the process of safely updating your codebase, backing up data, and merging configuration changes.

### Usage

Run from the project root directory:

```sh
bash update.sh
```
Or, after making it executable:
```sh
chmod +x update.sh
./update.sh
```

### What it does

- Stops running Mesh Bot services to prevent conflicts during update.
- Fetches and pulls the latest changes from the GitHub repository (using `git pull --rebase`).
- Handles git conflicts, offering to reset to the latest remote version if needed.
- Copies a custom scheduler template if not already present.
- Backs up the `data/` directory (and `custom_scheduler.py` if present) to a compressed archive.
- Merges your existing configuration with new defaults using `script/configMerge.py`, and logs the process.
- Restarts services if they were stopped for the update.
- Provides status messages and logs for troubleshooting.

### When to use

- To update your Mesh Bot installation to the latest version.
- Before making significant changes or troubleshooting, as it creates a backup of your data.

### Note

- Review `ini_merge_log.txt` and `config_new.ini` after running for any configuration changes or errors.
- You may be prompted if git conflicts are detected.

---

## launch.sh

### Purpose

`launch.sh` is a convenience script for starting the Mesh Bot, Pong Bot, or generating reports within the Python virtual environment. It ensures the correct environment is activated and the appropriate script is run.

### How to Use

From your project root, run one of the following commands:

- Launch Mesh Bot:  
  ```sh
  bash launch.sh mesh
  ```
- Launch Pong Bot:  
  ```sh
  bash launch.sh pong
  ```
- Generate HTML report:  
  ```sh
  bash launch.sh html
  ```
- Generate HTML5 report:  
  ```sh
  bash launch.sh html5
  ```
- Add a favorite (calls `script/addFav.py`):  
  ```sh
  bash launch.sh add
  ```

### What it does

- Ensures you are in the project directory.
- Copies `config.template` to `config.ini` if no config exists.
- Activates the Python virtual environment (`venv`).
- Runs the selected Python script based on your argument.
- Deactivates the virtual environment when done.

### Note

- The script requires a Python virtual environment (`venv`) to be present in the project directory.
- If `venv` is missing, the script will exit with an error message.
- Always provide an argument (`mesh`, `pong`, `html`, `html5`, or `add`) to specify what you want to launch.