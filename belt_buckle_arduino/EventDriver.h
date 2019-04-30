/*
 * EventDriver.h
 *
 * Created: 4/25/2019 4:34:54 PM
 *  Author: spongeloaf
 */ 




#ifndef EVENTDRIVER_H_
#define EVENTDRIVER_H_
#include "bb_parameters.h"
#include "FeederController.h"
#include "BinController.h"
#include "BeltController.h"
#include "ArrayPrint.h"
#include "PartTracker.h"
#include "EncoderController.h"



extern BinController		bins;
extern ArrayPrint			aprint;
extern PartTracker			parts;
extern FeederController		feeder;
extern BeltController		belt;
extern EncoderController	encoder;
extern SerialPacket			packet;



// This controls our real time events and handles interaction between primary control interfaces.
class EventDriver{
	
	// There's a bit of non-conventionality in here.
	// Because we are working with meat-space machinery, we need to wait and continually check on certain procedures.
	// this includes things like turning air jets off after a few milliseconds, and waiting for feeder startup phases.
	// This is the only class that interacts directly with the other classes.

public:
	
	EventDriver()
	{
		encoder_stall = false;
		lastDebounceTime = 0;
		input_active[num_inputs];
		input_previous_state = true;
		init_inputs();
	};
	
	void init_inputs();
	void check_inputs();
	void check_feeder();
	void check_distances();
	void check_encoder();
	void send_ack(SerialPacket&);
	void parse_command(char*);
	void construct_packet(char*);
	void read_serial_port();


private:
	
	bool encoder_stall;							// tracks status of encoder
	unsigned long lastDebounceTime;				// for de-bouncing
	bool input_previous_state;					// default to true because pull up resistors invert our logic
	int  serial_str_index;						// the current index number of the read string
	char serial_str[serial_str_len];			// stores the read chars.
	char serial_char;							// the most recent char read from serial port

};


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
		check = bins.check_past_bin(bin, travel_dist);
		
		switch (check)
		{
			case 1:
			// TODO: Add response to events of a successful sort.
			bins.on_airjet(bin);
			parts.flush_part_array(part);
			break;
			
			case -1:
			// TODO: Notify events that a part missed its' bin.
			parts.flush_part_array(part);
			break;
			
			case 0:
			{
				// Nothing to do, the part hasn't yet reached the bin.
				// This case only included for explicitness.
			}
			break;
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
	// TODO: send events a warning message
}


void EventDriver::send_ack(SerialPacket& packet){
	Serial.print("[ACK-");
	Serial.print(packet.command);
	Serial.print("-");
	Serial.print(packet.result);
	Serial.print("-");
	Serial.print(packet.payload);
	Serial.print("-");
	Serial.print("CSUM");
	Serial.println("]");
}


void EventDriver::parse_command(char* packet_string){					// parses the command and then passes the relevant data off to wherever it needs to go.

	extern SerialPacket packet;
	
	construct_packet(packet_string);
	
	/*
	// for debugging
	Serial.println(packet.argument_arr);
	Serial.println(packet.argument_int);
	Serial.println(packet.command);
	Serial.println(packet.payload);
	Serial.println(packet.raw_default);
	Serial.println(packet.raw_packet);
	Serial.println(packet.result);
	*/
	
	if (packet.result != 200)
	{
		send_ack(packet);
		construct_packet(packet.raw_default);							// If a packet is malformed, reset all values to default.
		return;
	}

	
	// switch case for all the different command types.
	// see trello for a list of commands
	switch (packet.command)
	{
		case 'A':
		// Add a new part instance
		parts.add_part(packet, encoder.get_dist());
		send_ack(packet);
		break;
		
		case 'B':
		// assign a bin number
		parts.assign_bin(packet);
		send_ack(packet);
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
		send_ack(packet);
		break;

		case 'X':
		// print part index
		// TODO
		Serial.println("TODO X");
		break;

		case 'P':
		Serial.println("TODO P");
		// TODO: Most likely broken
		// print part index with bins and distance
		//aprint.part_index_full();
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
		
		default:
			packet.result = 406;	// 406: bad command
			send_ack(packet);
		break;
	}
	// We're finished with the packet, reset all values to default.
	construct_packet(packet.raw_default);
}


void EventDriver::construct_packet(char* packet_str)
{
	// If a packet string is syntactically correct, this function copies it into the correct parts of a packet struct.
	
	// ------------TODO: Needs to have CSUM installed HERE------------
	
	extern SerialPacket packet;
	
	// check str len
	if (strlen(packet_str) != packet_length)
	{
		packet.result = 401;		// 401 = bad length
		return;
	}
	
	for (int i = 0; i < strlen(packet_str); i++)
	//for (int i : strlen(packet.raw_packet))
	{
		packet.raw_packet[i] = packet_str[i];
	}
	
	// setup command
	packet.command = packet_str[1];
	
	// sets up the argument array
	for (int i = 0; i <= argument_length - 2; i++)              // argument length -2, because the last character is \0 and we are zero indexed
	{
		packet.argument_arr[i] = packet_str[i + 2];             //  the argument begins on the [2] char
	}
	packet.argument_arr[4] = '\0';                              // don't forget the terminator on the array!
	packet.argument_int = atoi(packet.argument_arr);			// the bin number is more useful as an int than an array. But now we have both.

	// sets up the payload array
	for (int i = 0; i <= payload_length - 2; i++)               // payload length -2, because the last character is \0 and we are zero indexed
	{
		packet.payload[i] = packet_str[i + 6];                  //  the argument begins on the [2] char
	}
	packet.payload[payload_length - 1] = '\0';
	
	// TODO: insert more thorough command and argument checking here
	
	packet.result = 200;  // 200 packet syntax is OK.
}


void EventDriver::read_serial_port(){

	// abort if there's nothing to read.
	if (Serial.available() == 0)
	{
		return;
	}
	
	serial_char = Serial.read();                                        //  Read a character
	
	switch (serial_char)
	{
		case '<':												// '<' is the packet initiator.
			memset(&serial_str[0], 0, sizeof(serial_str));		// clear the array every time we get a new initiator.
			serial_str_index = 0;                               // reset the array index because we're starting a new command.
			serial_str[0] = serial_char;                        // place our '<' character at the beginning of the array
			serial_str_index = serial_str_index + 1;			// increment array index number
		
			// print_array(serial_read_string);                              // for debugging
			// Serial.println("packet initiator found");                     // for debugging
		break;
				
		case '>':								                // '>' is the packet terminator.
			serial_str[serial_str_index] = serial_char;			// add the terminator to the string before we begin
			parse_command(serial_str);                          // executes the received packet
			memset(&serial_str[0], 0, sizeof(serial_str));		// clear the array every time we get a new initiator.
			serial_str_index = 0;                               // reset the packet array index to 0
		
			// Serial.println(strlen(serial_read_string));                   // for debugging
			// print_array(serial_read_string);                              // for debugging
			// Serial.println("packet terminator found");                    // for debugging
		break;
		
		default:
			// check to make sure were not too long
			if (serial_str_index < (sizeof(serial_str) - 2))    
			{
				serial_str[serial_str_index] = serial_char;     // append the read character to the array
				serial_str_index = serial_str_index + 1;        // increment the array index number
			}
		
			// should we receive more than 22 characters before a terminator, something is wrong, dump the string
			else                                                
			{
				memset(&serial_str[0], 0, sizeof(serial_str));  
				serial_str_index = 0;                           // reset the array index because we're starting a new command.
			}
		break;
	}
}



#endif /* EVENTDRIVER_H_ */