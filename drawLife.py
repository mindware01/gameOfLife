import time
from random import randint
import pygame
import threading
import signal
import math
import main

rectSize = 8
white = (255, 255, 255)


def getDrawing(life):
    board = set([])
    mouseDown = False
    drawing = True
    while drawing:
        for evt in pygame.event.get():
            if evt.type == pygame.MOUSEBUTTONDOWN:
                if evt.button == 3:
                    life.running = False
                    life.drawn = False
                    return None

                mouseDown = True
                x, y = evt.pos
                rect = x - rectSize/2, y - rectSize/2, rectSize, rectSize
                pygame.draw.rect(life.screen, white, rect)
                pygame.display.flip()
                board = addSets(rect, board, life)

            if evt.type == pygame.MOUSEMOTION and mouseDown:
                x, y = evt.pos
                rect = x - rectSize/2, y - rectSize/2, rectSize, rectSize
                pygame.draw.rect(life.screen, white, rect)
                pygame.display.flip()
                board = addSets(rect, board, life)

            if evt.type == pygame.MOUSEBUTTONUP and mouseDown:
                x, y = evt.pos
                rect = x - rectSize/2, y - rectSize/2, rectSize, rectSize
                pygame.draw.rect(life.screen, white, rect)
                pygame.display.flip()
                board = addSets(rect, board, life)
                drawing = False
                return board


def addSets(rect, board, life):
    newBoard = set([])
    nCells = rectSize * 2 / life.scale
    x, y = 0, 0
    for _ in range(int(rectSize / life.scale)):
        for _ in range(rectSize):
            newBoard.add(((x + rect[0])/life.scale, (y + rect[1])/life.scale))
            x += life.scale
        y += life.scale
        x = 0
    return board.union(newBoard)

