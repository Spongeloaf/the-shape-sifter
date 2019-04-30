/*
 * BeltController.h
 *
 * Created: 4/26/2019 2:02:19 PM
 *  Author: spongeloaf
 */



#ifndef BELTCONTROLLER_H_
#define BELTCONTROLLER_H_
#include "bb_parameters.h"



class BeltController{

public:

	BeltController()
	{ 
		pinMode(belt_control_pin, OUTPUT);
		mode = false;
	};

	bool get_mode();
	void set_mode(bool);
	void toggle_mode();


private:

	bool mode;
};


void BeltController::toggle_mode()
{
	if (mode)
	{
		mode = false;
		digitalWrite(belt_control_pin, LOW);
	}
	else
	{
		mode = true;
		digitalWrite(belt_control_pin, HIGH);
	}
}


bool BeltController::get_mode()
{
	return mode;
}


void BeltController::set_mode(bool set)
{
	if (set)
	{
		mode = true;
		digitalWrite(belt_control_pin, HIGH);
	}
	else
	{
		mode = false;
		digitalWrite(belt_control_pin, LOW);
	}
}


#endif /* BELTCONTROLLER_H_ */