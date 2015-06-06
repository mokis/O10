# -*- coding: cp1252 -*-
import time
from math import *
import random

import pygame
from pygame.locals import *

import motor_controller
reload(motor_controller)

import subpub3
reload(subpub3)

import speed_filter
reload(speed_filter)


#############################################
zmq = subpub3.messanger("192.168.2.1")
#zmq = subpub3.messanger()
zmq.sub("man_ctrl")

print "###########"
print "  motion"
print "###########"
print ""

print "sub: man_ctrl"

pygame.init()
clock = pygame.time.Clock()

ot = time.time()
running = True

fow_speed = 0
turn_speed = 0
skew = 0

connection_counter = 0

speed_f = speed_filter.speed_filter()

motor_ctrl = motor_controller.motor_controller()

print "start"

while running:

    zmq.synch()
    man_ctrl = zmq.recv("man_ctrl")
    
    connection_counter += 1

    if len(man_ctrl) == 3:
        connection_counter = 0

        fow_speed = float(man_ctrl[0])
        turn_speed = float(man_ctrl[1])
        skew = float(man_ctrl[2])

        speed_f.set_sensitivity(0.25)
        fow_speed, turn_speed, skew = speed_f.update_speeds(fow_speed, turn_speed, skew)

    elif connection_counter >= 50:
        connection_counter = 50
        
        fow_speed = float(0)
        turn_speed = float(0)
        skew = float(0)

        speed_f.set_sensitivity(0.25)
        fow_speed, turn_speed, skew = speed_f.update_speeds(fow_speed, turn_speed, skew)

    motor_ctrl.drive(fow_speed, turn_speed, skew)

    #clock.tick(30)

pygame.quit()





    
    
    
