class BeltController{
public:

	BeltController(int pin) : control_pin{pin} mode{false} {}

	bool get_mode();
	void set_mode(bool set);
	void toggle_mode();


private:

	bool mode;
	int control_pin;
};


void BeltController::belt_toggle_mode()
{
	if (mode)
	{
		mode = false;
		digitalWrite(control_pin, LOW);
	}
	else
	{
		mode = true;
		digitalWrite(control_pin, HIGH);
	}
}

