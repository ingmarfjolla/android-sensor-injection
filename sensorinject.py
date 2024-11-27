# author: ingmarfjolla
# sourced from : https://github.com/umer0586/SensorServer/wiki/Connecting-to-Multiple-Sensors-Using-Threading-in-Python
# modifed to send console commands, and added more events.
import websocket
import json
import threading
import telnetlib
from time import sleep
import argparse 

parser = argparse.ArgumentParser(description="middleware to inject sensor data into emulator")
parser.add_argument("--port", type=int, default=5554, help="port for the emulator console, defaults to 5554")
args = parser.parse_args()

EMULATOR_HOST = "localhost"
EMULATOR_PORT = args.port

def send_console_command(command):
    try:
        with telnetlib.Telnet(EMULATOR_HOST, EMULATOR_PORT) as tn:
            tn.write(command.encode('ascii') + b"\n")
            response = tn.read_until(b"OK", timeout=1).decode('ascii')
            print(f"Sent: {command.strip()}, Response: {response.strip()}")
    except Exception as e:
        print(f"Failed to send command: {e}")

def on_accelerometer_event(values,timestamp):
    x = values[0]
    y = values[1]
    z = values[2]
    print(f"acclerometer values = {values}  timestamp = {timestamp}")
    command = f"sensor set acceleration {x}:{y}:{z}"
    send_console_command(command)

def on_gyroscope_event(values,timestamp):
    x = values[0]
    y = values[1]
    z = values[2]
    print(f"gyroscope values = {values}  timestamp = {timestamp}")
    command = f"sensor set gyroscope {x}:{y}:{z}"
    send_console_command(command)

def on_magnetic_field_event(values,timestamp):
    x = values[0]
    y = values[1]
    z = values[2]
    print(f"magnetic field values = {values}  timestamp = {timestamp}")
    command = f"sensor set magnetic-field {x}:{y}:{z}"
    send_console_command(command)

def on_light_event(values,timestamp):
    x = values[0]
    print(f"light values = {values}  timestamp = {timestamp}")
    command = f"sensor set light {x}"
    send_console_command(command)

## using a workaround using gravity sensor to set gyroscope values in emulator 
def on_gravity_event(values,timestamp):
    x = values[0]
    y = values[1]
    z = values[2]
    print(f"gravity values = {values}  timestamp = {timestamp}")
    command = f"sensor set gyroscope {x}:{y}:{z}"
    send_console_command(command)

def on_rotation_vector_event(values,timestamp):
    x = values[0]
    print(f"rotation vector values = {values}  timestamp = {timestamp}")
    #command = f"sensor set light {x}"
    #send_console_command(command)

def on_orientation_event(values,timestamp):
    x = values[0]
    y = values[1]
    z = values[2]
    print(f"orientation values = {values}  timestamp = {timestamp}")
    command = f"sensor set orientation {x}:{y}:{z}"
    send_console_command(command)

def on_gps_event(lat,long,lastKnownLocation,timestamp):
    print(f"gps values = {lat,long,lastKnownLocation}  timestamp = {timestamp}")
    #command = f"sensor set light {x}"
    #send_console_command(command)

class Sensor:
    
    def __init__(self,address,sensor_type, on_sensor_event):
        self.address = address
        self.sensor_type = sensor_type
        self.on_sensor_event = on_sensor_event
    
    def on_message(self,ws, message):
        if(self.sensor_type == "gps"):
            data = json.loads(message)
            print(data)
            lat , long = data["latitude"] , data["longitude"]
            lastKnownLocation = data["lastKnowLocation"]
            self.on_sensor_event(lat = lat,long=long,lastKnownLocation=lastKnownLocation, timestamp = timestamp)
        else:
            values = json.loads(message)['values']
            timestamp = json.loads(message)['timestamp']

        self.on_sensor_event(values = values, timestamp = timestamp)

    def on_error(self,ws, error):
        print("error occurred")
        print(error)

    def on_close(self,ws, close_code, reason):
        print(f"connection closed : {reason}")

    def on_open(self,ws):
        print(f"connected to : {self.address}")
        if(self.sensor_type == "gps"):
            while True:
                ws.send("getLastKnowLocation") # will trigger ws.onMessage
                sleep(0.1)


    def make_websocket_connection(self):
        if(self.sensor_type=="gps"):
            ws = websocket.WebSocketApp(f"ws://{self.address}/gps",
                        on_open=self.on_open,
                        on_message=self.on_message,
                        on_error=self.on_error,
                        on_close=self.on_close)
        else:
            ws = websocket.WebSocketApp(f"ws://{self.address}/sensor/connect?type={self.sensor_type}",
                                    on_open=self.on_open,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)

        # blocking call
        ws.run_forever()
    
    # make connection and start recieving data on sperate thread
    def connect(self):
        thread = threading.Thread(target=self.make_websocket_connection)
        thread.start() 

address = "localhost:8080"

Sensor(address = address, sensor_type="android.sensor.accelerometer", on_sensor_event=on_accelerometer_event).connect()
Sensor(address = address, sensor_type="android.sensor.gyroscope",on_sensor_event=on_gyroscope_event).connect()
Sensor(address = address, sensor_type="android.sensor.magnetic_field",on_sensor_event=on_magnetic_field_event).connect()

# Sensor(address = address, sensor_type="android.sensor.light",on_sensor_event=on_light_event).connect()
Sensor(address = address, sensor_type="android.sensor.gravity",on_sensor_event=on_gravity_event).connect()

################################# not supported to set in emulator ################################
# Sensor(address = address, sensor_type="android.sensor.linear_acceleration",on_sensor_event=on_linear_acceleration_event).connect()
# Sensor(address = address, sensor_type="android.sensor.rotation_vector",on_sensor_event=on_rotation_vector_event).connect()
###################################################################################################

Sensor(address = address, sensor_type="android.sensor.orientation",on_sensor_event=on_orientation_event).connect()

#### GPS from device not working, ignroing for now
#Sensor(address = address, sensor_type="gps",on_sensor_event=on_gps_event).connect()