# android-sensor-injection

Small middleware written as part of research into emulation detection. This functions similarly (according to their docs) to genymotions [Device Link](https://docs.genymotion.com/desktop/04_Emulating_sensors_and_features/#device-link) feature that lets you stream a real device's sensor data connected over ADB's into the emulators sensor data. Since Android studios emulator doesn't support this natively I wrote this up. 

This uses [SensorServer](https://github.com/umer0586/SensorServer) to stream live sensor data over adb and then feeds the data into the emulator using the android [emulator console](https://developer.android.com/studio/run/emulator-console).

## pre-requisites
- ADB and other android [tools](https://developer.android.com/studio) 
- Install [SensorServer](https://github.com/umer0586/SensorServer) on your android device and enable the `local host` option in the app. 
- python environment set up with [websocket-client](https://pypi.org/project/websocket-client/) installed

## usage
- start the SensorServer app on your phone and start the server
- run `adb forward tcp:8080 tcp:8080` on your machine that the device is connected to over USB 
- start your emulator(s) and keep note of the port number (usually defaults to 5554)
- if this is your first time connecting to the emulators console, I would first run `telnet localhost <emulatorport>` and then make sure to delete the data in auth token located in `.emulator_console_auth_token` so that it's empty. Since this script doesn't support connecting with an auth token that is mandatory.
- run `python sensorinject.py --port <emulator-port>` and you should be streaming data! you can drop the `--port <emulator-port>` option if your port is 5554 since that is the default in the script. 

> **_NOTE:_**  Since my device didn't support gyroscope, I fed in the `android.sensor.gravity` sensor. You can modify the script depending on what sensors you do/don't have. 

## demo

![Alt Text](/demo.gif)