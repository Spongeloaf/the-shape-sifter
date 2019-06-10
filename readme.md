# The Shape Sifter
The Shape Sifter is a lego sorting machine utilizing a neural network, image processing software, a conveyor belt, and air jets. The software is written in C++ and Python. 

A desktop PC runs the python program that watches the cpnveyor belt via a webcam. When a part passes the webcam, the Arduino begins to track it's movement along the conveyor belt. A Picture of the part is then passed to a neural network, which classififes it, and assigns it to a bin. Once the part passes in front of the bin, the Arduino activates a pneumatic valve, and blows the part into the bin.

Here is a link to video footage of the machine in action.

If you'd like to checkout the code, you can start with the server by looking in server.py, or chekout the conveyor belt controller code in belt_buckle_arduino.ino. If you have Visual Studio or ATmel Studio, you can open the .sln or .atsln files as well.

The Conveyor belt controller consists of two Arduinos. One is a Mega running the "Belt Buckle" software, and the other is an Uno running a rotary encoder program and connected to the conveyor belt. The encoder's only job is to report the conveyor belt's position over I2C, back to the Belt Buckle. Otherwise, the Belt Buckle does all of the part tracking, communicates with the server, activates the airjets, etc.

The Belt Buckle has 16 digital IO pins connected to MOSFETs which allow a 12VDC power supply to activate the airjets by driving the pins high. In theory, we could have many more bins, one for each IO pin, or possibly more using IO expanders. The Belt Buckle has other IO pins dedicated to controlling the feeder and conveyor belt. We can turn the feeder on and off, and control it's speed using PWM. We also have a relay connected to the conveyor belt motor. This only grants us on/off control, not speed. The speed of the belt is manually set by a knob on the belt motor. Achieving speed control is quite possible, but would require purchasing more hardware.

The LEDs in the box are powered by the 12VDC power supply which also powers the air jets, and the two arduinos.

The Server communicates with the belt buckle, but also is responsible for launching the other clients. The other clients are separate process and they pass around information via pipes. 

The webcam feed is analyzed a process known as the Taxidermist. The neural network, known as the MT_Mind, is another separate process. Finally, the process which assigns parts to their bins is the Classifist. You'll find their .py files in their respectively named folders.

The server maintains a list of part objects, which it passes to the various processes in sequence. Meanwhile, the belt buckle is also tracking the parts. This ensures the Belt Buckle always has a very precise measurement of each part's location on the belt.  Variations in conveyor belt speed or minor time delays on behalf of the server will not affect part tracking.

