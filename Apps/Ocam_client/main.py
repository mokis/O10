# -*- coding: cp1252 -*-
import time
from math import *
import random

import pygame
from pygame.locals import *

import subpub3
reload(subpub3)

import camera_widget
reload(camera_widget)




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
pygame.init()
x_size = 680
y_size = 520

screen = pygame.display.set_mode((x_size, y_size), pygame.RESIZABLE)
screen.fill((250,250,250))
print "screen created"

clock = pygame.time.Clock()
mouse = my_mouse()

orgin = (20,20)

cam_block = camera_widget.camera_widget([20, 20], [640, 480], "CAM1")

zmq = subpub3.messanger()
zmq.sub("cam1")


print "##############"
print "  Rcamclient"
print "##############"
print ""

#zmq.connect_sub_manually("cam1", "127.0.0.1:10060")

ot = time.time()
running = True

while running:
    mouse.reset_events()
    zmq.synch()

    # eventit, hiiriluokka ylempänä
    for ev in pygame.event.get():
        if ev.type == QUIT:
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

    
    data = zmq.recv("cam1", False)

    print time.time()-ot, len(data)
    ot = time.time()

    cam_block.update(screen, data)

    pygame.display.flip()
    #time.sleep(1)

pygame.quit()
print "clean exit"
