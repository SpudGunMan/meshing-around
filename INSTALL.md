# INSTALL.md

## Table of Contents

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

### Manual Install
Install the required dependencies using pip:
```sh
pip install -r requirements.txt
```

Copy the configuration template to `config.ini` and edit it to suit your needs:
```sh
cp config.template config.ini
```


### Docker Installation - handy for windows
See further info on the [docker.md](script/docker/README.md)
### Requirements
Python 3.8? or later is needed (docker on 3.13). The following can be installed with `pip install -r requirements.txt` or using the [install.sh](install.sh) script for venv and automation:

```sh
pip install meshtastic
pip install pubsub
```

Mesh-bot enhancements:

```sh
pip install pyephem
pip install requests
pip install geopy
pip install maidenhead
pip install beautifulsoup4
pip install dadjokes
pip install schedule
pip install wikipedia
```

For the Ollama LLM:

```sh
pip install googlesearch-python
```

To enable emoji in the Debian console, install the fonts:

```sh
sudo apt-get install fonts-noto-color-emoji
```

## install.sh

### Purpose
`install.sh` is an installation and setup script for the Meshing Around Bot project. It automates installing dependencies, configuring the environment, setting up system services, and preparing the bot for use on Linux systems (especially Debian/Ubuntu/Raspberry Pi and embedded devices).

### Usage
Run this script from the project root directory:
```sh
bash install.sh
```

### What it does
- Checks for existing installations and required permissions.
- Optionally moves the project to `/opt/meshing-around` for standardization.
- Installs Python and pip if not present (unless on embedded systems).
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
Run this script from the project root directory:
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