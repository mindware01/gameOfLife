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
        if event.type == 1026:
            return True
    return False


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
    pass


class Main:
    def __init__(self):
        settings.getSettings()
        pygame.display.init()

        config = configparser.ConfigParser()
        config.read('settings.ini')
        secs = config['life']['scale']
        # lifeMain.scale = int(scaleBox.getText())
        # lifeMain.popPercent = float(popBox.getText())
        # lifeMain.fullScreen = fullScreen.isEnabled()
        # lifeMain.xmax = int(widthLabelBox.getText())
        # lifeMain.ymax = int(heightLabelBox.getText())
        # lifeMain.ymax = int(heightLabelBox.getText())
        # styleString = str(styleBox.getSelected())
        # if styleString == 'None':
        #     styleString = "random"
        # setattr(lifeMain, styleString, True)

        self.fullScreen = False
        if config['life']['fullscreen'] == 'True':
            self.fullScreen = True
        self.scale = int(config['life']['scale'])
        self.popPercent = float(config['life']['poppercent'])
        self.maxNeighbors = 3
        if self.fullScreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.xmax = self.screen.get_width()  # Width of full screen in pixels including Windows display scale
            self.ymax = self.screen.get_height()  # Height of full screen in pixels including Windows display scale
        else:
            self.xmax = int(config['life']['screenwidth'])
            self.ymax = int(config['life']['screenheight'])
            self.screen = pygame.display.set_mode((self.xmax, self.ymax), 0, 24)  # New 24-bit screen

        self.cellLives = dict()
        self.xborder = self.xmax // self.scale
        self.yborder = self.ymax // self.scale
        self.cols = self.xmax // self.scale
        self.rows = self.ymax // self.scale
        self.prevBoard = None

        # add margin is needed
        self.margin = 0

        self.BLACK = (0, 0, 0)
        self.running = True
        self.drawn = -1

        self.maxCell = [self.screen.get_width(), self.screen.get_height()]

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
        styleString = config['life']['style']
        if styleString == 'None':
            styleString = "random"
        setattr(self, styleString, True)

        showDebugStr = config['life']['showdebuginfo']
        self.stats = False
        if showDebugStr == 'True':
            self.stats = True
        # print(self.stats)

    def updateLoop(self):
        initial_population = int(self.cols * self.rows * self.popPercent)

        while self.running or self.drawn:
            board = set([])

            # PATTERN TYPES

            # RANDOM
            if self.random:
                board = set((randint(self.margin, self.cols), randint(self.margin, self.rows)) for _ in range(initial_population))

            # CIRCLE
            elif self.circle:
                marginO = 80/self.scale
                marginI = 240/self.scale
                board = set((randint(self.margin, self.cols), randint(self.margin, self.rows)) for _ in range(initial_population))
                boardA = putInCircle(board, int(self.cols/4), int(self.rows/2), int(self.rows/2) - marginO)
                boardA = removeFromCircle(boardA, int(self.cols/4), int(self.rows/2), int(self.rows/2) - marginI)
                boardB = putInCircle(board, int(self.cols/4) * 3, int(self.rows/2), int(self.rows/2) - marginO)
                boardB = removeFromCircle(boardB, int(self.cols/4) * 3, int(self.rows/2), int(self.rows/2) - marginI)
                board = boardA.union(boardB)

            # CIRCLE EDGE
            elif self.circleEdge:
                for i in range(40):
                    center = int(self.rows/2 + i*20), int(self.rows/2)
                    radius = int(self.rows / 2 - 100)
                    # rads = 0
                    it = 5000
                    inc = (math.pi * 2) / it
                    angle = float(0)
                    for _ in range(it):
                        m = radius
                        x = int(center[0] + (m * math.cos(angle)))
                        y = int(center[1] + (m * math.sin(angle)))
                        board.add((x, y))
                        angle += inc

            # VERTICAL
            if self.vertical:
                board = set([])
                for row in range(int(self.rows)):
                    cell = (int(self.cols/8), row)
                    board.add(cell)
                for row in range(int(self.rows)):
                    cell = (int(self.cols/8) * 3, row)
                    board.add(cell)
                for row in range(int(self.rows)):
                    cell = (int(self.cols/8) * 5, row)
                    board.add(cell)
                for row in range(int(self.rows)):
                    cell = (int(self.cols/8) * 7, row)
                    board.add(cell)

            # HORIZONTAL
            if self.horizontal:
                board = set([])
                for row in range(32, int(self.rows), 64):
                    for col in range(int(self.cols)):
                        cell = (col, row)
                        board.add(cell)

            # RECTANGLES
            def rectLife(leftR, topR, w, h, ):
                # horizontal
                for c in range(w):  # top line
                    cellR = (leftR + c, topR)
                    board.add(cellR)

                for c in range(w):  # bottom line
                    cellR = (leftR + c, topR + h)
                    board.add(cellR)

                for r in range(h):  # left line
                    cellR = (leftR, topR + r)
                    board.add(cellR)

                for r in range(h):  # right line
                    cellR = (leftR + w, topR + r)
                    board.add(cellR)

            # rectangles variation
            if self.rectangles:
                board = set([])
                self.margin = int(self.rows/5)
                rTop = self.margin
                rLeft = self.margin
                rW = int(self.cols/2 - self.margin * 2)
                rH = int(self.margin)

                rectLife(rLeft, rTop, rW, rH)  # top left
                rTopBot = self.margin * 3
                rectLife(rLeft, rTopBot, rW, rH)  # bottom left
                rLeftRight = self.cols / 2 + self.margin
                rectLife(rLeftRight, rTopBot, rW, rH)  # bottom right
                rectLife(rLeftRight, rTop, rW, rH)  # top right

            # squares variation
            if self.squares:
                board = set([])
                self.margin = int(self.rows/5)
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
                rectLife(rL2, t2, rW, rH)    # bottom 8
                rectLife(rL3, t2, rW, rH)    # bottom 9
                rectLife(rL4, t2, rW, rH)    # bottom 10
                rectLife(rL5, t2, rW, rH)    # bottom 11
                rectLife(rL6, t2, rW, rH)    # bottom 12

            # WHOLE
            if self.whole:
                board = set([])
                rectLife(int(self.cols/2 - self.rows/2), 0, int(self.rows), int(self.rows)) #  - (self.scale * 1)

            # DRAWN
            if self.drawn:
                board = set([])
                board = drawLife.getDrawing(self)
                if len(board) < 100:
                    break
                if board is None:
                    continue
                self.running = True
                self.screen.fill(self.BLACK)

            board = self.iterate(board)

            # cell entropy
            self.cellLives = dict()
            for x, y in board:
                self.cellLives[str(x) + "," + str(y)] = CellLife()
            cell = (randint(0, self.maxCell[0]), randint(0, self.maxCell[1]))
            board.add(cell)
            cellL = CellLife()
            cellL.clr = [255, 255, 255]
            self.cellLives[keyStrGen(cell[0], cell[1])] = cellL

            done = 0
            while True:
                if self.running is False:
                    break
                self.screen.fill(self.BLACK)

                startD = time.time()
                for x, y in board:
                    if pyGameExit() is True:
                        self.running = False
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
                board = self.iterate(board)
                endI = time.time() - startI

                # STATS
                if self.stats:
                    text = self.font.render("Draw: {:.4f}".format(endD), True, self.fontColor)
                    textPos = text.get_rect(topleft=(8, 8))
                    self.screen.blit(text, textPos)
                    text = self.font.render("Iter: {:.4f}".format(endI), True, self.fontColor)
                    textPos = text.get_rect(topleft=(8, 24))
                    self.screen.blit(text, textPos)
                    text = self.font.render("Cells: {}".format(len(board)), True, self.fontColor)
                    textPos = text.get_rect(topleft=(8, 42))
                    self.screen.blit(text, textPos)
                pygame.display.flip()

                if done >= len(board):
                    self.screen.fill(self.BLACK)
                    pygame.display.flip()
                    print("done >>>>>>>>>>>>>>>>>>>>>>>>")
                    break

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
            if keyStr in self.cellLives:
                pass
            else:
                self.cellLives[keyStr] = CellLife()

        return new_board


