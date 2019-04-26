/*
 * PacketStruct.h
 *
 * Created: 4/25/2019 11:20:03 PM
 *  Author: spongeloaf
 */ 


#ifndef PACKETSTRUCT_H_
#define PACKETSTRUCT_H_


// These cannot be changed without modifying the ServerInterface class.
// They are used in the parsing of packets.
// DO NOT CHANGE THEM UNLESS YOU KNOW EXACTLY WHAT YOU ARE DOING!
const int packet_length = 23;						// length in bytes of each command packet
const int csum_length = 5;							// length in bytes of of the CSUM +1 for terminator
const int argument_length = 5;						// number of bytes in the packet argument
const int payload_length = 13;						// number of bytes in the packet payload



// a struct to hold packet data
struct SerialPacket{
	char raw_packet[packet_length] = 'z';
	char command = 'z';
	unsigned int argument_int = 0;                               // int to store the packet argument
	char argument_arr[argument_length] = {'z'};                  // char array for parsing packet arguments
	char payload[payload_length] = {'z'};                        // char array for parsing packet payload
	int result = 0;												 // Error messages are a letter designator matching the command, followed by a three digit number
};


#endif /* PACKETSTRUCT_H_ */