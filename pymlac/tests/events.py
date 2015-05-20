#!/usr/bin/python 
################################################################################
################################################################################

import sys
import pygame
from pygame.locals import *

class Test(object):
    def __init__(self):
        self.event = pygame.event.Event(USEREVENT + 1, mystr="test event")
        self.count = 100000

    def test(self):
        self.count -= 1
        if self.count < 0:
            self.count = 100000
            pygame.event.post(self.event)

def main():
    test = Test()
    pygame.init()
    screen = pygame.display.set_mode((100,100))

    while 1:
        test.test()
        for event in pygame.event.get():
            if event.type == USEREVENT + 1:
                print event.dict["mystr"]


if __name__ == '__main__':
    main()

