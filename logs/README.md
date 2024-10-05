Logs will collect here.

Reporting is via [etc/report_generator5.py](etc/report_generator5.py), run it from the etc/ working directory. The report_generator5 has newer feel and HTML5 coding. The index.html output is published in [../etc/www](../etc/www)
 - Make sure to have `SyslogToFile = True` to use reporting! ‼️
 - serviceTimer templates for routine output
![reportView](../etc/reporting.jpg)


Logging messages to disk or Syslog to disk uses the python native logging function. Take a look at the [/modules/log.py](/modules/log.py) you can set the file logger for syslog to INFO for example to not log DEBUG messages to file log, or modify the stdOut level.
```
[general]
# logging to file of the non Bot messages
LogMessagesToFile = True
# Logging of system messages to file
SyslogToFile = True
```
Example to log to disk only INFO and higher (ignore DEBUG)
```
*log.py
file_handler.setLevel(logging.INFO) # DEBUG used by default for system logs to disk example here shows INFO
```