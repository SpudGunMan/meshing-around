Logs will collect here.

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

Reporting is via [etc/report_generator5.py](etc/report_generator5.py) static log analysis to a HTML report file.