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
	void free_part_slot(unsigned int);
	int get_bin(unsigned int);
	unsigned long  get_dist(unsigned int);
	bool get_occupied(unsigned int);
	void print_part_list(int);
	void print_part_single(unsigned int);
	
private:

	TrackedPart part_list[part_list_length];
	bool check_range(unsigned int);
	void print_array(char*);
	void print_slot(unsigned int);
	void print_list_header();
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
	
	part_list[slot].occupied = true;			// this slot is no longer free
	part_list[slot].distance = dist;            // set the belt distance
	part_list[slot].bin = 0;                    // bin is always 0 until the assign command
		
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


void PartTracker::free_part_slot(unsigned int slot)
{
	part_list[slot].occupied = false;
}


unsigned long PartTracker::get_dist(unsigned int slot)
{
	// returns the distance value stored in the parts list.
	// This distance is the belt position when the part was added.	
	return part_list[slot].distance;
}


int PartTracker::get_bin(unsigned int slot)
{
	if (check_range(slot))
	{
		return part_list[slot].bin;
	}
	return 0;
}


bool PartTracker::get_occupied(unsigned int slot)
{
	if (check_range(slot))
	{
		return part_list[slot].occupied;
	}
	return 0;
}


inline bool PartTracker::check_range(unsigned int slot)
{
	// check if index is in range
	if (slot >= part_list_length || slot < 0)
	{
		// TODO: Make this send an error message to the server.
		Serial.println("Part list index out of range!");
		return false;
	}
	return true;
}


void PartTracker::print_part_list(int count = part_list_length) 
{
	// Prints out the part list from 0 to count like this:
	// Occ.  :   Dist   :   Bin   :  Id
	// bool  : 12345678 :     0   : 123456789012
	// ... count ...
	// bool  : 12345678 :     0   : 123456789012
	
	// Range checking. Print full list if out of range.
	if (count < 1 || count > part_list_length)
	{
		count = part_list_length;
	}

	print_list_header();
	for ( unsigned int slot = 0; slot < count; ++slot )                     //  loop through array's rows
	{
		print_slot(slot);
	}
}


void PartTracker::print_part_single(unsigned int slot) 
{
	// Prints out the part list like this:
	// Occ.  :   Dist   :   Bin   :  Id
	// bool  : 12345678 :     0   : 123456789012
	
	print_list_header();
	print_part_single(slot);
}


void PartTracker::print_array(char* to_be_printed)
{                    
	// prints an array of characters
	for (int i = 0; i <= print_size; i++)
	{
		if (to_be_printed[i] == '\0')
		{
			Serial.print("\r\n");
			return;
		}
		Serial.print(to_be_printed[i]);
	}
}


void PartTracker::print_slot(unsigned int slot)
{
	Serial.print(part_list[slot].occupied);
	Serial.print("      :     ");
	Serial.print(part_list[slot].bin);
	Serial.print("     :     ");
	Serial.print(part_list[slot].distance);
	Serial.print("  : ");
	print_array(part_list[slot].id);
}


void PartTracker::print_list_header()
{
	Serial.println("Occ.   :    Bin    :    Dist   :   Id") ;
}



#endif /* PARTTRACKER_H_ */