class CellLife:
    def __init__(self):
        self.clr = [70, 0, 0]
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
        self.bEndVal = 80

        self.decayed = False

    def reset(self):
        self.__init__()

    def decay(self):
        if self.clr == [255, 255, 255]:  # last gasp flash
            self.clr = [0, 0, self.bEndVal]
            self.decayed = True
        if self.decayed:
            return True

        decInc = 2

        # RED
        if self.rState == self.rStateUp:
            if self.clr[0] < 255:
                self.clr[0] += decInc
            if self.clr[0] >= self.rPeakVal:
                self.rState = self.rStateStay
                self.gState = self.gStateUp
        elif self.rState == self.rStateFall and self.clr[0] > 0:
            self.clr[0] -= decInc
            if self.clr[0] <= 0:
                self.rState = 0
                # self.decayed = True
                self.clr = [0, 0, 70]
                self.bState = self.bStateUp

        # GREEN
        if self.gState == self.gStateUp:
            if self.clr[1] < 255:
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
            if self.clr[2] < 255:
                self.clr[2] += decInc
            if self.clr[2] >= self.bPeak:
                self.bState = self.bStateFall
        elif self.bState == self.bStateFall:
            self.clr[2] -= decInc
            if self.clr[2] == self.bEndVal + decInc:
                self.clr = [255, 255, 255]  # flash before decayed completely
        self.clr[0] = clamp(0, 255, self.clr[0])
        self.clr[1] = clamp(0, 255, self.clr[1])
        self.clr[2] = clamp(0, 255, self.clr[2])

        return self.decayed


def main(exit_trigger):
    life = Main()
    life.updateLoop()


if __name__ == "__main__":
    try:
        main_exit_trigger = threading.Event()
        # CTRL-C signal handler
        # used a lambda, because a proper function is too much code
        signal.signal(signal.SIGINT, lambda signum, frame: main_exit_trigger.set())
        main(main_exit_trigger)
    except KeyboardInterrupt:
        pass
