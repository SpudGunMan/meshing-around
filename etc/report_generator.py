import os
import re
import sys
import json
import pickle
import platform
import requests
import subprocess
from string import Template
from datetime import datetime
from importlib.metadata import version
from collections import Counter, defaultdict

# global variables
LOG_PATH = '/opt/meshing-around/logs'
W3_PATH = '/var/www/html'
multiLogReader = False

def parse_log_file(file_path):
    global log_data
    lines = ['']
    # check if the file exists
    print(f"Checking log file: {file_path}")
        
    # see if many logs are present
    if multiLogReader:
        log_files = [f for f in os.listdir(file_path) if f.endswith('.log')]
        if log_files:
            log_files.sort()

            for logFile in log_files:
                if logFile.startswith('meshbot'):
                    with open(os.path.join(file_path, logFile), 'r') as file:
                        lines += file.readlines()
    else:
        # read the file for the day
        with open(file_path, 'r') as file:
            lines = file.readlines()

    log_data = {
        'command_counts': Counter(),
        'message_types': Counter(),
        'unique_users': set(),
        'warnings': [],
        'errors': [],
        'hourly_activity': defaultdict(int),
        'bbs_messages': 0,
        'messages_waiting': 0,
        'total_messages': 0,
        'gps_coordinates': defaultdict(list),
        'command_timestamps': [],
        'message_timestamps': [],
        'firmware1_version': "N/A",
        'firmware2_version': "N/A",
        'node1_uptime': "N/A",
        'node2_uptime': "N/A",
        'node1_name': "N/A",
        'node2_name': "N/A",
        'node1_ID': "N/A",
        'node2_ID': "N/A"
    }

    for line in lines:
        timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+', line)
        if timestamp_match:
            timestamp = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')
            log_data['hourly_activity'][timestamp.strftime('%Y-%m-%d %H:00:00')] += 1

        if 'Bot detected Commands' in line:
            command = re.search(r"'cmd': '(\w+)'", line)
            if command:
                cmd = command.group(1)
                log_data['command_counts'][cmd] += 1
                log_data['command_timestamps'].append((timestamp.isoformat(), cmd))

        if 'Sending DM:' in line or 'Sending Multi-Chunk DM:' in line or 'SendingChannel:' in line or 'Sending Multi-Chunk Message:' in line:
            log_data['message_types']['Outgoing DM'] += 1
            log_data['total_messages'] += 1
            log_data['message_timestamps'].append((timestamp.isoformat(), 'Outgoing DM'))

        if 'Received DM:' in line or 'Ignoring DM:' in line or 'Ignoring Message:' in line or 'ReceivedChannel:' in line:
            log_data['message_types']['Incoming DM'] += 1
            log_data['total_messages'] += 1
            log_data['message_timestamps'].append((timestamp.isoformat(), 'Incoming DM'))

        user_match = re.search(r'From: (\w+)', line)
        if user_match:
            log_data['unique_users'].add(user_match.group(1))
            
        if 'WARNING |' in line:
            log_data['warnings'].append(line.strip())

        if 'ERROR |' in line or 'CRITICAL |' in line:
            log_data['errors'].append(line.strip())

        # bbs messages
        bbs_match = re.search(r'📡BBSdb has (\d+) messages.*?Messages waiting: (\d+)', line)
        if bbs_match:
            bbs_messages = int(bbs_match.group(1))
            messages_waiting = int(bbs_match.group(2))
            log_data['bbs_messages'] = bbs_messages
            log_data['messages_waiting'] = messages_waiting

        gps_match = re.search(r'location data for (\d+) is ([-\d.]+),([-\d.]+)', line)
        if gps_match:
            node_id = None
            node_id, lat, lon = gps_match.groups()
            log_data['gps_coordinates'][node_id].append((float(lat), float(lon)))
        
        # get firmware version for nodes
        if 'Interface1 Node Firmware:' in line:
            firmware1_match = re.search(r'Interface1 Node Firmware: (\S+)', line)
            if firmware1_match:
                firmware1_version = firmware1_match.group(1)
                log_data['firmware1_version'] = firmware1_version
        if 'Interface2 Node Firmware:' in line:
            firmware2_match = re.search(r'Interface2 Node Firmware: (\S+)', line)
            if firmware2_match:
                firmware2_version = firmware2_match.group(1)
                log_data['firmware2_version'] = firmware2_version

        # get uptime for nodes
        if 'Uptime:' in line:
            node_id = None
            uptime_match = re.search(r'Device:(\d+).*?(SNR:.*?)(?= To:)', line)
            if uptime_match:
                node_id = uptime_match.group(1)
                snr_and_more = uptime_match.group(2)
                if node_id == '1':
                    log_data['node1_uptime'] = snr_and_more
                elif node_id == '2':
                    log_data['node2_uptime'] = snr_and_more
        
        # get name and nodeID for devices
        if 'Autoresponder Started for Device' in line:
            device_match = re.search(r'Autoresponder Started for Device(\d+)\s+([^\s,]+).*?NodeID: (\d+)', line)
            if device_match:
                device_id = device_match.group(1)
                device_name = device_match.group(2)
                node_id = device_match.group(3)
                if device_id == '1':
                    log_data['node1_name'] = device_name
                    log_data['node1_ID'] = node_id
                elif device_id == '2':
                    log_data['node2_name'] = device_name
                    log_data['node2_ID'] = node_id

    log_data['unique_users'] = list(log_data['unique_users'])
    return log_data

