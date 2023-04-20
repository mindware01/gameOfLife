#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# pygame GUI + cellLife entropy sim (c) 2023 John Dole
# See LICENSE.rst for details.
# PYTHON_ARGCOMPLETE_OK

"""
Conway's game of life.

Adapted from:
http://codereview.stackexchange.com/a/108121
"""

import time
from random import randint
import pygame
import threading
import signal
import math
import drawLife
import settings
import configparser
import os

os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()


def neighbors(cell):
    x, y = cell
    yield x - 1, y - 1
    yield x, y - 1
    yield x + 1, y - 1
    yield x - 1, y
    yield x + 1, y
    yield x - 1, y + 1
    yield x, y + 1
    yield x + 1, y + 1


def pyGameExit():
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return True


def keyStrGen(x, y):
    return str(x) + "," + str(y)


def clamp(l, h, v):
    if v < l:
        return l
    if v > h:
        return h
    return v


def putInCircle(board, cx, cy, r):
    new_board = set([])
    for cell in board:
        x, y = cell
        hypotenuse = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        if hypotenuse <= r:
            new_board.add(cell)
    return new_board


def removeFromCircle(board, cx, cy, r):
    new_board = set([])
    for cell in board:
        x, y = cell
        hypotenuse = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        if hypotenuse >= r:
            new_board.add(cell)
    return new_board


def isGlider(x, Y):
    pass  # TODO: identify glider for special coloring


