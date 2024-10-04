# -*- coding: utf-8 -*-
import os
import re
from datetime import datetime
from collections import Counter, defaultdict
import json
import platform
import subprocess

print("use the alpha branch of the project (lab) for better results it will all be pushed to main soon")

def parse_log_file(file_path):
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
        'total_messages': 0,
        'gps_coordinates': defaultdict(list),
        'command_timestamps': [],
        'message_timestamps': [],
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

        if 'Sending DM:' in line or 'Sending Multi-Chunk DM:' in line:
            log_data['message_types']['Outgoing DM'] += 1
            log_data['total_messages'] += 1
            log_data['message_timestamps'].append((timestamp.isoformat(), 'Outgoing DM'))

        if 'Received DM:' in line:
            log_data['message_types']['Incoming DM'] += 1
            log_data['total_messages'] += 1
            log_data['message_timestamps'].append((timestamp.isoformat(), 'Incoming DM'))

        user_match = re.search(r'From: (\w+)', line)
        if user_match:
            log_data['unique_users'].add(user_match.group(1))

        if '| WARNING |' in line:
            log_data['warnings'].append(line.strip())

        if '| ERROR |' in line:
            log_data['errors'].append(line.strip())

        bbs_match = re.search(r'ð¡BBSdb has (\d+) messages', line)
        if bbs_match:
            log_data['bbs_messages'] = int(bbs_match.group(1))

        gps_match = re.search(r'location data for (\d+) is ([-\d.]+),([-\d.]+)', line)
        if gps_match:
            node_id, lat, lon = gps_match.groups()
            log_data['gps_coordinates'][node_id].append((float(lat), float(lon)))

    log_data['unique_users'] = list(log_data['unique_users'])
    return log_data

def get_system_info():
    def get_command_output(command):
        try:
            return subprocess.check_output(command, shell=True).decode('utf-8').strip()
        except subprocess.CalledProcessError:
            return "N/A"

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
        }

    return {
        'uptime': uptime,
        'memory_total': f"{memory_total} MB",
        'memory_available': f"{memory_available} MB" if memory_available != "N/A" else "N/A",
        'disk_total': disk_total,
        'disk_free': disk_free,
    }

