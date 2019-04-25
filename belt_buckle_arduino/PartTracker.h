/*
 * PartTracker.h
 *
 * Created: 4/23/2019 3:30:43 PM
 *  Author: spongeloaf
 */ 


#ifndef PARTTRACKER_H_
#define PARTTRACKER_H_



class PartTracker{
public:

	PartTracker(int idx_len, int pyld_len) : 
		index_length{idx_len}, 
		payload_length{pyld_len},
		index_distance{0},
		index_bin{0},
		index_payload{'z'}
		{}

	int add_part(char (*));
	int assign_bin(int, char (*));
	int add_part_and_assign_bin(char (*), int, char (*));
	void flush_part_array(int);
	bool get_bin(int);
	unsigned long  get_dist(int);
	

private:
	
	int index_length;
	int payload_length;
	unsigned int index_selector = 0;                                 // the next available index for storing a part
	unsigned long index_distance[index_length];                // the main distance index - global
	int index_bin[index_length];                               // the main bin index - global
	char index_payload[index_length][payload_length];          // the main part index - global
};


int PartTracker::add_part(char& packet_payload[]){                                                      
	// Adds a new part instance to the part index array
	bool valid_part = true;

	// first check to see if this part number exists already
	for (unsigned int i = 0; i < index_length; i++)
	{
		if (memcmp(index_payload[i], packet_payload, payload_length) == 0)
		{
			return 409;
		}
	}
	
	for (int i = 0; i < payload_length; i++)                                          // Stores the received part index in the DB
	{
		index_payload[index_selector][i] = packet_payload[i];
	}

	index_distance[index_selector] = encoder.get_dist();                    // set the belt distance
	index_bin[index_selector] = 0;                                           // bin is always 0 until the sort command
	index_selector++;
	
	if (index_selector >= index_length)
	{
		index_selector = 0;
	}
	return 200;
}


int PartTracker::assign_bin(int packet_argument, char packet_payload[]){             // assign a part to a bin. loops through the payload array, returns 404 if the part isn't found

	for (unsigned int i = 0; i < index_length; i++)
	{
		if (memcmp(index_payload[i], packet_payload, payload_length) == 0)   // Reminder: memcmp returns 0 when it finds a match.
		{
			index_bin[i] = packet_argument;
			return 200;
		}
	}
	return 404;

}


int PartTracker::add_part_and_assign_bin(char packet_payload[], int assign_argument, char assign_payload[])
{
	//  TODO: figure out what in gods name is wrong with the arguments here. l_payload? WTF. And is assign_payload even used?
	bool valid_part = true;

	// first check to see if this part number exists already
	for (unsigned int i = 0; i < index_length; i++)
	{
		if (memcmp(index_payload[i], packet_payload, payload_length) == 0)
		{
			return 409;
		}
	}
	
	for (int i = 0; i < payload_length; i++)                                          // Stores the received part index in the DB
	{
		index_payload[index_selector][i] = packet_payload[i];
	}

	index_distance[index_selector] = encoder.get_dist();                    // set the belt distance
	index_bin[index_selector] = assign_argument;                                     // set the bin number
	index_selector++;
	
	if (index_selector >= index_length)
	{
		index_selector = 0;
	}
	return 200;
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


int PartTracker::get_bin(int bin)
{
	return index_bin[bin];
}


unsigned long  PartTracker::get_dist(int bin)
{
	return index_distance[bin];
}


#endif /* PARTTRACKER_H_ */