def get_system_info():
    def get_command_output(command):
        try:
            return subprocess.check_output(command, shell=True).decode('utf-8').strip()
        except subprocess.CalledProcessError:
            return "N/A"
        
    # Capture some system information from log_data
    firmware1_version = log_data['firmware1_version']
    firmware2_version = log_data['firmware2_version']
    node1_uptime = log_data['node1_uptime']
    node2_uptime = log_data['node2_uptime']
    node1_name = log_data['node1_name']
    node2_name = log_data['node2_name']
    node1_ID = log_data['node1_ID']
    node2_ID = log_data['node2_ID']

    # get Meshtastic CLI version on web
    try:
        url = "https://pypi.org/pypi/meshtastic/json"
        data = requests.get(url, timeout=5).json()
        pypi_version = data["info"]["version"]
        cli_web = f"v{pypi_version}"
    except Exception:
        pass
    # get Meshtastic CLI version on local
    try:
        if "importlib.metadata" in sys.modules:
            cli_local = version("meshtastic")
    except:
        pass # Python 3.7 and below, meh.. 


    if platform.system() == "Linux":
        uptime = get_command_output("uptime -p")
        memory_total = get_command_output("free -m | awk '/Mem:/ {print $2}'")
        memory_available = get_command_output("free -m | awk '/Mem:/ {print $7}'")
        disk_total = get_command_output("df -h / | awk 'NR==2 {print $2}'")
        disk_free = get_command_output("df -h / | awk 'NR==2 {print $4}'")
    elif platform.system() == "Darwin":  # macOS
        uptime = get_command_output("uptime | awk '{print $3,$4,$5}'")
        memory_total = get_command_output("sysctl -n hw.memsize | awk '{print $0/1024/1024}'")
        memory_available = "N/A"  # Not easily available on macOS without additional tools
        disk_total = get_command_output("df -h / | awk 'NR==2 {print $2}'")
        disk_free = get_command_output("df -h / | awk 'NR==2 {print $4}'")
    else:
        return {
            'uptime': "N/A",
            'memory_total': "N/A",
            'memory_available': "N/A",
            'disk_total': "N/A",
            'disk_free': "N/A",
            'interface1_version': "N/A",
            'interface2_version': "N/A",
            'node1_uptime': "N/A",
            'node2_uptime': "N/A",
            'node1_name': "N/A",
            'node2_name': "N/A",
            'node1_ID': "N/A",
            'node2_ID': "N/A",
            'cli_web': "N/A",
            'cli_local': "N/A"
        }

    return {
        'uptime': uptime,
        'memory_total': f"{memory_total} MB",
        'memory_available': f"{memory_available} MB" if memory_available != "N/A" else "N/A",
        'disk_total': disk_total,
        'disk_free': disk_free,
        'interface1_version': firmware1_version,
        'interface2_version': firmware2_version,
        'node1_uptime': node1_uptime,
        'node2_uptime': node2_uptime,
        'node1_name': node1_name,
        'node2_name': node2_name,
        'node1_ID': node1_ID,
        'node2_ID': node2_ID,
        'cli_web': cli_web,
        'cli_local': cli_local
    }

