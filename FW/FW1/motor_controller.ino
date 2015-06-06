void init_motor_controller() {
  // shift zero points
  shift_zero(fr_y, fr_offset);
  shift_zero(fl_y, fl_offset);
  shift_zero(rr_y, rr_offset);
  shift_zero(rl_y, rl_offset);
}
  
void shift_zero(int *curve, int offset) {
  int len = sizeof(curve) / 2;
  
  for(int i = 0; i < len; i++) {
   curve[i] = curve[i] + offset;
  } 
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


int curve_interpolation_lim(int *curve_x, int *curve_y, int input_val, int array_len) {
  int last = array_len - 1;
  int i = 0;

  float ratio;
  int dy;
  int output_val;
  
  if (input_val <= curve_x[0]) {
    return curve_y[0];
  }

  if (input_val >= curve_x[last]) {
    return curve_y[last];
  }    

  while (curve_x[i] < input_val) {
    i++;
  }

  ratio = (float)(input_val - curve_x[i-1]) / (curve_x[i] - curve_x[i-1]);

  dy = curve_y[i] - curve_y[i-1];
  output_val = curve_y[i-1] + (int)(ratio * dy + 0.5);

  return output_val;
}



