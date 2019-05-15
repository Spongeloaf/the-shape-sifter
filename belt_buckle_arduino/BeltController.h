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
		pinMode(gp::belt_control_pin, OUTPUT);
		mode = false;
	};

	bool get_mode();
	void toggle_mode();
	void start();
	void stop();


private:

	bool mode;
};


void BeltController::toggle_mode()
{
	if (mode)
	{
		stop();
	}
	else
	{
		start();
	}
}


bool BeltController::get_mode()
{
	return mode;
}


void BeltController::start()
{
	mode = true;
	digitalWrite(gp::belt_control_pin, HIGH);
}


void BeltController::stop()
{
	mode = false;
	digitalWrite(gp::belt_control_pin, LOW);
}


#endif /* BELTCONTROLLER_H_ */