def get_wall_of_shame():
    # Get the wall of shame

    return {
        'shame': "N/A",
    }

def get_database_info():
    # Get the database information

    # collect high scores from the database
    try:
        with open('../lemonade_hs.pkl', 'rb') as f:
            lemon_score = pickle.load(f)
        f.close()

        with open('../dopewar_hs.pkl', 'rb') as f:
            dopewar_score = pickle.load(f)
        f.close()

        with open('../blackjack_hs.pkl', 'rb') as f:
            blackjack_score = pickle.load(f)
        f.close()

        with open('../videopoker_hs.pkl', 'rb') as f:
            videopoker_score = pickle.load(f)
        f.close()

        with open('../mmind_hs.pkl', 'rb') as f:
            mmind_score = pickle.load(f)
        f.close()

        with open('../golfsim_hs.pkl', 'rb') as f:
            golfsim_score = pickle.load(f)
        f.close()

        with open('../bbsdb.pkl', 'rb') as f:
            bbsdb = pickle.load(f)
        f.close()

        with open('../bbsdm.pkl', 'rb') as f:
            bbsdm = pickle.load(f)
        f.close()

    except Exception as e:
        pass

    return {
        'database': "N/A",
        "bbsdb": bbsdb,
        "bbsdm": bbsdm,
        'lemon_score': lemon_score,
        'dopewar_score': dopewar_score,
        'blackjack_score': blackjack_score,
        'videopoker_score': videopoker_score,
        'mmind_score': mmind_score,
        'golfsim_score': golfsim_score
    }

