# Pupil Labs - Mocap Trigger

Use a low-cost Arduino microcontroller to synchronise motion Capture systems (e.g. Vicon/Qualisys)
with the Pupil Core Mobile eye tracker. Temporal accuracy currently ~1 ms

## Theory

The Arduino is setup to listen to a mocap sync-out port. Typically, these ports can deliver a specific 
voltage depending on recording state. In this case:

- ~0.2V: **not** recording
- ~5.0V: **is** recording

When the voltage is above or below 3.5, the arduino sends a single character, 'h' or 'l', respectively,
via serial port to the connected PC. The python scripts listen to the serial port. A change 
between states is interpreted as a trigger, at which point a timestamp from Pupil Capture (or from the PC 
clock depending on which script is run) is recorded. The timestamp can be stored in the Pupil Capture 
recording folder for post-hoc synchronisation, or sent to the Pupil Capture Annotation Plugin, where it 
will appear as a 'start' or 'stop' annotation when the recording is played back in Pupil Player. 

An average oneway trip duration from the Arduino to PC was measured at ~0.5 ms. Therefore, 0.5 ms is deducted 
from the timestamp to account for latency. This can easily be changed if required. In the next version, 
real time clock (RTC) functionality will be added to the Arduino so that timestamps can be taken directly from 
the Arduino, which will improve temporal accuracy.
 
### Clock sync method

annotations_wclock_sync and timestamps_wclock_sync attempt to synchronise the Pupil Capture time base with that of
the PC using:

	socket.send_string("T {}".format(time())) 

Due to variations in the speed of the connection, sync_clocks and test_sync functions are used to 
recursively set and test the sync  until a required threshold (e.g. <0.01ms) is achieved. All time stamps on 
trigger input are then taken from the PC clock.

- **Pros**: This method is stable when the eye tracker is connected to the PC via USB. 
- **Cons**: When connected using the Pupil Remote android app, updating the Pupil Capture clock with socket.send_string("T {}".format(time()))
seems not to always update the Pupil remote clock. When this happens a Pupil recording is not possible. I had
to re-run the Python script a few times to resolve this


### Pupil Capture timestamp method
annotations and pupil_remote_timestamps do not rely on the PC clock. Rather, all time stamps on trigger input 
are taken from the Pupil Capture time base. In this method, each oneway trip duration is recorded and deducted from
the timestamp to account for latency:

	t1 = time()
    socket.send_string('t')
    pct = socket.recv()
    t2 = time()
    oneway_dur = (t2-t1) / 2
    corrected_pct = float(pct.decode()) - oneway_dur
	
- **Pros**: In theory this should achieve the same accuracy as the clock sync methods, and is robust when used with
Pupil Remote.

## Requirements

1. Arduino Micro microcontroller
2. Mocap server with sync out capabilities
3. Windows 10 PC running Pupil Labs 'Capture' and Python 3

## Instructions
### Arduino

Make a new sketch in [Arduino Create](https://create.arduino.cc/) using Trigger.io. Connect Arduino 
to PC via a USB. Verify and upload the sketch. Check the Sketch is running okay by opening the Monitor 
in Arduino Create. You should see 'l' repeating. 

Connect an AV lead to the sync-out port on the mocap server, and secure the other end to pin A0 on the 
Arduino. Connect the Arduino to your PC via USB.

### Mocap
In the mocap software (e.g. Vicon Nexus), set the corresponding sync-out port to 'duration'. The server 
will then provide ~0.2V when not recording, and ~5.0V when an acquisition is started.

### Python
In all scripts, change the IP and Port to connect to Pupil Capture. Pupil Capture's
local IP address and Port can be found in Pupil Capture software under the Network API plugin. 

For timestamps and timestamps_wclock_sync, modify the path variable to point to your recording directory. 

### Ready to go?

1. Open Pupil Capture and ensure the glasses are connected and everything is running
2. Ensure Arduino is connected to PC and mocap server
3. Run desired script and wait for 'Ready to start/stop mocap acquisition...'.
Watch out for errors
4. Calibrate your participant and start a Pupil Capture recording
5. Start/stop a Vicon recording as appropriate.
6. **Important:** Use Ctrl+c to escape a script and close sockets (disconnecting the usb should also be fine)

For timestamps and timestamps_wclock_sync, time stamps will be stored in the recording folder in a 
txt file (Mocap_timestamps.txt). If multiple mocap acquisitions are made during the same Pupil Capture 
recording, the associated timestamps will be appended to the txt file.

For annotations and annotations_wclock_sync, time stamps will be stored in the recording annotation file.
These can be viewed in Pupil Player and exported as csv file.

It may be best to run the scripts from the command prompt as I have found IDEs like Spyder can result in unwanted behaviour.

## License

Pupil-Labs-Mocap-Trigger is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.

## Citation

Citation option if you find this useful...

Thomas, NM. (2020) Github repository, https://github.com/n-m-t/Pupil-Labs-Mocap-Trigger, https://doi.org/10.5281/zenodo.4032375 


[![DOI](https://zenodo.org/badge/190172285.svg)](https://zenodo.org/badge/latestdoi/190172285)


