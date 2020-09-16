# Pupil labs - Mocap trigger

Take Pupil player timestamp in accordance with start/stop of Vicon Nexus acquisition (also tested with Qualisys).

## Requirements

An Arduino Micro microcontroller, a Vicon server with sync out capabilities, a Windows 10 PC running Pupil labs 'Capture' software and Python 2.7 (not tested on Linux or Python 3).

## Instructions

Upload the Arduino sketch to your board. Connect an AV lead to a sync out on the Vicon server, and secure the other end to pin A0 on the Arduino. Connect the Arduino to your PC using a USB. In Nexus, set the corresponding sync out port to 'duration'. The server will then give a TTL voltage of 5V when an acquisition is started. 

Depending on which USB port the Arduino is connected to, you might have to edit line 49 in Trigger_Connect.py, for example, from serial.Serial('COM10', 115200) to serial.Serial('COM11', 115200). Also lines 12 and 28 for ip address.

The path to your pupil labs recordings will also need to be altered on line 70.

Open pupil labs capture and ensure the glasses are connected and everything is running. Run Trigger_Connect.py, start a Pupil capture recording, then start/stop a Vicon recording as appropriate. At the start and stop, a Pupil player timestamp will be taken and saved to the appropriate recording folder in a txt file (Mocap_timestamps.txt). If multiple Vicon recordings are made during the same Pupil player recording, the associated timestamps will be appended to the txt file. 

Check the round trip time for communication speed between Trigger_connect.py and pupil player. Use this to correct start/stop timestamps if more accuracy is needed -- the same for the Arduino. 

It is best to run Trigger_Connect.py from the command prompt as I have found IDEs like Spyder can result in unwanted behaviour.

## License

Pupil-Labs-Vicon-Trigger is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
