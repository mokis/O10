class speed_filter:
    def __init__(self):
        self.fow_speed = 0
        self.turn_speed = 0
        self.skew = 0
        self.sensitivity = 1

    def set_sensitivity(self, sensitivity):
        self.sensitivity = sensitivity

    def update_speeds(self, new_fow_speed, new_turn_speed, new_skew):
        # 1st order filter
        self.fow_speed = self.fow_speed * (1-self.sensitivity) + new_fow_speed * self.sensitivity
        self.turn_speed = self.turn_speed * (1-self.sensitivity) + new_turn_speed * self.sensitivity
        self.skew = self.skew * (1-self.sensitivity) + new_skew * self.sensitivity

        if self.fow_speed > 1:
            self.fow_speed = 1

        if self.fow_speed < -1:
            self.fow_speed = -1

        if self.turn_speed > 1:
            self.turn_speed = 1

        if self.turn_speed < -1:
            self.turn_speed = -1

        if self.skew > 1:
            self.skew = 1

        if self.skew < -1:
            self.skew = -1

        return self.fow_speed, self.turn_speed, self.skew

