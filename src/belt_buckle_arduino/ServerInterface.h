/*
 * ServerInterface.h
 *
 * Created: 4/25/2019 5:22:45 PM
 *  Author: spongeloaf
 */ 



#include "bb_parameters.h"



#ifndef SERVERINTERFACE_H_
#define SERVERINTERFACE_H_





class ServerInterface{

public:
	
	ServerInterface(int payload, int csum, int arg, int packet) :
		payload_len{payload},
		csum_len{csum},
		argument_len{arg},
		packet_len{packet}
		{};
	
	void send_ack(SerialPacket& packet);
	void read_serial_port();
	void parse_packet(char* packet_string);
	void construct_packet(char* packet_str);
	void throw_error(SerialPacket& packet);
	
	
private:
	
	char serial_char;							// The latest char received from the serial port
	const int packet_len;						// length in bytes of each command packet
	const int csum_len;							// length in bytes of of the CSUM +1 for terminator
	const int argument_len;						// number of bytes in the packet argument
	const int payload_len;						// number of bytes in the packet payload


};


void ServerInterface::read_serial_port(){

	// abort if there's nothing to read.
	if (Serial.available() == 0)
	{
		return;
	}
	
	serial_char = Serial.read();                                        //  Read a character
	
	switch (serial_char)
	{
		case '<':                                                       // '<' is the packet initiator.
		memset(&serial_read_string[0], 0, sizeof(serial_read_string));  // clear the array every time we get a new initiator.
		serial_read_string_index = 0;                                   // reset the array index because we're starting a new command.
		serial_read_string[0] = serial_char;                            // place our '<' character at the beginning of the array
		serial_read_string_index = serial_read_string_index + 1;        // increment array index number
			
		// print_array(serial_read_string);                              // for debugging
		// Serial.println("packet initiator found");                     // for debugging
		break;
			
		case '>':                                                         // '>' is the packet terminator.
		serial_read_string[serial_read_string_index] = serial_char;     // add the terminator to the string before we begin
		parse_packet(serial_read_string);                               // executes the received packet
		memset(&serial_read_string[0], 0, sizeof(serial_read_string));  // clear the array every time we get a new initiator.
		serial_read_string_index = 0;                                   // reset the packet array index to 0
			
		// Serial.println(strlen(serial_read_string));                   // for debugging
		// print_array(serial_read_string);                              // for debugging
		// Serial.println("packet terminator found");                    // for debugging
		break;
			
		default:
		if (serial_read_string_index < (sizeof(serial_read_string) - 2))          // if the serial read string get too long, we stop adding to it to prevent overruns.
		{
			serial_read_string[serial_read_string_index] = serial_char;     // append the read character to the array
			serial_read_string_index = serial_read_string_index + 1;        // increment the array index number
		}
		else                                                            // should we receive more than 22 characters before a terminator, something is wrong, dump the string.
		{
			memset(&serial_read_string[0], 0, sizeof(serial_read_string));  // clear the array every time we get a new initiator.
			serial_read_string_index = 0;                                   // reset the array index because we're starting a new command.
		}
	}
}



void ServerInterface::throw_error(SerialPacket& packet)
{
	// TODO
}



#endif /* SERVERINTERFACE_H_ */