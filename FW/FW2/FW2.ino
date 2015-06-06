// freeIMU libraries 
/*
#include <SPI.h>
#include <I2Cdev.h>
#include <bma180.h>
#include <HMC58X3.h>
#include <MS561101BA.h>
#include <MPU60X0.h>
#include <DebugUtils.h>
#include <EEPROM.h>

*/ 
#include <Wire.h>
//#include "FreeIMU.h"
//#include <TimerOne.h>

// For servos
#include <Servo.h>

// Global variables
#include "globals.h"

#define FR    9
#define FL    5
#define RR    4
#define RL    11
#define PAN   A1

Servo servo_fr;
Servo servo_fl;
Servo servo_rr;
Servo servo_rl;

Servo servo_pan;

//FreeIMU imu = FreeIMU();

void setup()
{
  servo_fr.attach(FR);
  servo_fl.attach(FL);
  servo_rr.attach(RR);
  servo_rl.attach(RL); 
  
  servo_pan.attach(PAN);
  
  init_motor_controller();
  init_pan_controller();
  
  Serial.begin(115200);
  
  Wire.begin();
  
  delay(500);
  //imu.init(true); // the parameter enable or disable fast mode
  delay(500);
}


void loop()
{
  //imu.getValues(imu_values);
  motor_controller();
  pan_controller();
  serial_com();
  delay(1);
}