def generate_main_html(log_data, system_info):
    html_template = """
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meshbot (BBS) Network Statistics</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --background-color: #ecf0f1;
            --card-background: #ffffff;
            --text-color: #34495e;
            --sidebar-text-color: #ecf0f1;
            --accent-color-1: #e74c3c;
            --accent-color-2: #2ecc71;
            --accent-color-3: #f39c12;
            --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            --transition: all 0.3s ease;
        }

        [data-theme="dark"] {
            --primary-color: #1a2639;
            --secondary-color: #2980b9;
            --background-color: #2c3e50;
            --card-background: #34495e;
            --text-color: #ecf0f1;
            --sidebar-text-color: #ecf0f1;
            --accent-color-1: #c0392b;
            --accent-color-2: #27ae60;
            --accent-color-3: #d35400;
            --shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }

        [data-theme="high-contrast"] {
            --primary-color: #000000;
            --secondary-color: #ffffff;
            --background-color: #000000;
            --card-background: #000000;
            --text-color: #ffffff;
            --sidebar-text-color: #000000;
            --accent-color-1: #ff0000;
            --accent-color-2: #00ff00;
            --accent-color-3: #ffff00;
            --shadow: 0 0 0 2px #ffffff;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            line-height: 1.6;
            transition: var(--transition);
        }

        .header {
    background-color: var(--secondary-color);
    color: var(--sidebar-text-color);
    padding: 1rem;
    font-size: 1.5rem;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
    box-shadow: var(--shadow);
	}
        .main-container {
            display: flex;
            margin-top: 3.5rem;
        }

        .sidebar {
            width: 250px;
            background-color: var(--secondary-color);
            padding: 1rem;
            height: calc(100vh - 3.5rem);
            position: fixed;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: var(--shadow);
            transition: var(--transition);
        }

        .sidebar:hover {
            width: 270px;
        }

        .sidebar-nav ul {
            list-style-type: none;
        }

        .sidebar-nav li {
            margin-bottom: 1rem;
        }

        .sidebar-nav a {
            color: var(--sidebar-text-color);
            text-decoration: none;
            font-weight: 400;
            transition: var(--transition);
            display: block;
            padding: 0.5rem;
            border-radius: 4px;
        }

        .sidebar-nav a:hover {
            background-color: rgba(255, 255, 255, 0.1);
            transform: translateX(5px);
        }

        .sidebar-footer {
            font-size: 0.75rem;
            color: var(--sidebar-text-color);
            opacity: 0.8;
        }

        .content {
            margin-left: 250px;
            padding: 1rem;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            flex-grow: 1;
        }

        .chart-container {
            background-color: var(--card-background);
            border-radius: 8px;
            padding: 1.5rem;
            height: 400px;
            display: flex;
            flex-direction: column;
            box-shadow: var(--shadow);
            transition: var(--transition);
        }

        .chart-container:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }

        .chart-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--text-color);
        }

        #map, .chart-content {
            flex-grow: 1;
            width: 100%;
            border-radius: 4px;
            overflow: hidden;
        }

        .list-container {
            background-color: var(--card-background);
            border-radius: 8px;
            padding: 1.5rem;
            height: 400px;
            overflow-y: auto;
            box-shadow: var(--shadow);
            transition: var(--transition);
        }

        .list-container:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }

        ul {
            list-style-type: none;
        }

        li {
            padding: 0.75rem 0;
            border-bottom: 1px solid var(--background-color);
            transition: var(--transition);
        }

        li:last-child {
            border-bottom: none;
        }

        li:hover {
            background-color: rgba(255, 255, 255, 0.05);
            padding-left: 0.5rem;
        }

        #iframe-content {
            display: none;
            position: fixed;
            top: 3.5rem;
            left: 250px;
            right: 0;
            bottom: 0;
            background: var(--card-background);
            z-index: 900;
            box-shadow: var(--shadow);
        }

        iframe {
            width: 100%;
            height: 100%;
            border: none;
        }

        .timestamp-list {
            height: 200px;
            overflow-y: auto;
            font-size: 0.85rem;
        }

        .theme-switch {
            display: flex;
            align-items: center;
            margin-top: 1rem;
        }

        .theme-switch-label {
            margin-right: 10px;
            color: var(--sidebar-text-color);
        }

        .switch {
            position: relative;
            display: inline-block;
            width: 60px;
            height: 34px;
        }

        .switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }

        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 34px;
        }

        .slider:before {
            position: absolute;
            content: "";
            height: 26px;
            width: 26px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }

        input:checked + .slider {
            background-color: var(--accent-color-2);
        }

        input:checked + .slider:before {
            transform: translateX(26px);
        }

        @media (max-width: 768px) {
            .sidebar {
                width: 100%;
                height: auto;
                position: static;
            }

            .content {
                margin-left: 0;
                grid-template-columns: 1fr;
            }

            #iframe-content {
                left: 0;
            }
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .chart-container, .list-container {
            animation: fadeIn 0.5s ease-out;
        }
    </style>
</head>
<body>
    <header class="header">Meshbot (BBS) Network Statistics</header>
    <div class="main-container">
        <nav class="sidebar">
            <div class="sidebar-nav">
                <ul>
                    <li><a href="#" onclick="showDashboard(); return false;">Dashboard</a></li>
                    <li><a href="#" onclick="showIframe('network_map_${date}.html'); return false;">Network Map</a></li>
                    <li><a href="#" onclick="showIframe('hosts_${date}.html'); return false;">Host</a></li>
                </ul>
                <div class="theme-switch">
                    <span class="theme-switch-label">Theme:</span>
                    <label class="switch">
                        <input type="checkbox" id="theme-toggle">
                        <span class="slider"></span>
                    </label>
                </div>
            </div>
            <div class="sidebar-footer">
                <p>&copy; 2024 Meshbot Dashboard</p>
                <p>Version 1.0</p>
            </div>
        </nav>
        <main class="content" id="dashboard-content">
            <section class="chart-container">
                <h2 class="chart-title">Node Locations</h2>
                <div id="map"></div>
            </section>
            <section class="chart-container">
                <h2 class="chart-title">Network Activity</h2>
                <div class="chart-content">
                    <canvas id="activityChart"></canvas>
                </div>
            </section>
            <section class="chart-container">
                <h2 class="chart-title">Command Usage</h2>
                <div class="chart-content">
                    <canvas id="commandChart"></canvas>
                </div>
            </section>
            <section class="chart-container">
                <h2 class="chart-title">Message Types</h2>
                <div class="chart-content">
                    <canvas id="messageChart"></canvas>
                </div>
            </section>
            <section class="chart-container">
                <h2 class="chart-title">Message Counts</h2>
                <div class="chart-content">
                    <canvas id="messageCountChart"></canvas>
                </div>
            </section>
            <section class="chart-container">
                <h2 class="chart-title">Recent Commands</h2>
                <div class="timestamp-list">
                    <ul>
                        ${command_timestamps}
                    </ul>
                </div>
            </section>
            <section class="chart-container">
                <h2 class="chart-title">Recent Messages</h2>
                <div class="timestamp-list">
                    <ul>
                        ${message_timestamps}
                    </ul>
                </div>
            </section>
            <section class="list-container">
                <h2 class="chart-title">Unique Users</h2>
                <ul>
                    ${unique_users}
                </ul>
            </section>
            <section class="list-container">
                <h2 class="chart-title">Warnings</h2>
                <ul>
                    ${warnings}
                </ul>
            </section>
            <section class="list-container">
                <h2 class="chart-title">Errors</h2>
                <ul>
                    ${errors}
                </ul>
            </section>
        </main>
        <div id="iframe-content">
            <iframe id="content-iframe" src=""></iframe>
        </div>
    </div>
    <script>
        const commandData = ${command_data};
        const messageData = ${message_data};
        const activityData = ${activity_data};
        const messageCountData = {
            labels: ['BBSdb Messages', 'Total Messages'],
            datasets: [{
                label: 'Message Counts',
                data: [${bbs_messages}, ${total_messages}],
                backgroundColor: ['rgba(255, 206, 86, 0.6)', 'rgba(75, 192, 192, 0.6)']
            }]
        };

        const chartOptions = {
            responsive: true,
            maintainAspectRatio: false
        };

        function createCharts() {
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
        }

        function initMap() {
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
        }

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

        const themes = ['light', 'dark', 'high-contrast'];
        let currentThemeIndex = themes.indexOf(localStorage.getItem('theme') || 'light');

        function cycleTheme() {
            currentThemeIndex = (currentThemeIndex + 1) % themes.length;
            const newTheme = themes[currentThemeIndex];
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateCharts();
            updateSwitchState();
        }

        function updateSwitchState() {
            const switchElement = document.getElementById('theme-toggle');
            switchElement.checked = currentThemeIndex !== 0;
        }

        function updateCharts() {
            const theme = document.documentElement.getAttribute('data-theme');
            const textColor = getComputedStyle(document.documentElement).getPropertyValue('--text-color').trim();
            
            Chart.helpers.each(Chart.instances, function(chart) {
                chart.options.plugins.legend.labels.color = textColor;
                chart.options.scales.x.ticks.color = textColor;
                chart.options.scales.y.ticks.color = textColor;
                chart.update();
            });
        }

        document.addEventListener('DOMContentLoaded', function() {
            createCharts();
            initMap();

            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
            currentThemeIndex = themes.indexOf(savedTheme);
            updateSwitchState();
            updateCharts();

            document.getElementById('theme-toggle').addEventListener('change', cycleTheme);
        });
    </script>
</body>
</html>    
"""

    from string import Template
    template = Template(html_template)
    return template.safe_substitute(
        date=datetime.now().strftime('%Y_%m_%d'),
        command_data=json.dumps(log_data['command_counts']),
        message_data=json.dumps(log_data['message_types']),
        activity_data=json.dumps(log_data['hourly_activity']),
        bbs_messages=log_data['bbs_messages'],
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
                attribution: 'Â© OpenStreetMap contributors'
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

    from string import Template
    template = Template(html_template)
    return template.safe_substitute(gps_coordinates=json.dumps(log_data['gps_coordinates']))

def generate_hosts_html(system_info):
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Host Information</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }
            h1 { color: #333; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>Host Information</h1>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Uptime</td><td>${uptime}</td></tr>
            <tr><td>Total Memory</td><td>${memory_total}</td></tr>
            <tr><td>Available Memory</td><td>${memory_available}</td></tr>
            <tr><td>Total Disk Space</td><td>${disk_total}</td></tr>
            <tr><td>Free Disk Space</td><td>${disk_free}</td></tr>
        </table>
    </body>
    </html>
    """

    from string import Template
    template = Template(html_template)
    return template.safe_substitute(system_info)

def main():
    log_dir = '../logs'
    today = datetime.now().strftime('%Y_%m_%d')
    log_file = f'meshbot{today}.log'
    log_path = os.path.join(log_dir, log_file)

    log_data = parse_log_file(log_path)
    system_info = get_system_info()

    main_html = generate_main_html(log_data, system_info)
    network_map_html = generate_network_map_html(log_data)
    hosts_html = generate_hosts_html(system_info)

    output_dir = ''
    index_path = os.path.join(output_dir, 'index.html')
    
    try:
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

        print(f"HTML reports generated for {today} in {output_dir}")

    except PermissionError:
        print("Error: Permission denied. Please run the script with appropriate permissions (e.g., using sudo).")
    except Exception as e:
        print(f"An error occurred while writing the output: {str(e)}")

if __name__ == "__main__":
    main()
