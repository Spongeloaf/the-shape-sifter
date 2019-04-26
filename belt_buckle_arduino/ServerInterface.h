/*
 * ServerInterface.h
 *
 * Created: 4/25/2019 5:22:45 PM
 *  Author: spongeloaf
 */ 


#ifndef SERVERINTERFACE_H_
#define SERVERINTERFACE_H_





class ServerInterface{

public:
	
	ServerInterface(int payload, int csum, int arg, int packet) :
		payload_len{payload},
		csum_len{csum},
		argument_len{arg},
		packet_len{packet},
		{};
	
	void send_ack(SerialPacket& packet);
	void read_serial_port();
	void parse_packet(SerialPacket& packet);
	void throw_error(SerialPacket& packet);
	
private:
	
	const int packet_len;						// length in bytes of each command packet
	const int csum_len;							// length in bytes of of the CSUM +1 for terminator
	const int argument_len;						// number of bytes in the packet argument
	const int payload_len;						// number of bytes in the packet payload
	int  serial_read_string_index;				// the current index number of the read string
	char serial_read_string[packet_len + 1];    // stores the read chars

};


void ServerInterface::read_serial_port(){

	// We inititialize all of our local vars here; never in-line. It's much easier to track them. the only exceptions are vars used in for loops.
	char serial_char;
	if (Serial.available() > 0)
	{
		serial_char = Serial.read();                                        //  Read a character
		// print_array(serial_read_string);                                  // for debugging

		switch (serial_char)
		{
			case '<':                                                         // '<' is the packet initiator.
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
}


void ServerInterface::send_ack(char send_command, int send_command_result, char send_packet_payload[]){
	Serial.print("[ACK-");
	Serial.print(send_command);
	Serial.print("-");
	Serial.print(send_command_result);
	Serial.print("-");
	Serial.print(send_packet_payload);
	Serial.print("-");
	Serial.print("CSUM");
	Serial.print("]");
}


void ServerInterface::validate_packet(SerialPacket& packet)
{
	// ------------TODO: Needs to have CSUM installed HERE------------
	
	// Serial.print("Packet length:");                                       // for debugging
	// Serial.println(strlen(packet));                                       // for debugging
	
	if (strlen(packet.raw_packet) != packet_len)
	{
		packet.result = 401;
		return;
	}
				
	//  this loop sets up the argument array
	for (int i = 0; i <= argument_len - 2; i++)                      // argument length -2, because the last character is \0 and we are zero indexed
	{
		packet.argument_arr[i] = packet.raw_packet[i + 2];                   //  the argument begins on the [2] char
	}
	packet.argument_arr[4] = '\0';                                // don't forget the terminator on the array!
	packet.argument_int = atoi(packet.argument_arr);        // the bin number is more useful as an int than an array. But now we have both.

	//  this loop sets up the payload array
	for (int i = 0; i <= payload_len - 2; i++)                       // payload length -2, because the last character is \0 and we are zero indexed
	{
		packet.payload[i] = packet.raw_packet[i + 6];                        //  the argument begins on the [2] char
	}
	packet.payload[payload_len - 1] = '\0';
	
	// TODO: insert more thorough command and argument checking here
	
	packet.result = 200;
}


void ServerInterface::throw_error(SerialPacket& packet)
{
	// TODO
}


#endif /* SERVERINTERFACE_H_ */