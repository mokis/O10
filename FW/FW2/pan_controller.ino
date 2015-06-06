void init_pan_controller() {
  // shift zero points
  shift_zero(pan_y, pan_offset);
}

void pan_controller() {
  int len_x = sizeof(common_x) / 2;
  
  pan_micros = curve_interpolation_lim(pan_x, pan_y, pan_angle, len_x);
  
  servo_pan.writeMicroseconds(pan_micros);
}

