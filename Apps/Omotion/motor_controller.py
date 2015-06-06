import interface
reload(interface)

class motor_controller:
    def __init__(self):
        com_port = "/dev/ttyACM0"
        #com_port = "COM8"
        
        self.multiwii = interface.interface()
        self.multiwii.init_serial(com_port)
        self.multiwii.get_variables("")

        self.fow_scale = 100.0
        self.turn_scale = 100.0
        self.skew_scale = 100.0


    def drive(self, fow_speed, turn_speed, skew):

        motor_fow = fow_speed * self.fow_scale
        motor_turn = turn_speed * self.turn_scale
        motor_skew = skew * self.skew_scale
        
        self.multiwii.set_variable("fr_ctrl_value", motor_fow + motor_turn + motor_skew, 0)
        self.multiwii.set_variable("rr_ctrl_value", motor_fow + motor_turn - motor_skew, 0)
        self.multiwii.set_variable("fl_ctrl_value", motor_fow - motor_turn + motor_skew, 0)
        self.multiwii.set_variable("rl_ctrl_value", motor_fow - motor_turn - motor_skew, 0)

    
