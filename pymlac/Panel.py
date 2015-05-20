#!/usr/bin/python
################################################################################
# The Imlac panel.
################################################################################

import os

import pygame
from pygame.locals import *

from Globals import *

class Panel(object):
    def __init__(self, version, screen, datafont, labelfont):
        self.version = version
        self.screen = screen
        self.datafont = datafont
        self.labelfont = labelfont
        self.img_panel = pygame.image.load(os.path.join('images', 'panel.png'))
        self.img_ledoff = pygame.image.load(os.path.join('images', 'led_off.png'))
        self.img_ledon = pygame.image.load(os.path.join('images', 'led_on.png'))
        self.img_quitbutton = pygame.image.load(os.path.join('images', 'quit.png'))
        self.img_haltbutton = pygame.image.load(os.path.join('images', 'halt.png'))
        self.img_runbutton = pygame.image.load(os.path.join('images', 'run.png'))
        self.img_singlebutton = pygame.image.load(os.path.join('images', 'singlestep.png'))
        self.img_checkboxon = pygame.image.load(os.path.join('images', 'checkon.png'))
        self.img_checkboxoff = pygame.image.load(os.path.join('images', 'checkoff.png'))
        self.img_radiobuttonon = pygame.image.load(os.path.join('images', 'radioon.png'))
        self.img_radiobuttonoff = pygame.image.load(os.path.join('images', 'radiooff.png'))

        self.img_panel.blit(self.datafont.render(self.version, 1, BLACK), VERSION_POSN)
        self.draw_databox('ptr', BOX_POSNX, PTR_BOX_POSNY, BOX_WIDTH, BOX_HEIGHT)
        self.draw_databox('ptp', BOX_POSNX, PTP_BOX_POSNY, BOX_WIDTH, BOX_HEIGHT)
        self.draw_databox('ttyin', BOX_POSNX, TTYIN_BOX_POSNY, BOX_WIDTH, BOX_HEIGHT)
        self.draw_databox('ttyout', BOX_POSNX, TTYOUT_BOX_POSNY, BOX_WIDTH, BOX_HEIGHT)

        self.img_panel.blit(self.img_ledoff, (LEDL_POSNX, LEDAC_POSNY))
        self.img_panel.blit(self.labelfont.render('l', 1, BLACK), (LEDL_POSNX, LEDAC_POSNY + LEDAC_LABEL_OFFSETY))
        self.img_panel.blit(self.labelfont.render('ac', 1, BLACK), (LEDAC_POSNX, LEDAC_POSNY + LEDAC_LABEL_OFFSETY))
        led_posnx = LEDAC_POSNX
        mark_count = 1
        for i in LED_BIT_RANGE:
            if (mark_count == 0):
                mark_count = 3
                pygame.draw.line(self.img_panel, GREY, (led_posnx - 1, LEDAC_POSNY + 10), (led_posnx - 1, LEDAC_POSNY + 15))
            self.img_panel.blit(self.img_ledoff, (led_posnx, LEDAC_POSNY))
            led_posnx += LED_BIT_OFFSETX
            mark_count -= 1

        self.draw_divider(FILE_ROM_DIVIDER, PANEL_WIDTH)

        self.img_panel.blit(self.labelfont.render('pc', 1, BLACK), (LEDPC_POSNX, LEDPC_POSNY + LEDPC_LABEL_OFFSETY))
        led_posnx = LEDPC_POSNX
        mark_count = 1
        for i in LED_BIT_RANGE:
            if (mark_count == 0):
                mark_count = 3
                pygame.draw.line(self.img_panel, GREY, (led_posnx - 1, LEDPC_POSNY + 10), (led_posnx - 1, LEDPC_POSNY + 15))
            self.img_panel.blit(self.img_ledoff, (led_posnx, LEDPC_POSNY))
            led_posnx += LED_BIT_OFFSETX
            mark_count -= 1

        self.draw_divider(ROM_MON_DIVIDERY, PANEL_WIDTH)

        self.draw_divider(MON_LED_DIVIDERY, PANEL_WIDTH)

        self.draw_databox('l', REGL_BOX_POSNX, REGL_BOX_POSNY, REGL_BOX_WIDTH, REGL_BOX_HEIGHT)
        self.draw_databox('ac', REGAC_BOX_POSNX, REGAC_BOX_POSNY, REGAC_BOX_WIDTH, REGAC_BOX_HEIGHT)
        self.draw_databox('pc', REGPC_BOX_POSNX, REGPC_BOX_POSNY, REGPC_BOX_WIDTH, REGPC_BOX_HEIGHT)

        self.draw_databox('dx', REGDX_BOX_POSNX, REGDX_BOX_POSNY, REGDX_BOX_WIDTH, REGDX_BOX_HEIGHT)
        self.draw_databox('dpc', REGDPC_BOX_POSNX, REGDPC_BOX_POSNY, REGDPC_BOX_WIDTH, REGDPC_BOX_HEIGHT)
        self.draw_databox('dy', REGDY_BOX_POSNX, REGDY_BOX_POSNY, REGDY_BOX_WIDTH, REGDY_BOX_HEIGHT)

        self.draw_divider(REGS_MON_DIVIDERY, PANEL_WIDTH)

        self.draw_divider(BOX_BOT_DIVIDERY, PANEL_WIDTH)

        self.img_panel.blit(self.labelfont.render('boot rom:', 1, BLACK), BOOTROM_LABEL_POSN)
        self.draw_checkbox(BOOTROM_WRITABLE_POSN, 0)
        self.img_panel.blit(self.labelfont.render('is writable', 1, BLACK), BOOTROM_WRITABLE_LABEL_POSN)
        self.draw_radiobutton(BOOTROM_LOADPTR_RADIO_POSN, 1)
        self.img_panel.blit(self.labelfont.render('papertape', 1, BLACK), BOOTROM_LOADPTR_LABEL_POSN)
        self.draw_radiobutton(BOOTROM_LOADTTY_RADIO_POSN, 0)
        self.img_panel.blit(self.labelfont.render('teletype', 1, BLACK), BOOTROM_LOADTTY_LABEL_POSN)

        self.img_panel.blit(self.img_quitbutton, QUITBUTTON_POSN)
        self.img_panel.blit(self.img_haltbutton, HALTBUTTON_POSN)
        self.img_panel.blit(self.img_singlebutton, SINGLESTEPBUTTON_POSN)

        #
        self.screen.blit(self.img_panel, (1024,0))
        pygame.display.flip()

    def draw_checkbox(self, posn, on):
        if (on):
            self.img_panel.blit(self.img_checkboxon, posn)
        else:
            self.img_panel.blit(self.img_checkboxoff, posn)

    def draw_databox(self, label, x, y, width, height):
        if (len(label) > 0):
            self.img_panel.blit(self.labelfont.render(label, 1, BLACK), (x, y + LABEL_OFFSETY))
        pygame.draw.rect(self.img_panel, BLACK, ((x, y), (width, height)), 1)
        self.img_panel.fill(WHITE, ((x + 1,y + 1),(width - 2,height - 2)))

    def draw_divider(self, y, width):                                                                      
        pygame.draw.line(self.img_panel, LIGHTGREY, (0, y), (width - 1, y))
        pygame.draw.line(self.img_panel, BLACK, (0, y+1), (width - 1, y+1))

    def draw_leds(self, y, value):
        posn = LEDAC_SCREEN_POSNX
        for i in LED_BIT_RANGE:
            if (value & 1 << i):
                self.screen.blit(self.img_ledon, (posn, y))
            else:
                self.screen.blit(self.img_ledoff, (posn, y))
            posn += LED_BIT_OFFSETX

    def draw_radiobutton(self, posn, on):
        if (on):
            self.img_panel.blit(self.img_radiobuttonon, posn)
        else:
            self.img_panel.blit(self.img_radiobuttonoff, posn)

    def updateAC(self, value):
        self.draw_leds(LEDAC_SCREEN_POSNY, value)

    def updateL(self, value):
        if value:
            self.screen.blit(self.img_ledon, (LEDL_POSNX, LEDAC_SCREEN_POSNY))
        else:
            self.screen.blit(self.img_ledoff, (LEDL_POSNX, LEDAC_SCREEN_POSNY))
        pass

    def updatePC(self, value):
        self.draw_leds(LEDPC_SCREEN_POSNY, value)

    def setromstate(self, type, write):
        pass

    def setptrstate(self, file, on, eof):
        pass

    def setptpstate(self, file, on, eof):
        pass

    def setttyinstate(self, file, on, eof):
        pass

    def setttyoutstate(self, file, on, eof):
        pass

    def updatescreen(self, screen):
        pass
