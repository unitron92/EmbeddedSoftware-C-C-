import serial
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

# Define the COM port and baud rate
com_port = 'COM1'  # Change this to your COM port
baud_rate = 115200  # Change this to match your device's baud rate

# Lists to store temperature data for the graph
temperature_data = []
time_data = []

# Serial port object
ser = None

# Create a function to read and display data
def read_and_display_data():
    global ser
    try:
        ser = serial.Serial(com_port, baud_rate)
        data_label_var.set("Reading data...")
        start_time = datetime.now()
        prev_temperature = None  # To track the previous temperature reading
        light_and_fan_on = False  # Flag to track if light and fan are turned on

        def update_data():
            nonlocal prev_temperature, light_and_fan_on

            if not stop_reading:
                try:
                    data = ser.readline().decode('utf-8').strip()

                    if "Error Rx" in data:  # Check for Error Rx message
                        data_label_var.set("Error Rx in UART")
                    else:
                        # Extract the numeric part (temperature value) from the string
                        temperature_str = data.split(' ')[0]
                        temperature = float(temperature_str)

                        formatted_temperature = "{:.2f}".format(temperature)  # Format to 2 decimal places

                        # Check if the temperature is increasing or decreasing
                        if prev_temperature is not None:
                            color = 'red' if temperature > prev_temperature else 'blue'
                        else:
                            color = 'black'

                        # Check if temperature is above 27°C
                        if temperature > 27 and not light_and_fan_on:
                            light_and_fan_on = True
                            fan_label_var.set("FAN is TURN ON")

                        # Update the graph with the appropriate color
                        temperature_graph.plot(time_data, temperature_data, label='Temperature (°C)', color=color)
                        prev_temperature = temperature  # Update previous temperature
                        data_label_var.set(f"Data: Temperature: {formatted_temperature} °C")

                        temperature_data.append(temperature)
                        time_data.append((datetime.now() - start_time).total_seconds())

                        # Set the y-axis range for the temperature values (adjust min and max as needed)
                        temperature_graph.set_ylim(20, 30)

                        temperature_canvas.draw()

                        # Update circular indicator and fan label
                        if temperature > 27:
                            canvas.create_oval(100, 100, 150, 150, fill="red", outline="red", tags="indicator")
                        else:
                            canvas.create_oval(100, 100, 150, 150, fill="blue", outline="blue", tags="indicator")
                            fan_label_var.set("FAN is TURN OFF")

                except (serial.SerialException, ValueError) as e:
                    data_label_var.set(f"Error: {e}")
                    return

                root.after(200, update_data)  # Schedule the next update after 200 milliseconds

        # Start the update loop
        update_data()

    except serial.SerialException as e:
        data_label_var.set(f"Error: {e}")

# Create a function to stop reading data
def stop_reading_data():
    global stop_reading, ser
    stop_reading = True

    # Close the serial port
    if ser and ser.is_open:
        ser.close()
        ser = None

# Create a function to start reading data
def start_reading_data():
    global stop_reading
    stop_reading = False
    read_and_display_data()

# Create the main window
root = tk.Tk()
root.title("COM Port Data Reader")

# Create a frame for the header
header_frame = ttk.Frame(root)
header_frame.pack(pady=10)

# Create a label for the header
header_label = ttk.Label(header_frame, text="Temperature Monitoring System", font=("Helvetica", 16))
header_label.pack()

# Create a frame for the temperature graph
temperature_frame = ttk.Frame(root)
temperature_frame.pack(pady=10)

# Create a Figure for the graph
fig, temperature_graph = plt.subplots(figsize=(7, 4), dpi=100)

# Create a canvas to embed the Figure
temperature_canvas = FigureCanvasTkAgg(fig, master=temperature_frame)
temperature_canvas.get_tk_widget().pack()

# Create a frame for the circular indicator and fan label
indicator_frame = ttk.Frame(root)
indicator_frame.pack(pady=10)

# Create a Canvas widget for the circular indicator
canvas = tk.Canvas(indicator_frame, width=200, height=200)
canvas.pack(side=tk.LEFT, padx=10)

# Create a label to display fan status
fan_label_var = tk.StringVar()
fan_label_var.set("FAN is TURN OFF")
fan_label = ttk.Label(indicator_frame, textvariable=fan_label_var)
fan_label.pack(side=tk.LEFT)

# Create a frame for the data label and control buttons
control_frame = ttk.Frame(root)
control_frame.pack(pady=10)

# Create a label to display data
data_label_var = tk.StringVar()
data_label_var.set("Data: Waiting for data...")
data_label = ttk.Label(control_frame, textvariable=data_label_var)
data_label.pack(pady=5)

# Create start and stop buttons
start_button = ttk.Button(control_frame, text="Start", command=start_reading_data)
start_button.pack(side=tk.LEFT, padx=10)
stop_button = ttk.Button(control_frame, text="Stop", command=stop_reading_data)
stop_button.pack(side=tk.LEFT)

# Variable to control data acquisition
stop_reading = False

# Function to release port and close the window when the window is closed
def on_closing():
    global ser
    if ser and ser.is_open:
        ser.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Run the GUI
root.mainloop()
