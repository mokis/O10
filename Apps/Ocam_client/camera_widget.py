# -*- coding: cp1252 -*-
import pygame
import Image
import StringIO
from math import *


class camera_widget:
    def __init__(self, pos, size, name):

        self.pos = pos
        self.size = size
        self.reso = [640,480]

        self.cam_surf = pygame.image.load("no_cam.jpg")
        self.blit_surf = pygame.Surface(self.size, 0, 24)

        font = pygame.font.SysFont("Fixedsys",20)
        font.set_bold(False)
        self.text = font.render(name, 1, (250,250,250))
        tsize = self.text.get_size()

        self.text_pos = [5,5]


    def update(self, screen, cam_str):
        #print "c", len(cam_str)
        
        # backgroung
        pygame.draw.rect(screen, (245,245,245), [self.pos, self.size], 0)

        if len(cam_str) > 0:
            
            #cam_str = "640"+cam_str

            reso = cam_str[0:3]

            #print "." + reso + "."

            
            
            if reso == "320":
                self.reso = [320,240]
            elif reso == "160":
                self.reso = [160,120]
            else:
                self.reso = [640,480]
                
            try:
                pil_img = Image.open(StringIO.StringIO(cam_str[3:]))
            except:
                print "Error, unable to convert the image"
                pil_img = Image.new("RGB", self.reso, (200,200,200))
            
            self.cam_surf = pygame.image.fromstring(pil_img.tostring(), self.reso, "RGB", False)

        pygame.transform.scale(self.cam_surf, self.size, self.blit_surf)
        self.blit_surf.blit(self.text, (self.text_pos[0], self.text_pos[1]))
        self.draw_frame()
        screen.blit(self.blit_surf, self.pos)


    def position_update(self, pos_dict, maximized):
        if maximized == self.id:
            self.size = [640,480]
        else:
            self.size = [320,240]
        
        self.pos = pos_dict[self.id]
        self.blit_surf = pygame.Surface(self.size, 0, 24)

        print self.id, self.pos

    def move_and_resize(self, new_pos, new_size):
        self.pos = new_pos
        self.size = new_size
        self.blit_surf = pygame.Surface(self.size, 0, 24)

    def draw_frame(self):
        self.blit_surf.lock()

        border = (255,255,255)
        aa_border = (155,155,155)
        bg = (50,50,50)

        pygame.draw.rect(self.blit_surf, bg, [(0,0), self.size], 1)

        # left upper corner
        # erase
        self.blit_surf.set_at((0, 0), border)
        self.blit_surf.set_at((1, 0), border)
        self.blit_surf.set_at((2, 0), aa_border)
        self.blit_surf.set_at((0, 1), border)
        self.blit_surf.set_at((0, 2), aa_border)

        # rounding
        self.blit_surf.set_at((1, 1), bg)
        self.blit_surf.set_at((1, 2), bg)
        self.blit_surf.set_at((2, 1), bg)

        # right upper corner
        # erase
        self.blit_surf.set_at((self.size[0]-1, 0), border)
        self.blit_surf.set_at((self.size[0]-2, 0), border)
        self.blit_surf.set_at((self.size[0]-3, 0), aa_border)
        self.blit_surf.set_at((self.size[0]-1, 1), border)
        self.blit_surf.set_at((self.size[0]-1, 2), aa_border)

        # rounding
        self.blit_surf.set_at((self.size[0]-2, 1), bg)
        self.blit_surf.set_at((self.size[0]-2, 2), bg)
        self.blit_surf.set_at((self.size[0]-3, 1), bg)

        # left lower corner
        # erase
        self.blit_surf.set_at((0, self.size[1]-1), border)
        self.blit_surf.set_at((1, self.size[1]-1), border)
        self.blit_surf.set_at((2, self.size[1]-1), aa_border)
        self.blit_surf.set_at((0, self.size[1]-2), border)
        self.blit_surf.set_at((0, self.size[1]-3), aa_border)

        # rounding
        self.blit_surf.set_at((1, self.size[1]-2), bg)
        self.blit_surf.set_at((1, self.size[1]-3), bg)
        self.blit_surf.set_at((2, self.size[1]-2), bg)

        # right lower corner
        # erase
        self.blit_surf.set_at((self.size[0]-1, self.size[1]-1), border)
        self.blit_surf.set_at((self.size[0]-2, self.size[1]-1), border)
        self.blit_surf.set_at((self.size[0]-3, self.size[1]-1), aa_border)
        self.blit_surf.set_at((self.size[0]-1, self.size[1]-2), border)
        self.blit_surf.set_at((self.size[0]-1, self.size[1]-3), aa_border)

        # rounding
        self.blit_surf.set_at((self.size[0]-2, self.size[1]-2), bg)
        self.blit_surf.set_at((self.size[0]-2, self.size[1]-3), bg)
        self.blit_surf.set_at((self.size[0]-3, self.size[1]-2), bg)
    
        self.blit_surf.unlock()
