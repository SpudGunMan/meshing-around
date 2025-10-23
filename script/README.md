## script/runShell.sh

**Purpose:**  
`runShell.sh` is a simple demo shell script for the Mesh Bot project. It demonstrates how to execute shell commands within the project’s scripting environment.

**Usage:**  
Run this script from the terminal to see a basic example of shell scripting in the project context.

```sh
bash script/runShell.sh
```

**What it does:**  
- Changes the working directory to the script’s location.
- Prints the current directory path and a message indicating the script is running.
- Serves as a template for creating additional shell scripts or automating tasks related to the project.

**Note:**  
You can modify this script to add more shell commands or automation steps as needed for your workflow.

## script/runShell.sh

**Purpose:**  
`runShell.sh` is a demonstration shell script for the Mesh Bot project, showing how to execute shell commands in the project environment.

**Usage:**  
Run this script from the terminal to see a basic shell scripting example:

```sh
bash script/runShell.sh
```

**What it does:**  
- Changes to the script’s directory.
- Prints the current directory path.
- Displays a message indicating the script is running.

**Note:**  
You can use this as a template for your own shell scripts or to automate project-related tasks.

## script/sysEnv.sh

**Purpose:**  
`sysEnv.sh` is a shell script that collects and displays system telemetry and environment information, especially useful for monitoring a Raspberry Pi or similar device running the Mesh Bot.

**Usage:**  
Run this script from the terminal to view system stats and network info:

```sh
bash script/sysEnv.sh
```

**What it does:**  
- Reports disk space, RAM usage, CPU usage, and CPU temperature (in °C and °F).
- Checks for available Git updates if the project is a Git repository.
- Displays the device’s public and local IP addresses.
- Designed to work on Linux systems, with special handling for Raspberry Pi hardware.

**Note:**  
You can expand or modify this script to include additional telemetry or environment checks as needed for your deployment.