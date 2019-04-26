/*
 * EventDriver.h
 *
 * Created: 4/25/2019 4:34:54 PM
 *  Author: spongeloaf
 */ 



#include "PacketStruct.h"



#ifndef EVENTDRIVER_H_
#define EVENTDRIVER_H_


struct SerialPacket{};


// This controls our real time events and handles interaction between primary control interfaces.
class EventDriver {

	// There's a bit of non-conventionality in here.
	// Because we are working with meat-space machinery, we need to wait and continually check on certain procedures.
	// this includes things like turning air jets off after a few milliseconds, and waiting for feeder startup phases.
	// This is the only class that interacts directly with the other classes.

public:
	
	EventDriver(int num, int delay);
	
	void init_inputs();
	void check_inputs();
	void check_feeder();
	void check_distances();
	void check_encoder();


private:
	
	int num_inputs;									// used to initialize input arrays.
	bool encoder_stall;								// tracks status of encoder
	int debounce_delay;								// delay to wait for input changes
	unsigned long lastDebounceTime;					// for de-bouncing
	bool input_active[num_inputs];                  // stores the current state of each input - global
	bool input_previous_state;                      // default to true because pull up resistors invert our logic
	const int input_pins[num_inputs];				// array of input pin numbers.
};


EventDriver::EventDriver(int num, int delay)
	{
		encoder_stall = false;
		debounce_delay = delay;
		lastDebounceTime = 0;
		input_active[num];
		input_previous_state = true;
		num_inputs = num;
		
		input_pins[num_inputs] = {			// storing the pin numbers in an array is clever.
			4,								//  stick_up
			5,								//  stick_down
			6,								//  stick_left
			7,								//  stick_right
			8,								//  button_run
			9,								//  button_stop
			10,								//  button_belt,
			11								//  button_feeder,
		};
		init_inputs();
	}


void EventDriver::init_inputs()
{
	// setup our pins using a loop, makes it easier to add new pins
	for (int i = 0; i < num_inputs; i++)	
	{
		pinMode (input_pins[i], INPUT_PULLUP);
		input_active[i] = true;						// Remember that using internal pull-up resistors causes our true/false to be inverted!
	}
}


void EventDriver::check_inputs(){                                                                // check the state of all inputs

	 for (int i = 0; i < num_inputs; i++)                         // loop through the array of inputs
	 {
		 input_previous_state = input_active[i];                           // take the value from the previous loop and store it here
		 input_active[i] = digitalRead(input_pins[i]);                           // read the current input state
		 
		 if (input_active[i] == false) {                                   // false here means input is active because of pull-up resistors!
			 {
				 if (input_active[i] != input_previous_state)                  // checks if the state changed from our last trip through the loop
				 {
					 if ((millis() - lastDebounceTime) > debounce_delay)          // We use the number of milliseconds the arduino has been running for to see if it's been more than X number of millis since we last pressed a input It doesn't necessarily stop all input bouncing, but it helps.
					 {
						 lastDebounceTime = millis();                              // reset the debounce timer.
						 switch (i)                                                // take action if a input is pressed.
						 {
							 case stick_up:
							 feeder.speed_up();
							 Serial.print("speed: ");
							 Serial.println(feeder.get_speed());
							 break;
							 
							 case stick_down:
							 feeder.speed_down();
							 Serial.print("speed: ");
							 Serial.println(feeder.get_speed());
							 break;
							 
							 case stick_left:
							 belt.toggle_mode();
							 Serial.print("belt is: ");                         // replace this with a usable action at some point
							 Serial.println(belt.get_mode());
							 break;
							 
							 case stick_right:
							 feeder.toggle();
							 Serial.print("Mode: ");
							 Serial.print(feeder.get_mode());
							 Serial.print(" Speed: ");
							 Serial.println(feeder.get_speed());                         // replace this with a usable action at some point
							 break;

							 case button_run:
							 Serial.println("button_run");                         // replace this with a usable action at some point
							 break;

							 case button_stop:
							 Serial.println("button_stop");                        // replace this with a usable action at some point
							 break;

							 case button_belt:
							 Serial.println("button_belt");                         // replace this with a usable action at some point
							 break;

							 case button_feeder:
							 Serial.println("button_feeder");                         // replace this with a usable action at some point
							 break;


						 }
					 }
				 }
			 }
		 }
	 }
 }


void EventDriver::check_feeder()
{
	// updates the feeder start phase.
	if (feeder.get_startup())
	{
		feeder.start();
	}
}


void EventDriver::check_distances()
{
	// needs to be tested. Does not handle distance long rollover.
	int bin = 0;
	int check = 0;
	unsigned long current_dist = encoder.get_dist();
	unsigned long travel_dist = 0;
	
	// loop through the main part array
	for (unsigned int part = 0; part < index_length; part++)
	{
		// gets the bin assigned to part_array[part].
		bin = parts.get_bin(part);
		
		// skips unassigned parts.
		if (bin <= 0) continue;
		
		travel_dist = current_dist - parts.get_dist(part);
		
		// checks the distance of the part relative to the bin position.
		check = bins.check_past_bin(bin, travel_dist)
		
		switch (check)
		{
			case 1:
			// TODO: Add response to server of a successful sort.
			bins.on_airjet(bin);
			parts.flush_part_array(part);
			break;
			
			case -1:
			// TODO: Notify server that a part missed its' bin.
			parts.flush_part_array(part)
			break;
			
			case 0:
			{
				// Nothing to do, the part hasn't yet reached the bin.
				// This case only included for explicitness.
			}
			break:
		}
	}
}


void EventDriver::check_encoder()
{
	if (encoder.is_running()) return;
	
	// we are already aware that the encoder isn't running.
	if (encoder_stall)	return;
	
	// The encoder is not running, and we expect it to be.
	encoder_stall = true;
	// TODO: send server a warning message
}


void EventDriver::parse_packet(SerialPacket& packet){																					// parses the command and then passes the relevant data off to wherever it needs to go.

	
	server.validate_packet(packet);
	
	if (packet.result != 200)
	{
		server.throw_error(packet)
	}	

		
	// switch case for all the different command types.
	// see trello for a list of commands
	switch (packet.command)
	{
		case 'A':
			// Add a new part instance
			parts.add_part(packet);
			server.send_ack(packet);
		break;
			
		case 'B':
			// assign a bin number
			parts.assign_bin(packet);
			server.send_ack(packet);
		break;
		
		case 'G':
			// print current distance
			Serial.println(encoder.get_dist());
		break;
			
		case 'H':
			// handshake
			Serial.print("Command ");
			Serial.print(packet.command);
			Serial.println(" Received");
		break;

		case 'O':
			// flush index
			parts.flush_part_array(packet.argument_int);
			server.send_ack(packet);
		break;

		case 'X':
			// print part index
			// TODO
			Serial.println("TODO X");
		break;

		case 'P':
			// TODO: Most likely broken
			// print part index with bins and distance
			aprint.part_index_full();
		break;

		case 'S':
			// print part index
			// TODO
			Serial.println("TODO S");
		break;
			
		case 'T':
			// test cycle the outputs, argument is time in ms for each pulse
			bins.test_outputs(packet.argument_int);
		break;
			
		case 'W':
			//  TODO
			// Set feeder speed
			Serial.println("TODO W");
		break;
	}
}






#endif /* EVENTDRIVER_H_ */