def generate_main_html(log_data, system_info):
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MeshBot (BBS) Web Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f0f0f0;
                display: flex;
            }
            .header {
                background-color: #333;
                color: white;
                padding: 10px;
                font-size: 24px;
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                z-index: 1000;
            }
            .sidebar {
                width: 200px;
                background-color: #ddd;
                padding: 10px;
                height: 100vh;
                position: fixed;
                top: 50px;
                left: 0;
                overflow-y: auto;
            }
            .content {
                margin-left: 220px;
                margin-top: 60px;
                padding: 20px;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 20px;
                flex-grow: 1;
            }
            .chart-container {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 10px;
                height: 400px;
                display: flex;
                flex-direction: column;
            }
            .chart-title {
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            #map, .chart-content {
                flex-grow: 1;
                width: 100%;
            }
            .list-container {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 10px;
                height: 400px;
                overflow-y: auto;
            }
            ul {
                list-style-type: none;
                padding: 0;
                margin: 0;
            }
            li {
                padding: 5px 0;
                border-bottom: 1px solid #eee;
            }
            li:last-child {
                border-bottom: none;
            }
            #iframe-content {
                display: none;
                position: fixed;
                top: 50px;
                left: 220px;
                right: 0;
                bottom: 0;
                background: white;
                z-index: 900;
            }
            iframe {
                width: 100%;
                height: 100%;
                border: none;
            }
            .timestamp-list {
                height: 200px;
                overflow-y: auto;
                font-size: 12px;
            }
        </style>
    </head>
    <body>
        <div class="header">Meshbot (BBS) Network Statistics</div>
        <div class="sidebar">
            <ul>
                <li><a href="#" onclick="showDashboard(); return false;">Dashboard</a></li>
                <li><a href="#" onclick="showIframe('network_map_${date}.html'); return false;">Network Map</a></li>
                <li><a href="#" onclick="showIframe('wall_of_shame_${date}.html'); return false;">Wall of Shame</a></li>
                <li><a href="#" onclick="showIframe('database_${date}.html'); return false;">Database</a></li>
                <li><a href="#" onclick="showIframe('hosts_${date}.html'); return false;">System Host</a></li>
            </ul>
        </div>
        <div class="content" id="dashboard-content">
            <div class="chart-container">
                <div class="chart-title">Node Locations</div>
                <div id="map"></div>
            </div>
            <div class="chart-container">
                <div class="chart-title">Network Activity</div>
                <div class="chart-content">
                    <canvas id="activityChart"></canvas>
                </div>
            </div>
            <div class="chart-container">
                <div class="chart-title">Command Usage</div>
                <div class="chart-content">
                    <canvas id="commandChart"></canvas>
                </div>
            </div>
            <div class="chart-container">
                <div class="chart-title">Message Types</div>
                <div class="chart-content">
                    <canvas id="messageChart"></canvas>
                </div>
            </div>
            <div class="chart-container">
                <div class="chart-title">Message Counts</div>
                <div class="chart-content">
                    <canvas id="messageCountChart"></canvas>
                </div>
            </div>
            <div class="chart-container">
                <div class="chart-title">Recent Commands</div>
                <div class="timestamp-list">
                    <ul>
                        ${command_timestamps}
                    </ul>
                </div>
            </div>
            <div class="chart-container">
                <div class="chart-title">Recent Messages</div>
                <div class="timestamp-list">
                    <ul>
                        ${message_timestamps}
                    </ul>
                </div>
            </div>
            <div class="list-container">
                <div class="chart-title">Unique Users</div>
                <ul>
                    ${unique_users}
                </ul>
            </div>
            <div class="list-container">
                <div class="chart-title">Warnings</div>
                <ul>
                    ${warnings}
                </ul>
            </div>
            <div class="list-container">
                <div class="chart-title">Errors</div>
                <ul>
                    ${errors}
                </ul>
            </div>
        </div>
        <div id="iframe-content">
            <iframe id="content-iframe" src=""></iframe>
        </div>
        <script>
            const commandData = ${command_data};
            const messageData = ${message_data};
            const activityData = ${activity_data};
            const messageCountData = {
                labels: ['BBSdm Messages', 'BBSdb Messages', 'Channel Messages'],
                datasets: [{
                    label: 'Message Counts',
                    data: [${messages_waiting}, ${bbs_messages}, ${total_messages}],
                    backgroundColor: ['rgba(255, 206, 86, 0.6)', 'rgba(75, 192, 192, 0.6)', 'rgba(54, 162, 235, 0.6)']
                }]
            };

            const chartOptions = {
                responsive: true,
                maintainAspectRatio: false
            };

            new Chart(document.getElementById('commandChart'), {
                type: 'bar',
                data: {
                    labels: Object.keys(commandData),
                    datasets: [{
                        label: 'Command Usage',
                        data: Object.values(commandData),
                        backgroundColor: 'rgba(75, 192, 192, 0.6)'
                    }]
                },
                options: chartOptions
            });

            new Chart(document.getElementById('messageChart'), {
                type: 'pie',
                data: {
                    labels: Object.keys(messageData),
                    datasets: [{
                        data: Object.values(messageData),
                        backgroundColor: ['rgba(255, 99, 132, 0.6)', 'rgba(54, 162, 235, 0.6)']
                    }]
                },
                options: chartOptions
            });

            new Chart(document.getElementById('activityChart'), {
                type: 'line',
                data: {
                    labels: Object.keys(activityData),
                    datasets: [{
                        label: 'Hourly Activity',
                        data: Object.entries(activityData).map(([time, count]) => ({x: new Date(time), y: count})),
                        borderColor: 'rgba(153, 102, 255, 1)',
                        fill: false
                    }]
                },
                options: {
                    ...chartOptions,
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'hour',
                                displayFormats: {
                                    hour: 'MMM d, HH:mm'
                                }
                            },
                            title: {
                                display: true,
                                text: 'Time'
                            }
                        },
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Activity Count'
                            }
                        }
                    }
                }
            });

            new Chart(document.getElementById('messageCountChart'), {
                type: 'bar',
                data: messageCountData,
                options: {
                    ...chartOptions,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });

            var map = L.map('map').setView([0, 0], 2);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);

            var gpsCoordinates = ${gps_coordinates};
            for (var nodeId in gpsCoordinates) {
                var coords = gpsCoordinates[nodeId][0];
                L.marker(coords).addTo(map)
                    .bindPopup("Node ID: " + nodeId);
            }

            var bounds = [];
            for (var nodeId in gpsCoordinates) {
                bounds.push(gpsCoordinates[nodeId][0]);
            }
            map.fitBounds(bounds);

            function showIframe(src) {
                document.getElementById('dashboard-content').style.display = 'none';
                document.getElementById('iframe-content').style.display = 'block';
                document.getElementById('content-iframe').src = src;
            }

            function showDashboard() {
                document.getElementById('dashboard-content').style.display = 'grid';
                document.getElementById('iframe-content').style.display = 'none';
                document.getElementById('content-iframe').src = '';
            }
        </script>
    </body>
    </html>
    """
    template = Template(html_template)
    return template.safe_substitute(
        date=datetime.now().strftime('%Y_%m_%d'),
        command_data=json.dumps(log_data['command_counts']),
        message_data=json.dumps(log_data['message_types']),
        activity_data=json.dumps(log_data['hourly_activity']),
        bbs_messages=log_data['bbs_messages'],
        messages_waiting=log_data['messages_waiting'],
        total_messages=log_data['total_messages'],
        gps_coordinates=json.dumps(log_data['gps_coordinates']),
        unique_users='\n'.join(f'<li>{user}</li>' for user in log_data['unique_users']),
        warnings='\n'.join(f'<li>{warning}</li>' for warning in log_data['warnings']),
        errors='\n'.join(f'<li>{error}</li>' for error in log_data['errors']),
        command_timestamps='\n'.join(f'<li>{timestamp}: {cmd}</li>' for timestamp, cmd in reversed(log_data['command_timestamps'][-50:])),
        message_timestamps='\n'.join(f'<li>{timestamp}: {msg_type}</li>' for timestamp, msg_type in reversed(log_data['message_timestamps'][-50:]))
    )

def generate_network_map_html(log_data):
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Network Map</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <style>
            body { margin: 0; padding: 0; }
            #map { position: absolute; top: 0; bottom: 0; width: 100%; }
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            var map = L.map('map').setView([0, 0], 2);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);

            var gpsCoordinates = ${gps_coordinates};
            for (var nodeId in gpsCoordinates) {
                var coords = gpsCoordinates[nodeId][0];
                L.marker(coords).addTo(map)
                    .bindPopup("Node ID: " + nodeId);
            }

            var bounds = [];
            for (var nodeId in gpsCoordinates) {
                bounds.push(gpsCoordinates[nodeId][0]);
            }
            map.fitBounds(bounds);
        </script>
    </body>
    </html>
    """

    template = Template(html_template)
    return template.safe_substitute(gps_coordinates=json.dumps(log_data['gps_coordinates']))

