# Pupil labs - Vicon trigger

Stop/start a Pupil Labs recording in accordance with a Vicon Nexus acquisition

## Requirements

An Arduino Micro microcontroller, a Vicon server with sync out capabilities, a PC running Pupil labs 'Capture' software, Python 2.7 (not tested on Python 3)

## Instructions

Upload the Arduino sketch to your board. Connect an AV lead to a sync out on the Vicon server, and secure the other end to pin A0 on the Arduino. Connect the Arduino to your PC using a USB. In Nexus, set the corresponding sync out port to 'duration'. The server will then give a TTL voltage of 5V when an acquisition is started. Open pupil labs capture and ensure the glasses are connected and everything is running. Finally, run Trigger_Connect.py

Depending on which USB port the Arduino is connected to, you might have to edit line 45 in Trigger_Connect.py, for example, from serial.Serial('COM10', 115200) to serial.Serial('COM11', 115200). 

## License

Pupil-Labs-Vicon-Trigger is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
