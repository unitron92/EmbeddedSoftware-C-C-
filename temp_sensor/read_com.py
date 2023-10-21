import serial
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import time

# Define the COM port and baud rate
com_port = 'COM6'  # Change this to your COM port
baud_rate = 115200  # Change this to match your device's baud rate

# Lists to store temperature data for the graph
temperature_data = []
time_data = []

# Create a function to read and display data
def read_and_display_data():
    try:
        ser = serial.Serial(com_port, baud_rate)
        data_label.config(text="Reading data...")
        start_time = datetime.now()
        prev_temperature = None  # To track the previous temperature reading

        while not stop_reading:
            data = ser.readline().decode('utf-8').strip()
            
            # Extract the numeric part (temperature value) from the string
            temperature_str = data.split(' ')[0]
            try:
                temperature = float(temperature_str)
            except ValueError:
                data_label.config(text=f"Error: Invalid temperature data")
                continue  # Skip this iteration if temperature is not valid

            formatted_temperature = "{:.2f}".format(temperature)  # Format to 2 decimal places
            
            # Check if the temperature is increasing or decreasing
            if prev_temperature is not None:
                color = 'red' if temperature > prev_temperature else 'blue'
            else:
                color = 'black'
            
            # Update the graph with the appropriate color
            temperature_graph.plot(time_data, temperature_data, label='Temperature (°C)', color=color)
            prev_temperature = temperature  # Update previous temperature
            data_label.config(text=f"Data: Temperature: {formatted_temperature} °C")
            temperature_data.append(temperature)
            time_data.append((datetime.now() - start_time).total_seconds())
            
            # Set the y-axis range for the temperature values (adjust min and max as needed)
            temperature_graph.set_ylim(25, 35)
            
            temperature_canvas.draw()
            root.update_idletasks()
            
            # Introduce a 200-millisecond delay to slow down data refresh
            time.sleep(0.2)
        
    except serial.SerialException as e:
        data_label.config(text=f"Error: {e}")
    finally:
        if 'ser' in locals():
            ser.close()

# Create a function to stop reading data
def stop_reading_data():
    global stop_reading
    stop_reading = True

# Create the main window
root = tk.Tk()
root.title("COM Port Data Reader")

# Create a label to display data
data_label = tk.Label(root, text="Data: Waiting for data...")
data_label.pack(pady=20)

# Create a "Start" button to start reading data
start_button = tk.Button(root, text="Start Reading", command=read_and_display_data)
start_button.pack()

# Create a "Stop" button to stop reading data
stop_button = tk.Button(root, text="Stop Reading", command=stop_reading_data)
stop_button.pack()

# Create a frame for the temperature graph
temperature_frame = ttk.Frame(root)
temperature_frame.pack(pady=20)

# Create a Figure for the graph
fig, temperature_graph = plt.subplots(figsize=(5, 3), dpi=100)

# Create a canvas to embed the Figure
temperature_canvas = FigureCanvasTkAgg(fig, master=temperature_frame)
temperature_canvas.get_tk_widget().pack()

# Variable to control data acquisition
stop_reading = False

# Run the GUI
root.mainloop()
