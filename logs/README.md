Logs will collect here.

Reporting is via [../etc/report_generator5.py](../etc/report_generator5.py), run it from the etc/ working directory. The report_generator5 has newer feel and HTML5 coding. The index.html output is published in [../etc/www](../etc/www) there is a .cfg file created on first run for configuring values as needed.
 - `multi_log_reader = True` on by default will read all logs (or set to false to return daily logs)
 - Make sure to have `SyslogToFile = True` and default of DEBUG log level to fully enable reporting! ‼️
 - provided serviceTimer templates in etc/

![reportView](../etc/reporting.jpg)

Logging messages to disk or 'Syslog' to disk uses the python native logging function.
```
[general]
# logging to file of the non Bot messages only
LogMessagesToFile = False
# Logging of system messages to file, needed for reporting engine
SyslogToFile = True
```

To change the stdout (what you see on the console) logging level (default is DEBUG) see the following example, line is in [../modules/log.py](../modules/log.py)

```
# Set level for stdout handler
stdout_handler.setLevel(logging.INFO)
```