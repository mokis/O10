void init_motor_controller() {
  // shift zero points
  shift_zero(fr_y, fr_offset);
  shift_zero(fl_y, fl_offset);
  shift_zero(rr_y, rr_offset);
  shift_zero(rl_y, rl_offset);
}  


void motor_controller() {
  int len_x = sizeof(common_x) / 2;
  
  fr_micros = curve_interpolation_lim(common_x, fr_y, fr_ctrl_value, len_x);
  fl_micros = curve_interpolation_lim(common_x, fl_y, fl_ctrl_value, len_x); 
  rr_micros = curve_interpolation_lim(common_x, rr_y, rr_ctrl_value, len_x);
  rl_micros = curve_interpolation_lim(common_x, rl_y, rl_ctrl_value, len_x);
  
  servo_fr.writeMicroseconds(fr_micros);
  servo_fl.writeMicroseconds(fl_micros);
  servo_rr.writeMicroseconds(rr_micros);
  servo_rl.writeMicroseconds(rl_micros);
}