def generate_sys_hosts_html(system_info):
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>System Host Information</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }
            h1 { color: #333; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>System Host Information</h1>
        <table>
            <tr><th>OS Metric</th><th>Value</th></tr>
            <tr><td>Uptime</td><td>${uptime}</td></tr>
            <tr><td>Total Memory</td><td>${memory_total}</td></tr>
            <tr><td>Available Memory</td><td>${memory_available}</td></tr>
            <tr><td>Total Disk Space</td><td>${disk_total}</td></tr>
            <tr><td>Free Disk Space</td><td>${disk_free}</td></tr>
            <tr><th>Meshtastic CLI/API</th><th>Value</th></tr>
            <tr><td>API Version/Latest</td><td>${cli_local} / ${cli_web}</td></tr>
            <tr><td>Int1 Name ID</td><td>${node1_name} (${node1_ID})</td></tr>
            <tr><td>Int1 Stat</td><td>${node1_uptime}</td></tr>
            <tr><td>Int1 FW Version</td><td>${interface1_version}</td></tr>
            <tr><td>Int2 Name ID</td><td>${node2_name} (${node2_ID})</td></tr>
            <tr><td>Int2 Stat</td><td>${node2_uptime}</td></tr>
            <tr><td>Int2 FW Version</td><td>${interface2_version}</td></tr>
        </table>
    </body>
    </html>
    """

    template = Template(html_template)
    return template.safe_substitute(system_info)

def generate_wall_of_shame_html(shame_info):
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Wall Of Shame</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }
            h1 { color: #333; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>Put Shame Here</h1>
        <table>
            <tr><th>Shame Metric</th><th>Value</th></tr>
            <tr><td>shame</td><td>${shame}</td></tr>
        </table>
    </body>
    </html>
    """

    template = Template(html_template)
    return template.safe_substitute(shame_info)

def generate_database_html(database_info):
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Database Information</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }
            h1 { color: #333; }
        </style>
    </head>
    <body>
        <h1>Database Information</h1>
        <p>${database}</p>
        <h1>BBS Message Database</h1>
        <p>BBSdb: ${bbsdb}</p>
        <p>BBSdm: ${bbsdm}</p>
        <h1>High Scores</h1>
        <table>
            <tr><th>Game</th><th>High Score</th></tr>
            <tr><td>Lemonade Stand</td><td>${lemon_score}</td></tr>
            <tr><td>Dopewars</td><td>${dopewar_score}</td></tr>
            <tr><td>Blackjack</td><td>${blackjack_score}</td></tr>
            <tr><td>Video Poker</td><td>${videopoker_score}</td></tr>
            <tr><td>Mastermind</td><td>${mmind_score}</td></tr>
            <tr><td>Golf Simulator</td><td>${golfsim_score}</td></tr>
        </table>
    </body>
    </html>
    """

    template = Template(html_template)
    return template.safe_substitute(database_info)

def main():
    log_dir = LOG_PATH
    today = datetime.now().strftime('%Y_%m_%d')
    log_file = f'meshbot{today}.log'
    log_path = os.path.join(log_dir, log_file)

    if not os.path.exists(log_path):
        # set file_path to the cwd of the default project ../log
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'logs')
        file_path = os.path.abspath(file_path)
        log_path = os.path.join(file_path, log_file)

    log_data = parse_log_file(log_path)
    system_info = get_system_info()
    shame_info = get_wall_of_shame()
    database_info = get_database_info()

    main_html = generate_main_html(log_data, system_info)
    network_map_html = generate_network_map_html(log_data)
    hosts_html = generate_sys_hosts_html(system_info)
    wall_of_shame = generate_wall_of_shame_html(shame_info)
    database_html = generate_database_html(database_info)

    output_dir = W3_PATH
    index_path = os.path.join(output_dir, 'index.html')
    
    try:
        if not os.path.exists(output_dir):
            output_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'www')
            output_dir = os.path.abspath(output_dir)
            index_path = os.path.join(output_dir, 'index.html')

        # Create backup of existing index.html if it exists
        if os.path.exists(index_path):
            backup_path = os.path.join(output_dir, f'index_backup_{today}.html')
            os.rename(index_path, backup_path)
            print(f"Existing index.html backed up to {backup_path}")

        # Write main HTML to index.html
        with open(index_path, 'w') as f:
            f.write(main_html)
        print(f"Main dashboard written to {index_path}")

        # Write other HTML files
        with open(os.path.join(output_dir, f'network_map_{today}.html'), 'w') as f:
            f.write(network_map_html)
        
        with open(os.path.join(output_dir, f'hosts_{today}.html'), 'w') as f:
            f.write(hosts_html)

        with open(os.path.join(output_dir, f'wall_of_shame_{today}.html'), 'w') as f:
            f.write(wall_of_shame)
        
        with open(os.path.join(output_dir, f'database_{today}.html'), 'w') as f:
            f.write(database_html)

        print(f"HTML reports generated for {today} in {output_dir}")

    except PermissionError:
        print("Error: Permission denied. Please run the script with appropriate permissions (e.g., using sudo).")
    except Exception as e:
        print(f"An error occurred while writing the output: {str(e)}")

if __name__ == "__main__":
    main()
