void shift_zero(int *curve, int offset) {
  int len = sizeof(curve) / 2;
  
  for(int i = 0; i < len; i++) {
   curve[i] = curve[i] + offset;
  } 
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




