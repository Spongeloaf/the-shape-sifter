/*
 * PartTracker.h
 *
 * Created: 4/23/2019 3:30:43 PM
 *  Author: spongeloaf
 */ 



#ifndef PARTTRACKER_H_
#define PARTTRACKER_H_



#include "bb_parameters.h"
extern SerialPacket packet;


class PartTracker{
public:

	PartTracker() : 
		index_distance{0},
		index_bin{0},
		index_payload{'z'}
		{}

	int add_part(SerialPacket&, unsigned long);
	int assign_bin(SerialPacket&);
	void flush_part_array(int);
	int get_bin(int);
	unsigned long  get_dist(int);
	

private:

	unsigned int index_selector = 0;                                 // the next available index for storing a part
	unsigned long index_distance[index_length];                // the main distance index - global
	int index_bin[index_length];                               // the main bin index - global
	char index_payload[index_length][payload_length];          // the main part index - global
};


int PartTracker::add_part(SerialPacket& packet, unsigned long dist){                                                      

	// first check to see if this part number exists already
	for (unsigned int i = 0; i < index_length; i++)
	{
		if (memcmp(index_payload[i], packet.payload, payload_length) == 0)
		{
			packet.result = 409;
			return;
		}
	}
	
	for (int i = 0; i < payload_length; i++)                                          // Stores the received part index in the DB
	{
		index_payload[index_selector][i] = packet.payload[i];
	}

	index_distance[index_selector] = dist;                    // set the belt distance
	index_bin[index_selector] = 0;                                           // bin is always 0 until the assign command
	index_selector++;
	
	if (index_selector >= index_length)
	{
		index_selector = 0;
	}
	packet.result = 200;
}


int PartTracker::assign_bin(SerialPacket& packet){             // assign a part to a bin. loops through the payload array, returns 404 if the part isn't found

	for (unsigned int i = 0; i < index_length; i++)
	{
		if (memcmp(index_payload[i], packet.payload, payload_length) == 0)   // Reminder: memcmp returns 0 when it finds a match.
		{
			index_bin[i] = packet.argument_int;
			packet.result = 200;
			return;
		}
	}
	packet.result = 404;
}


void PartTracker::flush_part_array(int index)
{
	// this function zeroes the part index array.
	// If the index number passed is out of bounds, an error is printed.
	// If the index number passed is -1, the whole array is flushed.
	

	if ((-1 < index) && (index < index_length))	// zeroes one index of the array
	{
		index_bin[index] = 0;
		index_distance[index] = 0;
		index_payload[index][0] = '0';
		index_payload[index][1] = '0';
		index_payload[index][2] = '0';
		index_payload[index][3] = '0';
		index_payload[index][4] = '0';
		index_payload[index][5] = '0';
		index_payload[index][6] = '0';
		index_payload[index][7] = '0';
		index_payload[index][8] = '0';
		index_payload[index][9] = '0';
		index_payload[index][10] = '0';
		index_payload[index][11] = '0';
		index_payload[index][12] = '\0';
		return;
	}
	if (index == -1)   // zeroes the whole array
	{
		for (int i=0; i < index_length; i++)
		{
			index_bin[i] = 0;
			index_distance[i] = 0;
			index_payload[i][0] = '0';
			index_payload[i][1] = '0';
			index_payload[i][2] = '0';
			index_payload[i][3] = '0';
			index_payload[i][4] = '0';
			index_payload[i][5] = '0';
			index_payload[i][6] = '0';
			index_payload[i][7] = '0';
			index_payload[i][8] = '0';
			index_payload[i][9] = '0';
			index_payload[i][10] = '0';
			index_payload[i][11] = '0';
			index_payload[i][12] = '\0';
		}
		return;
	}
	Serial.println("Error: Flush index out of range!");		// nothing is zeroed if index is out of range!
}


int PartTracker::get_bin(int index)
{
	return index_bin[index];
}


unsigned long  PartTracker::get_dist(int bin)
{
	return index_distance[bin];
}


#endif /* PARTTRACKER_H_ */