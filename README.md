# The Shape Sifter
The Shape Sifter is a lego sorting machine utilizing a neural network, image processing software, a conveyor belt, and air jets. The software is written in C++ and Python. 

As you can see, it's majesty is outmatched only by it's imposing size:


![In all her glory](https://i.imgur.com/L0vfOT7.jpg)


A screenshot of the UI:


![UI screenshot](https://i.imgur.com/bcjGmLM.png)

Here are a few videos of the machine, for the unbelievers:

Video 1: [A quick look at the hardware](INSERT VIDEO HERE)

Video 2: [The sorting machine in action](https://www.youtube.com/watch?v=0VHN3AZKY0E)

Development blog: https://mt_pages.silvrback.com


## Under the hood

If you'd like to checkout the code, you can start with the server by looking in `server.py`, or chekout the conveyor belt controller code in `\\belt_buckle_arduino\belt_buckle_arduino.ino`. If you have ATmel Studio, you can open the solution file `\\belt_buckle_arduino\belt_buckle_arduino.atsln` as well.


## Dependencies

* [Opencv](https://opencv.org) - Image and video manipulation library
* [Fast.ai](https://www.fast.ai/) - Neural network framework built on Pytorch
* [Arduino](https://www.arduino.cc/) - Open source hardware and software project for embedded devices
* [Encoder](https://www.pjrc.com/teensy/td_libs_Encoder.html) Library - Arduino library for reading data from rotary encoders
* [Pyserial](https://github.com/pyserial/pyserial) - Serial communication library for python.
* [QT](https://www.qt.io/) - UI authoring suite

Plus a few common python modules such as time, multiprocessing, etc.


## Want to build one yourself?

This project requires a significant hardware investment, so I don't expect many people to try running this on their own. If you do however, I will gladly share as much information and documentation as I can. I will not, however, be able to troubleshoot your hardware setup. The project also depends on some config and resource files which are not on github. Send me a message if you need them.

In theory, you could run the program substituting a video file instead of a webcam and leave out the air jets and conveyor belt. 

## License

[AGPL-3.0-or-later](https://choosealicense.com/licenses/agpl-3.0/#). This code comes with no warranty, liabillities, or guarantees of any sort. Use at your own risk.

## How does it work?

A desktop PC runs the python program that watches the conveyor belt via a webcam. When a part passes the webcam, the Arduino begins to track it's movement along the conveyor belt. A Picture of the part is then passed to a neural network, which classififes it, and assigns it to a bin. Once the part passes in front of the bin, the Arduino activates a pneumatic valve, and blows the part into the bin.

The Conveyor belt controller consists of two Arduinos. One is a Mega running the "Belt Buckle" software, and the other is an Uno running a rotary encoder program and connected to the conveyor belt. The Belt Buckle does all of the part tracking, communicates with the server, activates the airjets, etc, and the Encoder reports the conveyor belt distance via I2C.

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

Once part has been sorted into its bin, or if it runs off of the belt before it is assigned to a bin, the Belt Buckle will notify the server. The part is removed from the active part list, and added to a sorting log.
