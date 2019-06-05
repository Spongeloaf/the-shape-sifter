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
class EventDriver {

	// There's a bit of non-conventionality in here.
	// Because we are working with meat-space machinery, we need to wait and continually check on certain procedures.
	// this includes things like turning air jets off after a few milliseconds, and waiting for feeder startup phases.
	// This is the only class that interacts directly with the other classes.

public:

	EventDriver()
	{
		encoder_stall = false;
		lastDebounceTime = 0;
		input_active[gp::num_inputs];
		input_previous_state = true;
		init_inputs();
	};

	void init_inputs();
	void check_inputs();
	void check_feeder();
	void check_distances();
	void check_encoder();
	void check_airjets();
	void send_ack(SerialPacket&);
	void parse_command(char*);
	void construct_packet(char*);
	void read_serial_port();
	void tick_perf_timer();
	void start_perf_timer();
	void stop_perf_timer();
	void toggle_perf_timer();
	void set_param(SerialPacket&);


private:

	bool encoder_stall;							// tracks status of encoder
	unsigned long lastDebounceTime;				// for de-bouncing
	bool input_previous_state;					// default to true because pull up resistors invert our logic
	int  serial_str_index;						// the current index number of the read string
	char serial_str[gp::serial_str_len];			// stores the read chars.
	char serial_char;							// the most recent char read from serial port
	unsigned long loop_count = 0;				// used by the performance timer to track the number of loops the software has done.
	bool timer_mode = false;					// turns the performance timer on and off.
	bool input_active[gp::num_inputs];				// stores the current state of each input - global

	//  input name enum for readability
	enum input_enum {
		stick_up,
		stick_down,
		stick_left,
		stick_right,
		button_1,
		button_2,
		button_3,
		button_4
	};

	int input_pins[gp::num_inputs] = {			// storing the pin numbers in an array is clever.
		6,								//  stick_up
		7,								//  stick_down
		8,								//  stick_left
		9,								//  stick_right
		10,								//  button_1
		11,								//  button_2
		12,								//  button_3,
		13								//  button_4,
	};

};

void EventDriver::init_inputs()
{
	// setup our pins using a loop, makes it easier to add new pins
	for (int i = 0; i < gp::num_inputs; i++)	
	{
		pinMode (input_pins[i], INPUT_PULLUP);
		input_active[i] = true;						// Remember that using internal pull-up resistors causes our true/false to be inverted!
	}
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


void EventDriver::check_inputs(){                                                                // check the state of all inputs

	 for (int i = 0; i < gp::num_inputs; i++)                         // loop through the array of inputs
	 {
		 input_previous_state = input_active[i];                           // take the value from the previous loop and store it here
		 input_active[i] = digitalRead(input_pins[i]);                           // read the current input state
		 
		 if (input_active[i] == false) {                                   // false here means input is active because of pull-up resistors!
			 {
				 if (input_active[i] != input_previous_state)                  // checks if the state changed from our last trip through the loop
				 {
					 if ((millis() - lastDebounceTime) > gp::debounce_delay)          // We use the number of milliseconds the arduino has been running for to see if it's been more than X number of millis since we last pressed a input It doesn't necessarily stop all input bouncing, but it helps.
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

							 case button_1:
							 Serial.println("button_run");                         // replace this with a usable action at some point
							 break;

							 case button_2:
							 Serial.println("button_stop");                        // replace this with a usable action at some point
							 break;

							 case button_3:
							 Serial.println("button_belt");                         // replace this with a usable action at some point
							 break;

							 case button_4:
							 Serial.println("button_feeder");                         // replace this with a usable action at some point
							 break;


						 }
					 }
				 }
			 }
		 }
	 }
 }


void EventDriver::check_distances()
{
	// needs to be tested. Does not handle distance long rollover.
	// TODO: Make this handle distance rollover. Should happen after ~30 minutes of operation.
	
	int bin = 0;
	int check = 0;
	unsigned long current_dist = encoder.get_dist();
	unsigned long travel_dist = 0;
	
	// loop through the main part array
	for (unsigned int part = 0; part < gp::part_list_length; part++)
	{
		// skips unassigned part slots.
		if (parts.get_occupied(part) == false)
		{
			continue;
		}
		
		// gets the bin assigned to part_list[part].
		bin = parts.get_bin(part);
		
		travel_dist = current_dist - parts.get_dist(part);
		
		// checks the distance of the part relative to the bin position.
		check = bins.check_past_bin(bin, travel_dist);
		
		// checks the distance of the part relative to the bin position.
		if (bins.check_past_bin(bin, travel_dist) == false)
		{
			// part has not arrived at the bin yet, do nothing.
			continue;
		}

		// remember that we only reach this logic if the part is in front of it's bin or off the end of the belt.
		
		// normal sort, TEL sorted.
		if (parts.get_assigned(part))
		{
			bins.on_airjet(bin);
			parts.tel_server_sorted(part);
		}
							
		// Otherwise, TEL lost. The part has gone off the end of the belt.
		else
		{
			parts.tel_server_lost(part);
		}
							
		parts.free_part_slot(part);
	}
}


