# The Shape Sifter
The Shape Sifter is a lego sorting machine utilizing a neural network, image processing software, a conveyor belt, and air jets. The software is written in C++ and Python. 

As you can see, it's majesty is outmatched only by it's mass:
![In all her glory](https://i.imgur.com/L0vfOT7.jpg)

A screenshot of the UI:
![UI screenshot](https://i.imgur.com/bcjGmLM.png)

Here are a few videos of the machine, for the unbelievers:

Video 1: [A quick look at the hardware](!!!!! INSERT VIDEO HERE !!!!!!!)

Video 2: [The sorting machine in action](https://www.youtube.com/watch?v=0VHN3AZKY0E)

And of course we've kept a blog of our progress here: https://mt_pages.silvrback.com

### How does it work?

A desktop PC runs the python program that watches the cpnveyor belt via a webcam. When a part passes the webcam, the Arduino begins to track it's movement along the conveyor belt. A Picture of the part is then passed to a neural network, which classififes it, and assigns it to a bin. Once the part passes in front of the bin, the Arduino activates a pneumatic valve, and blows the part into the bin.

Here is a link to video footage of the machine in action.

If you'd like to checkout the code, you can start with the server by looking in server.py, or chekout the conveyor belt controller code in belt_buckle_arduino.ino. If you have Visual Studio or ATmel Studio, you can open the .sln or .atsln files as well.

The Conveyor belt controller consists of two Arduinos. One is a Mega running the "Belt Buckle" software, and the other is an Uno running a rotary encoder program and connected to the conveyor belt. The Belt Buckle does all of the part tracking, communicates with the server, activates the airjets, etc, and the Encoder reports the conveyor blet distance via I2C.

The Belt Buckle has 16 digital IO pins connected to MOSFETs which allow a 12VDC power supply to activate the airjets. The Belt Buckle has other IO pins dedicated to controlling the feeder and conveyor belt. We can turn the feeder on and off, and control it's speed using PWM. We also have a relay connected to the conveyor belt allowing us start/stop control.

The conveyor and the part feeder can both be turned off and on via a joystick connected to the belt buckle, or commands from the server.

The LEDs in the box are powered by the 12VDC power supply which also powers the air jets, and the two arduinos.

The Server communicates with the belt buckle over a serial port, but it's also is responsible for launching and coordinating the other processes. These processes are as follows:

* Taxidermist - Captures pictures of parts via the webcam and trims/crops/formats them appropriately.
* MT Mind - A neural network that is trained to identify lego parts from pictures
* Classifist - Decides which bin each part belongs in
* SUIP - (Sorting User Interface Program) A graphical UI for operating the machine

The processes exchange information with the server via pipes. You'll find their .py files in their respectively named folders.

The server maintains a list of part objects, which it passes to the various processes in sequence. Meanwhile, the belt buckle is also tracking the parts. This ensures we have a very precise measurement of each part's location on the belt. Variations in conveyor belt speed or minor time delays on behalf of the server will not affect part tracking.

Once part has been sorted into its bin, or if runs off of the belt before it is assigned to a bin, the Belt Buckle will notify the server. The part is removed from the active part list, and added to a sorting log.
