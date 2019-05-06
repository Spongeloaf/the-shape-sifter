/*
 * PartTracker.h
 *
 * Created: 4/23/2019 3:30:43 PM
 *  Author: spongeloaf
 */ 



#ifndef PARTTRACKER_H_
#define PARTTRACKER_H_
#include "bb_parameters.h"



class PartTracker{
public:

	PartTracker() {};

	int add_part(SerialPacket&, unsigned long);
	int assign_bin(SerialPacket&);
	void flush_part_array(int);
	int get_bin(int);
	unsigned long  get_dist(int);
	bool get_occupied(int)

private:

	TrackedPart part_list[part_list_length];
};


		
int PartTracker::add_part(SerialPacket& packet, unsigned long dist){

	// first check to see if this part number exists already
	for (unsigned int i = 0; i < part_list_length; i++)
	{
		if (memcmp(part_list[i].id, packet.payload, payload_length) == 0)
		{
			packet.result = 409;
			return;
		}
	}
	
	// find a free slot in the part list.
	int slot = -1;
	for (unsigned int i = 0; i < part_list_length; i++)
	{
		if (part_list[i].occupied == false)
			{
				part_list[i].occupied == true;
				slot = i;
				break;
			}
	}
	
	// true when there's no free slots in the part list.
	if (slot == -1)
	{
		packet.result = 419;
		return;
	}
	
	// Stores the received part index in the part_list
	for (int i = 0; i < payload_length; i++)            
	{
		part_list[slot].id[i] = packet.payload[i];
	}

	part_list[slot].distance = dist;                    // set the belt distance
	part_list[slot].bin = 0;                            // bin is always 0 until the assign command
		
	packet.result = 200;
}


int PartTracker::assign_bin(SerialPacket& packet){ 
	            
	// assign a part to a bin. loops through the payload array, returns 404 if the part isn't found
	for (unsigned int i = 0; i < part_list_length; i++)
	{
		if (memcmp(part_list[i].id, packet.payload, payload_length) == 0)
		{
			part_list[i].bin = packet.argument_int;
			packet.result = 200;
			return;
		}
	}
	
	packet.result = 404;
}


unsigned long PartTracker::get_dist(int slot)
{
	// returns the distance value stored in the parts list.
	// This distance is the belt position when the part was added.
	
	// check if index is in range
	if (slot >= part_list_length || slot < 0)
	{
		// TODO: Make this send an error message to the server.
		Serial.println("Part list index out of range!");
		return 0;
	}
	
	return part_list[slot].distance;
}


int PartTracker::get_bin(int slot)
{
	return part_list[slot].bin;
}


bool PartTracker::get_occupied(int slot)
{
	
}


#endif /* PARTTRACKER_H_ */