from flask import Flask, render_template, jsonify
import random
import time
import threading
import logging

app = Flask(__name__)

# Lists to store temperature data for the graph
temperature_data = []
time_data = []

# Configuration
NUM_DATA_POINTS = 30  # Number of data points to keep
SIMULATION_INTERVAL = 0.15  # Simulation data collection interval (in seconds)

# Logging configuration
logging.basicConfig(filename='temperature_monitor.log', level=logging.INFO)

# Error handling
@app.errorhandler(Exception)
def handle_error(e):
    logging.error('An error occurred: %s', str(e))
    return jsonify(error=str(e)), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-reading')
def start_reading():
    global temperature_data, time_data
    temperature_data = []
    time_data = []
    return 'Reading started.'

@app.route('/stop-reading')
def stop_reading():
    return 'Reading stopped.'

@app.route('/temperature-data')
def get_temperature_data():
    if time_data and temperature_data:
        data = {
            'time': time_data,
            'temperature': temperature_data,
        }
        return jsonify(data)
    else:
        return jsonify({'time': None, 'temperature': None})

def simulate_temperature_data():
    while True:
        if len(time_data) >= NUM_DATA_POINTS:
            time_data.pop(0)
            temperature_data.pop(0)

        current_time = time.time()
        temperature = random.uniform(20, 35)

        time_data.append(current_time)
        temperature_data.append(temperature)
        time.sleep(SIMULATION_INTERVAL)

if __name__ == '__main__':
    # Start a separate thread to simulate temperature data
    simulation_thread = threading.Thread(target=simulate_temperature_data)
    simulation_thread.daemon = True
    simulation_thread.start()

    app.run(debug=True, port=5001)
