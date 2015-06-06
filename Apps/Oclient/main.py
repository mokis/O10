# -*- coding: cp1252 -*-
import time
from math import *
import random

import pygame
from pygame.locals import *

import subpub3
reload(subpub3)


#############################################
class my_mouse:
    def __init__(self):
        self.pos = [0,0]
        self.buttons = [0,0,0,0,0,0,0,0,0,0]
        self.pressed_buttons = []
        self.released_buttons = []

    def set_mouse_motion(self, event):
        self.pos[0] = event.pos[0]
        self.pos[1] = event.pos[1]

    def set_button_down(self, event):
        self.buttons[event.button] = 1

    def set_button_up(self, event):
        self.buttons[event.button] = 0

    def init_events(self):
        self.pressed_buttons = []
        self.released_buttons = []

    def set_pressed(self, event):
        self.pressed_buttons.append(event.button)

    def set_released(self, event):
        self.released_buttons.append(event.button)

    def reset_events(self):
        mouse.pressed_buttons = []
        mouse.released_buttons = []



#############################################
zmq = subpub3.messanger()
zmq.pub("man_ctrl", 10050, 0.2)
        
pygame.init()
x_size = 600
y_size = 360
screen = pygame.display.set_mode((x_size, y_size))
screen.fill((250,250,250))
print "screen created"

clock = pygame.time.Clock()
mouse = my_mouse()

ot = time.time()
running = True

s1_speed = 0
s2_speed = 0
s3_speed = 0

pad = pygame.joystick.Joystick(0)
pad.init()

while running:

    zmq.synch()

    screen.fill((250,250,250))
    mouse.reset_events()

    # eventit, hiiriluokka ylempänä
    for ev in pygame.event.get():
        if ev.type == QUIT:
            running = False
            break
        
        if ev.type == KEYDOWN:
            if ev.key == K_q:
                running = False
                break
            
        if ev.type == MOUSEMOTION:
            mouse.set_mouse_motion(ev)

        if ev.type == MOUSEBUTTONUP:
            mouse.set_button_up(ev)
            mouse.set_released(ev)

        if ev.type == MOUSEBUTTONDOWN:
            mouse.set_button_down(ev)
            mouse.set_pressed(ev)

    x_axis = pad.get_axis(1)
    y_axis = pad.get_axis(0)
    z_axis = pad.get_axis(3)

    pad_enable = True
    
    if abs(pad.get_axis(2)) > 0.3:
        pad_enable = True

    if abs(x_axis) < 0.01 or not pad_enable:
        x_axis = 0

    if abs(y_axis) < 0.01 or not pad_enable:
        y_axis = 0

    if abs(z_axis) < 0.01 or not pad_enable:
        z_axis = 0

    dxs = s1_speed + x_axis*2
    dys = s2_speed + y_axis*2
    das = s3_speed + z_axis*2

    s1_speed -= dxs*0.2
    s2_speed -= dys*0.2
    s3_speed -= das*0.2

    if s1_speed > 2:
        s1_speed = 2
    if s1_speed < -2:
        s1_speed = -2

    if s2_speed > 2:
        s2_speed = 2
    if s2_speed < -2:
        s2_speed = -2

    if s3_speed > 2:
        s3_speed = 2
    if s3_speed < -2:
        s3_speed = -2

    if pad.get_button(0):
        divider = 2.0
    else:
        divider = 6.0

    zmq.send(str(s1_speed/divider) + " " + str(s2_speed/divider) + " " + str(s3_speed/divider), "man_ctrl")

    x_offset = 40
    y_offset = 40 

    pygame.draw.rect(screen, (0,0,0), (x_offset, y_offset, 200, 40), 1)
    pygame.draw.rect(screen, (0,0,0), (x_offset, y_offset+60, 200, 200), 1)

    pygame.draw.circle(screen, (0,0,0), (int(x_offset+100-s3_speed*(160/4)), int(y_offset+20)), 20, 0)
    
    pygame.draw.circle(screen, (0,0,0), (int(x_offset+100-s2_speed*(160/4)), int(y_offset+60+100-s1_speed*(160/4))), 20, 0)

    clock.tick(30)
    pygame.display.flip()

pygame.quit()
print "clean exit"




    
    
    