class Main:
    def __init__(self):
        self.config = None

        self.fullScreen = True
        self.scale = 2
        self.popPercent = 0.06
        self.maxNeighbors = 3
        self.screen = None
        self.xmax = 0
        self.ymax = 0

        self.cellLives = None
        self.xborder = self.xmax // self.scale
        self.yborder = self.ymax // self.scale
        self.cols = self.xmax // self.scale
        self.rows = self.ymax // self.scale
        self.prevBoard = None

        # add margin if needed
        self.margin = 0

        self.BLACK = (0, 0, 0)
        self.running = False
        self.drawn = -1
        self.maxCell = [0, 0]

        # font
        self.font = pygame.font.Font("C:\\Windows\\Fonts\\DejaVuSansMono.ttf", 18)
        self.fontColor = (0, 255, 0)

        # SEED STYLES
        self.random = False
        self.circle = False
        self.circleEdge = False
        self.vertical = False
        self.horizontal = False
        self.rectangles = False
        self.squares = False
        self.whole = False
        self.drawn = False
        self.addToDrawing = False
        self.stats = True

        self.settings = None

        self.more_board = None
        self.board = None
        self.count = 0

    def updateLoop(self):
        while True:
            self.settings = settings.Settings(self)
            self.settings.getSettings()
            self.settings.close()

            # switch loops
            self.settings.run = False
            self.running = True

            # apply settings
            self.config = self.settings.config
            if self.config['life']['fullscreen'] == 'True':
                self.fullScreen = True
            else:
                self.fullScreen = False
            self.scale = int(self.config['life']['scale'])
            self.popPercent = float(self.config['life']['poppercent'])
            styleString = self.config['life']['style']
            if styleString == 'None':
                styleString = "random"
            setattr(self, styleString, True)
            showDebugStr = self.config['life']['showdebuginfo']
            self.stats = False
            if showDebugStr == 'True':
                self.stats = True
            else:
                self.stats = False

            if self.fullScreen:
                self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                self.xmax = self.screen.get_width()  # Width of full screen in pixels including Windows display scale
                self.ymax = self.screen.get_height()  # Height of full screen in pixels including Windows display scale
            else:
                self.xmax = int(self.config['life']['screenwidth'])
                self.ymax = int(self.config['life']['screenheight'])
                self.screen = pygame.display.set_mode((self.xmax, self.ymax), 0, 24)  # New 24-bit screen
            self.settings.screen = self.screen
            self.xborder = self.xmax // self.scale
            self.yborder = self.ymax // self.scale
            self.cols = self.xmax // self.scale
            self.rows = self.ymax // self.scale
            self.maxCell = [self.screen.get_width(), self.screen.get_height()]

            initial_population = int(self.cols * self.rows * self.popPercent)

            self.more_board = None
            while self.running or self.drawn:
                self.count = 0
                # board = set([])

                # PATTERN TYPES

                # RANDOM
                if self.random:
                    self.board = set((randint(self.margin, self.cols), randint(self.margin, self.rows)) for _ in
                                     range(initial_population))

                # CIRCLE
                elif self.circle:
                    marginO = 80 / self.scale
                    marginI = 240 / self.scale
                    self.board = set((randint(self.margin, self.cols), randint(self.margin, self.rows)) for _ in
                                     range(initial_population))
                    boardA = putInCircle(self.board, int(self.cols / 4), int(self.rows / 2),
                                         int(self.rows / 2) - marginO)
                    boardA = removeFromCircle(boardA, int(self.cols / 4), int(self.rows / 2),
                                              int(self.rows / 2) - marginI)
                    boardB = putInCircle(self.board, int(self.cols / 4) * 3, int(self.rows / 2),
                                         int(self.rows / 2) - marginO)
                    boardB = removeFromCircle(boardB, int(self.cols / 4) * 3, int(self.rows / 2),
                                              int(self.rows / 2) - marginI)
                    self.board = boardA.union(boardB)

                # CIRCLE EDGE
                elif self.circleEdge:
                    for i in range(40):
                        center = int(self.rows / 2 + i * 20), int(self.rows / 2)
                        radius = int(self.rows / 2 - 100)
                        it = 5000
                        inc = (math.pi * 2) / it
                        angle = float(0)
                        for _ in range(it):
                            m = radius
                            x = int(center[0] + (m * math.cos(angle)))
                            y = int(center[1] + (m * math.sin(angle)))
                            self.board.add((x, y))
                            angle += inc

                # VERTICAL
                if self.vertical:
                    self.board = set([])
                    for row in range(int(self.rows)):
                        cell = (int(self.cols / 8), row)
                        self.board.add(cell)
                    for row in range(int(self.rows)):
                        cell = (int(self.cols / 8) * 3, row)
                        self.board.add(cell)
                    for row in range(int(self.rows)):
                        cell = (int(self.cols / 8) * 5, row)
                        self.board.add(cell)
                    for row in range(int(self.rows)):
                        cell = (int(self.cols / 8) * 7, row)
                        self.board.add(cell)

                # HORIZONTAL
                if self.horizontal:
                    self.board = set([])
                    for row in range(32, int(self.rows), 64):
                        for col in range(int(self.cols)):
                            cell = (col, row)
                            self.board.add(cell)

                # RECTANGLES
                def rectLife(leftR, topR, w, h, ):
                    for c in range(w):  # top line
                        cellR = (leftR + c, topR)
                        self.board.add(cellR)

                    for c in range(w):  # bottom line
                        cellR = (leftR + c, topR + h)
                        self.board.add(cellR)

                    for r in range(h):  # left line
                        cellR = (leftR, topR + r)
                        self.board.add(cellR)

                    for r in range(h):  # right line
                        cellR = (leftR + w, topR + r)
                        self.board.add(cellR)

                # rectangles variation
                if self.rectangles:
                    self.board = set([])
                    self.margin = int(self.rows / 5)
                    rTop = self.margin
                    rLeft = self.margin
                    rW = int(self.cols / 2 - self.margin * 2)
                    rH = int(self.margin)

                    rectLife(rLeft, rTop, rW, rH)  # top left
                    rTopBot = self.margin * 3
                    rectLife(rLeft, rTopBot, rW, rH)  # bottom left
                    rLeftRight = self.cols / 2 + self.margin
                    rectLife(rLeftRight, rTopBot, rW, rH)  # bottom right
                    rectLife(rLeftRight, rTop, rW, rH)  # top right

                # squares variation
                if self.squares:
                    self.board = set([])
                    self.margin = int(self.rows / 5)
                    rTop = self.margin
                    rLeft = self.margin / 2
                    rW = self.margin
                    rH = self.margin

                    rectLife(rLeft, rTop, rW, rH)  # top 1
                    rL2 = rLeft + self.margin * 2
                    rectLife(rL2, rTop, rW, rH)  # top 2
                    rL3 = rLeft + self.margin * 4
                    rectLife(rL3, rTop, rW, rH)  # top 3
                    rL4 = rLeft + self.margin * 6
                    rectLife(rL4, rTop, rW, rH)  # top 4
                    rL5 = rLeft + self.margin * 8
                    rectLife(rL5, rTop, rW, rH)  # top 5
                    rL6 = rLeft + self.margin * 10
                    rectLife(rL6, rTop, rW, rH)  # top 6
                    t2 = self.margin * 3
                    rectLife(rLeft, t2, rW, rH)  # bottom 7
                    rectLife(rL2, t2, rW, rH)  # bottom 8
                    rectLife(rL3, t2, rW, rH)  # bottom 9
                    rectLife(rL4, t2, rW, rH)  # bottom 10
                    rectLife(rL5, t2, rW, rH)  # bottom 11
                    rectLife(rL6, t2, rW, rH)  # bottom 12

                # WHOLE
                if self.whole:
                    self.board = set([])
                    rectLife(int(self.cols / 2 - self.rows / 2), 0, int(self.rows),
                             int(self.rows))  # - (self.scale * 1)

                # DRAWN
                if self.drawn:
                    if self.addToDrawing:
                        self.addToDrawing = False
                        self.more_board = drawLife.getDrawing(self, True)
                        temp_board = self.board.copy()
                        self.board = temp_board.union(self.more_board)
                    else:
                        self.board = set([])
                        self.board = drawLife.getDrawing(self, False)
                    if len(self.board) < 100:
                        break
                    if self.board is None:
                        continue
                    self.running = True
                    self.screen.fill(self.BLACK)

                self.board = self.iterate(self.board)

                # cell entropy
                self.addColorEntropy(self.board)

                done = 0
                while True:
                    if self.running is False or self.addToDrawing:
                        break
                    self.screen.fill(self.BLACK)

                    startD = time.time()
                    for x, y in self.board:
                        if self.drawn:
                            for evt in pygame.event.get():
                                print(evt.type)
                                if evt.type == pygame.MOUSEBUTTONDOWN:
                                    self.addToDrawing = True
                                    break
                                if evt.type == 768:  # tcod key down - quit to settings
                                    self.running = False
                                    self.drawn = False
                                    break
                        if self.addToDrawing:
                            break
                        if pyGameExit() is True:
                            self.running = False
                            break
                        if self.running is False:
                            break

                        # glider = isGlider(x, y)
                        keyStr = keyStrGen(x, y)
                        if keyStr in self.cellLives:
                            cellLife = self.cellLives[keyStr]
                        else:
                            cellLife = CellLife()
                            self.cellLives[keyStr] = cellLife
                        left = x * self.scale
                        top = y * self.scale
                        pygame.draw.rect(self.screen, cellLife.clr, (left, top, self.scale, self.scale))
                        if cellLife.decay():
                            done += 1
                        else:
                            done = 0
                        self.cellLives[keyStr] = cellLife

                    endD = time.time() - startD

                    startI = time.time()
                    self.board = self.iterate(self.board)
                    endI = time.time() - startI
                    self.count += 1

                    # STATS
                    if self.stats:
                        text = self.font.render("Draw:  {:.4f}".format(endD), True, self.fontColor)
                        textPos = text.get_rect(topleft=(8, 8))
                        self.screen.blit(text, textPos)
                        text = self.font.render("Iter:  {:.4f}".format(endI), True, self.fontColor)
                        textPos = text.get_rect(topleft=(8, 24))
                        self.screen.blit(text, textPos)
                        text = self.font.render("Cells: {}".format(len(self.board)), True, self.fontColor)
                        textPos = text.get_rect(topleft=(8, 42))
                        self.screen.blit(text, textPos)
                        text = self.font.render("Count: {}".format(self.count), True, self.fontColor)
                        textPos = text.get_rect(topleft=(8, 58))
                        self.screen.blit(text, textPos)
                    pygame.display.flip()

                    if done >= len(self.board):
                        self.screen.fill(self.BLACK)
                        pygame.display.flip()
                        break
            self.screen = None
            self.running = False

    def iterate(self, board):
        new_board = set([])
        candidates = board.union(set(n for cell in board for n in neighbors(cell)))
        for cell in candidates:
            x, y = cell
            if x > self.xborder or y > self.yborder:
                continue
            if x < 0 or y < 0:
                continue

            count = sum((n in board) for n in neighbors(cell))
            if count == self.maxNeighbors or (count == 2 and cell in board):
                new_board.add(cell)

            # insert new cellLife in new board if needed
            keyStr = keyStrGen(x, y)
            if self.cellLives is not None:
                if keyStr in self.cellLives:
                    pass
                else:
                    self.cellLives[keyStr] = CellLife()

        return new_board

    def addColorEntropy(self, brd):
        self.cellLives = dict()
        for x, y in brd:
            if keyStrGen(x, y) in self.cellLives is False:
                self.cellLives[str(x) + "," + str(y)] = CellLife()


