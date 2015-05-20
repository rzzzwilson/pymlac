#!/usr/bin/python

"""
The Imlac display.
"""


import pygame
from pygame.locals import *

from Globals import *


class Display(object):
    SYNC_HZ = 40
    SYNC_40HZ_CYCLE_COUNT = int(CYCLES_PER_SECOND / SYNC_HZ)

    def __init__(self, screen):
        self.screen = screen
        self.running = 0
        self.cycle_count = 0
        self.display = pygame.Surface((1024, 1024))
        self.Sync40hz = 1
        self.display.fill((0, 0, 0))

    def draw(self, dotted, oldx, oldy, x, y):
        oldx %= 1024
        oldy %= 1024
        x %= 1024
        y %= 1024
        pygame.draw.line(self.display, YELLOW, (oldx, 1024 - oldy), (x, 1024 - y))

    def flip(self):
        self.screen.blit(self.display, (0, 0))
        pygame.display.flip()
        self.display.fill((0, 0, 0))

    def syncclear(self):
        self.Sync40hz = 0
        self.cycle_count = self.SYNC_40HZ_CYCLE_COUNT

    def ready(self):
        return self.Sync40hz

    def tick(self, cycles):
        self.cycle_count -= cycles
        if self.cycle_count <= 0:
            self.Sync40hz = 1
