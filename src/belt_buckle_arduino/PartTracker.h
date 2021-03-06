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

	void add_part(SerialPacket&, unsigned long);
	void assign_bin(SerialPacket&);
	void free_part_slot(unsigned int);
	int get_bin(unsigned int);
	unsigned long  get_dist(unsigned int);
	bool get_occupied(unsigned int);
	void print_part_list(int);
	void print_part_single(unsigned int);
	void tel_server_sorted(unsigned int);
	void tel_server_lost(unsigned int);
	void remove_part(SerialPacket&);
	bool get_assigned(unsigned in);
	
private:

	TrackedPart part_list[gp::part_list_length];
	bool check_range(unsigned int);
	void print_array(char*);
	void print_slot(unsigned int);
	void print_list_header();
};


		
void PartTracker::add_part(SerialPacket& packet, unsigned long dist){

	// first check to see if this part number exists already
	for (unsigned int i = 0; i < gp::part_list_length; i++)
	{
		// skip slots not marked as occupied
		if (part_list[i].occupied)
		{		
			//  compare part id's	
			if (memcmp(part_list[i].id, packet.payload, gp::payload_length) == 0)
			{
				packet.result = 409;
				return;
			}
		}	
	}
	
	// find a free slot in the part list.
	int slot = -1;
	for (unsigned int i = 0; i < gp::part_list_length; i++)
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
	for (int i = 0; i < gp::payload_length; i++)            
	{
		part_list[slot].id[i] = packet.payload[i];
	}
		
	part_list[slot].occupied = true;								// this slot is no longer free
	part_list[slot].distance = dist - packet.argument_int;          // set the belt distance
	part_list[slot].bin = 0;										// bin is 0 until the assign command
	part_list[slot].assigned = false;								// the part has not yet been assigned to a bin
	
	packet.result = 200;
}


void PartTracker::assign_bin(SerialPacket& packet){ 
	            
	// assign a part to a bin. loops through the payload array, returns 404 if the part isn't found
	for (unsigned int i = 0; i < gp::part_list_length; i++)
	{
		if (memcmp(part_list[i].id, packet.payload, gp::payload_length) == 0)
		{
			part_list[i].bin = packet.argument_int;
			part_list[i].assigned = true;
			packet.result = 200;
			return;
		}
	}
	
	packet.result = 404;
}


void PartTracker::free_part_slot(unsigned int slot)
{
	part_list[slot].occupied = false;
	part_list[slot].assigned = false;
	part_list[slot].bin = 0;
	part_list[slot].distance = 0;
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
	if (slot >= gp::part_list_length || slot < 0)
	{
		return false;
	}
	return true;
}


void PartTracker::print_part_list(int count = gp::part_list_length) 
{
	// Prints out the part list from 0 to count like this:
	// Occ.  :   Dist   :   Bin   :  Id
	// bool  : 12345678 :     0   : 123456789012
	// ... count ...
	// bool  : 12345678 :     0   : 123456789012
	
	// Range checking. Print full list if out of range.
	if (count < 1 || count > gp::part_list_length)
	{
		count = gp::part_list_length;
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
	for (int i = 0; i <= gp::print_size; i++)
	{
		if (to_be_printed[i] == '\0')
		{
			return;
		}
		Serial.print(to_be_printed[i]);
	}
}


void PartTracker::print_slot(unsigned int slot)
{
	Serial.print(part_list[slot].occupied);
	Serial.print("      :     ");
	Serial.print(part_list[slot].assigned);
	Serial.print("      :     ");
	Serial.print(part_list[slot].bin);
	Serial.print("     :     ");
	Serial.print(part_list[slot].distance);
	Serial.print("  : ");
	print_array(part_list[slot].id);
	Serial.println("");
}


void PartTracker::print_list_header()
{
	Serial.println("Occed   :  Asignd  :    Bin    :    Dist   :   Id") ;
}


void PartTracker::tel_server_sorted(unsigned int part_slot)
{
		// Sends a TEL command to notify the server that a part has been sorted.
		
		if (!(check_range(part_slot)))
		{
			Serial.println("Bad part index in tel_server_sorted");
			return;
		}
		
		Serial.print("[TEL-C-200-");
		print_array(part_list[part_slot].id);
		Serial.print("-CSUM]");
}


void PartTracker::tel_server_lost(unsigned int part_slot)
{
	// Sends a TEL command to notify the server that a part has been sorted.
	
	if (!(check_range(part_slot)))
	{
		Serial.println("Bad part index in tel_server_sorted");
		return;
	}
	
	Serial.print("[TEL-F-200-");
	print_array(part_list[part_slot].id);
	Serial.print("-CSUM]");
}


void PartTracker::remove_part(SerialPacket& packet)
{
	// searches the part list for a matching id number and removes it.
	for (unsigned int i = 0; i < gp::part_list_length; i++)
	{
		if (memcmp(part_list[i].id, packet.payload, gp::payload_length) == 0)
		{
			free_part_slot(i);
			packet.result = 200;
			return;
		}
	}
	
	// No match found
	packet.result = 404;
	return;
}


bool PartTracker::get_assigned(unsigned slot)
{
	// Returns the state of the assigned variable for a slot in the part_list.
	return part_list[slot].assigned;
}

#endif /* PARTTRACKER_H_ */