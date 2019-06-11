# The Shape Sifter
The Shape Sifter is a lego sorting machine utilizing a neural network, image processing software, a conveyor belt, and air jets. The software is written in C++ and Python. 

A desktop PC runs the python program that watches the cpnveyor belt via a webcam. When a part passes the webcam, the Arduino begins to track it's movement along the conveyor belt. A Picture of the part is then passed to a neural network, which classififes it, and assigns it to a bin. Once the part passes in front of the bin, the Arduino activates a pneumatic valve, and blows the part into the bin.

Here is a link to video footage of the machine in action.

If you'd like to checkout the code, you can start with the server by looking in server.py, or chekout the conveyor belt controller code in belt_buckle_arduino.ino.

The Conveyor belt controller consists of two Arduinos. One is a Mega running the Belt_Buckle software, and the other is an Uno running a rotary encoder program and connected to the conveyor belt. The encoder's only job is to report the conveyor belt's position over I2C. Otherwise, the Belt Buckle does all of the part tracking, communicates with the server, activates the airjets, etc.