class CellLife:
    def __init__(self):
        self.clr = [70, 0, 0]
        self.maxIntensity = 255
        self.rState = 1
        self.gState = 0
        self.bState = 0

        self.rStateUp = 1
        self.rStateStay = 2
        self.rStateFall = 3
        self.rPeaked = False
        self.rPeakVal = 255
        self.rStay = False
        self.rDone = False

        self.gStart = False
        self.gStartVal = 25
        self.gPeaked = False
        self.gPeakVal = 150
        self.gStateUp = 1
        self.gStateFall = 3
        self.bPeaked = False
        self.gDone = False

        self.bStart = False
        self.bStartVal = 0
        self.bStateUp = 1
        self.bPeak = 254
        self.bStateFall = 3
        self.bEndVal = 90

        self.decayed = False

    def reset(self):
        self.__init__()

    def decay(self):
        if self.clr == [self.maxIntensity - 1, self.maxIntensity - 1, self.maxIntensity - 1]:  # last gasp flash
            self.clr = [0, 0, self.bEndVal]
            self.decayed = True
        if self.decayed:
            return True

        decInc = 2

        # RED
        if self.rState == self.rStateUp:
            if self.clr[0] < self.maxIntensity:
                self.clr[0] += decInc
            if self.clr[0] >= self.rPeakVal:
                self.rState = self.rStateStay
                self.gState = self.gStateUp
        elif self.rState == self.rStateFall and self.clr[0] > 0:
            self.clr[0] -= decInc
            if self.clr[0] <= 0:
                self.rState = 0
                self.clr = [0, 0, 70]
                self.bState = self.bStateUp

        # GREEN
        if self.gState == self.gStateUp:
            if self.clr[1] < self.maxIntensity:
                self.clr[1] += decInc
            if self.clr[1] >= self.gPeakVal:
                self.gState = self.gStateFall
                self.rState = self.rStateFall
        elif self.clr[1] > 0:
            self.clr[1] -= decInc * 2
            if self.clr[1] <= 0:
                self.gDone = 0

        # BLUE
        if self.bState == self.bStateUp:
            if self.clr[2] < self.maxIntensity:
                self.clr[2] += decInc
            if self.clr[2] >= self.bPeak:
                self.bState = self.bStateFall
        elif self.bState == self.bStateFall:
            self.clr[2] -= decInc
            if self.clr[2] == self.bEndVal + decInc:
                # flash before decayed completely
                # [self.maxIntensity, self.maxIntensity, self.maxIntensity]
                # is reserved for special entities like spawned spaceships
                self.clr = [self.maxIntensity - 1, self.maxIntensity - 1, self.maxIntensity - 1]
        self.clr[0] = clamp(0, self.maxIntensity, self.clr[0])
        self.clr[1] = clamp(0, self.maxIntensity, self.clr[1])
        self.clr[2] = clamp(0, self.maxIntensity, self.clr[2])

        return self.decayed


def main(exit_trigger):
    life = Main()
    # while True:
    life.updateLoop()


if __name__ == "__main__":
    try:
        main_exit_trigger = threading.Event()
        # CTRL-C signal handler
        # used a lambda, because a proper function is too much code
        signal.signal(signal.SIGINT, lambda signum, frame: main_exit_trigger.set())
        # while True:
        main(main_exit_trigger)
    except KeyboardInterrupt:
        pass
