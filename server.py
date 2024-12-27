from flask import Flask, render_template_string, jsonify, request
import subprocess

app = Flask(__name__)

# List of available Chromecast devices and music streams
CHROMECAST_DEVICES = [
    {'name': 'Jenna box', 'ip': '192.168.2.35'},
    {'name': 'Eline box', 'ip': '192.168.2.19'}
]

MUSIC_STREAMS = [
    {'name': 'Q Music Foute Uur', 'url': 'https://stream.qmusic.nl/fouteuur/mp3'},
    {'name': 'Q Music Non-stop', 'url': 'https://stream.qmusic.nl/nonstop/mp3'}
]

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Music Stream Control</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        /* Some basic styles for the webpage */
        body { 
            text-align: center; 
            padding: 20px; 
            font-family: Arial, sans-serif; 
        }
        button { 
            padding: 15px 30px; 
            font-size: 18px; 
            margin: 10px;
            border: none;
            border-radius: 5px;
            color: white;
            cursor: pointer;
        }
        .start { background-color: #4CAF50; }
        .stop { background-color: #f44336; }

        /* Style for the dropdown selectors */
        select {
            padding: 10px;
            font-size: 16px;
            margin: 10px;
        }

        /* Styles specifically for the volume control */
        .volume-control {
            margin: 20px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }

        .volume-button {
            width: 50px;
            height: 50px;
            font-size: 25px;
            line-height: 50px;
            text-align: center;
            background-color: #2196F3;
            border-radius: 50%;
            display: inline-block;
            color: white;
            margin: 0 10px;
        }

        /* Style the volume level display */
        #volumeLevel {
            font-size: 18px;
            margin-top: 10px;
        }

        .volume-buttons {
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>Music Stream Control</h1>

    <!-- Device and music stream selectors -->
    <div>
        <select id="deviceSelector">
            {% for device in chromecast_devices %}
            <option value="{{ device.ip }}">{{ device.name }}</option>
            {% endfor %}
        </select>

        <select id="streamSelector">
            {% for stream in music_streams %}
            <option value="{{ stream.url }}">{{ stream.name }}</option>
            {% endfor %}
        </select>
    </div>

    <!-- Start and stop buttons -->
    <button class="start" onclick="startStream()">Start Streaming</button>
    <button class="stop" onclick="stopStream()">Stop Streaming</button>
    
    <!-- Volume control with buttons -->
    <div class="volume-control">
        <h3>Volume Control</h3>
        <div class="volume-buttons">
            <div class="volume-button" onclick="changeVolume(-5)">-</div>
            <div id="volumeLevel">30%</div>
            <div class="volume-button" onclick="changeVolume(5)">+</div>
        </div>
    </div>
    
    <div id="status"></div>

    <script>
        // Get the currently selected device from the dropdown
        function getSelectedDevice() {
            const selector = document.getElementById('deviceSelector');
            return selector.value;
        }

        // Get the currently selected stream from the dropdown
        function getSelectedStream() {
            const selector = document.getElementById('streamSelector');
            return selector.value;
        }

        // Start the music stream on the selected device
        function startStream() {
            const device = getSelectedDevice();
            const stream = getSelectedStream();
            fetch(`/start?device=${device}&stream=${encodeURIComponent(stream)}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status').textContent = data.message;
                });
        }
        
        // Stop the music stream on the selected device
        function stopStream() {
            const device = getSelectedDevice();
            fetch(`/stop?device=${device}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status').textContent = data.message;
                });
        }
        
        // Update the volume display and set the volume
        function updateVolumeDisplay(value) {
            document.getElementById('volumeLevel').textContent = value + '%';
            setVolume(value);
        }

        // Make API call to set the volume on the device
        function setVolume(value) {
            const device = getSelectedDevice();
            fetch(`/volume/${value}?device=${device}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status').textContent = data.message;
                });
        }

        // Change the volume by a delta value
        function changeVolume(delta) {
            const volumeText = document.getElementById('volumeLevel').textContent;
            let volume = parseInt(volumeText);
            volume = Math.min(100, Math.max(0, volume + delta));
            updateVolumeDisplay(volume);
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML, chromecast_devices=CHROMECAST_DEVICES, music_streams=MUSIC_STREAMS)

@app.route('/start')
def start_stream():
    try:
        device_ip = request.args.get('device', '')
        stream_url = request.args.get('stream', '')
        subprocess.run(['sudo', 'catt', '-d', device_ip, 'cast', stream_url], check=True)
        return jsonify({'message': 'Stream started successfully'})
    except subprocess.CalledProcessError:
        return jsonify({'message': 'Failed to start stream'}), 500

@app.route('/stop')
def stop_stream():
    try:
        device_ip = request.args.get('device', '')
        subprocess.run(['sudo', 'catt', '-d', device_ip, 'stop'], check=True)
        return jsonify({'message': 'Stream stopped successfully'})
    except subprocess.CalledProcessError:
        return jsonify({'message': 'Failed to stop stream'}), 500

@app.route('/volume/<level>')
def set_volume(level):
    try:
        device_ip = request.args.get('device', '')
        subprocess.run(['sudo', 'catt', '-d', device_ip, 'volume', level], check=True)
        return jsonify({'message': f'Volume set to {level}%'})
    except subprocess.CalledProcessError:
        return jsonify({'message': 'Failed to set volume'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)