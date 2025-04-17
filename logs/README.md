# Logs and Reports
Logs will collect here. Give a day of logs or a bunch of messages to have good reports.

## Reporting Note
Reporting is via [../etc/report_generator5.py](../etc/report_generator5.py). The report_generator5 has newer feel and HTML5 coding. The index.html output is published in [../etc/www](../etc/www) there is a .cfg file created on first run for configuring values as needed (like moving web root)
 - Make sure to have `SyslogToFile = True` and default of DEBUG log level to fully enable reporting! ‼️
 - If you are in a venv and using launch.sh you can `launch.sh html5`

![reportView](../etc/reporting.jpg)

## Settings
Logging messages to disk or 'Syslog' to disk uses the python native logging function.
```conf
[general]
# logging to file of the non Bot messages only
LogMessagesToFile = False
# Logging of system messages to file, needed for reporting engine
SyslogToFile = True
# logging level for the bot (DEBUG, INFO, WARNING, ERROR, CRITICAL)
sysloglevel = DEBUG
# Number of log files to keep in days, 0 to keep all
log_backup_count = 32
```
## Web Reporting WebServer
There is a web-server module. You can run `python3 modules/web.py` from the project root directory and it will serve up the web content.

find it at. http://localhost:8420

If you have linux-native running and errors such as..
```bash
  File "/usr/lib/python3.11/http/server.py", line 136, in server_bind
    socketserver.TCPServer.server_bind(self)
  File "/usr/lib/python3.11/socketserver.py", line 472, in server_bind
    self.socket.bind(self.server_address)
```
modify the modules/web.py to use a real IP address, meshtasticD-native is binding to 127.0.0.1

```python
# Set the desired IP address
server_ip = '127.0.0.1'
```