void EventDriver::check_feeder()
{
	// updates the feeder start phase.
	if (feeder.get_delayed())
	{
		feeder.start_delayed(gp::feeder_delay);
		return;
	}
	
	if (feeder.get_startup())
	{
		feeder.start();
	}
}


void EventDriver::check_encoder()
{
	// TODO: Figure out why this doesn't work
	
	if (encoder.is_running()) return;
	
	// we are already aware that the encoder isn't running.
	if (encoder_stall)	return;
	
	// The encoder is not running, and we expect it to be.
	encoder_stall = true;
	// TODO: send events a warning message
}


void EventDriver::check_airjets()
{
	bins.off_airjets();
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
	Serial.print("]");
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
		
		case 'M':
		// set parameter
		set_param(packet);
		send_ack(packet);
		break;

		case 'O':
		// flush index
		parts.remove_part(packet);
		send_ack(packet);
		break;

		case 'X':
		// print part index
		// TODO
		Serial.println("TODO X");
		break;

		case 'P':
		parts.print_part_list(packet.argument_int);
		break;

		case 'S':
		// print part index
		// TODO
		Serial.println(encoder.get_sim());
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
	if (strlen(packet_str) != gp::packet_length)
	{
		packet.result = 401;		// 401 == bad length
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
	for (int i = 0; i <= gp::argument_length - 2; i++)              // argument length -2, because the last character is \0 and we are zero indexed
	{
		packet.argument_arr[i] = packet_str[i + 2];             //  the argument begins on the [2] char
	}
	packet.argument_arr[4] = '\0';                              // don't forget the terminator on the array!
	packet.argument_int = atoi(packet.argument_arr);			// the bin number is more useful as an int than an array. But now we have both.

	// sets up the payload array
	for (int i = 0; i <= gp::payload_length - 2; i++)               // payload length -2, because the last character is \0 and we are zero indexed
	{
		packet.payload[i] = packet_str[i + 6];                  //  the argument begins on the [2] char
	}
	packet.payload[gp::payload_length - 1] = '\0';
	
	// convert payload to int, if possible. Remember that a failed conversion returns 0!
	if (isdigit(packet.payload[0]) || packet.payload[0] == '-')
	{
		packet.payload_int = atol(packet.payload);	
	}
	else packet.payload_int = -1;
	
	// TODO: insert more thorough command and argument checking here.
	// It would be nice to change atoi() and atol() to functions which indicate whether or not there was a failure to interpret an int from an array.
	
	packet.result = 200;  // 200 == packet syntax is OK.
}


void EventDriver::tick_perf_timer()
{
	if (!(timer_mode)) return;
	
	if (loop_count > 100000)
	{
		loop_count = 0;
		Serial.print("100k loops: ");
		Serial.print(millis());
		Serial.println("ms");
	}
	loop_count++;
}


void EventDriver::start_perf_timer()
{
	timer_mode = true;
}


void EventDriver::stop_perf_timer()
{
	timer_mode = false;
}


void EventDriver::toggle_perf_timer()
{
	(timer_mode) ? stop_perf_timer() : start_perf_timer();
}


void EventDriver::set_param(SerialPacket& packet)
{	
	// Takes parameter arguments from the server to change operating modes
	
	switch (packet.argument_int)
	{
		// Run: Start the belt and feeder.
		case 1001:
			belt.start();
			feeder.start_delayed(gp::feeder_delay);
		break;
		
		// Halt: Stop the belt and feeder.
		case 1000:
			belt.stop();
			feeder.stop();
		break;
		
		// set encoder sim mode
		case 9001:
			if (packet.payload_int == 0) encoder.stop_sim();
			if (packet.payload_int == 1) encoder.start_sim();
			if (packet.payload_int == 2) encoder.toggle_sim();
		break;
		
		// set performance timer mode
		case 9002:
			if (packet.payload_int == 0) stop_perf_timer();
			if (packet.payload_int == 1) start_perf_timer();
			if (packet.payload_int == 2) toggle_perf_timer();
		break;
	}
}
 



#endif /* EVENTDRIVER_H_ */