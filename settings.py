import pygame
import pygame_widgets
from pygame_widgets.textbox import TextBox
from pygame_widgets.toggle import Toggle
from pygame_widgets.dropdown import Dropdown
from pygame_widgets.button import Button
import configparser
import subprocess
import os

# pygame.init()

run = True


def getSettings():
    global run

    xmax = 500  # Width of screen in pixels
    ymax = 800  # Height of screen in pixels
    screen = pygame.display.set_mode((xmax, ymax), 0, 24)  # New 24-bit screen

    config = configparser.ConfigParser()
    if os.path.exists("{}\\{}".format(os.getcwd(), 'settings.ini')):
        config.read('settings.ini')
    else:
        config.add_section('life')
        config['life']['scale'] = '2'
        config['life']['poppercent'] = '0.06'
        config['life']['fullscreen'] = 'True'
        config['life']['screenwidth'] = '2000'
        config['life']['screenheight'] = '500'
        config['life']['style'] = 'random'
        config['life']['showdebuginfo'] = 'False'

    screen.fill((0, 0, 0))
    pygame.display.flip()

    x, y, m, col, row = 40, 40, 10, 200, 40
    font = pygame.font.Font("C:\\Windows\\Fonts\\DejaVuSansMono.ttf", 18)
    fontColor = (0, 255, 0)
    title1Label = font.render("Game of Life algorithm - John Horton Conway", True, fontColor)
    title1LabelPos = title1Label.get_rect(topleft=(x, y + m))

    y += (row + m)
    title2Label = font.render("GUI and Entropy - John Dole", True, fontColor)
    title2LabelPos = title2Label.get_rect(topleft=(x, y + m))

    y += (row + m)
    scaleLabel = font.render("Scale", True, fontColor)
    scaleLabelPos = scaleLabel.get_rect(topleft=(x, y + m))
    scaleBox = TextBox(screen, col, y, 40, 40, font=font, fontSize=32)
    scaleBox.setText(config["life"]["scale"])

    y += (row + m)
    popLabel = font.render("Population", True, fontColor)
    popLabelPos = scaleLabel.get_rect(topleft=(x, y + m))
    popBox = TextBox(screen, col, y, 60, 40, font=font, fontSize=32)
    popBox.setText(config["life"]["poppercent"])

    y += (row + m)
    fsLabel = font.render("Full Screen", True, fontColor)
    fsLabelPos = fsLabel.get_rect(topleft=(x, y + m))
    fsValStr = config['life']['fullscreen']
    fsVal = False
    if fsValStr == 'True':
        fsVal = True
    fullScreen = Toggle(screen, col + 15, y + m, 20, 20, font=font, fontSize=32,
                        startOn=fsVal)

    y += (row + m)
    widthLabel = font.render("Window Width", True, fontColor)
    widthLabelPos = scaleLabel.get_rect(topleft=(x, y + m))
    widthBox = TextBox(screen, col, y, 60, 40, font=font, fontSize=32)
    widthBox.setText(config["life"]["screenwidth"])

    y += (row + m)
    heightLabel = font.render("Window Height", True, fontColor)
    heightLabelPos = scaleLabel.get_rect(topleft=(x, y + m))
    heightBox = TextBox(screen, col, y, 60, 40, font=font, fontSize=32)
    heightBox.setText(config["life"]["screenheight"])

    y += (row + m)
    styleLabel = font.render("Life Style", True, fontColor)
    styleLabelPos = scaleLabel.get_rect(topleft=(x, y + m))

    choiceList = ['random', 'circle', 'circleEdge', 'vertical', 'horizontal', 'rectangles', 'squares', 'whole', 'drawn']
    styleBox = Dropdown(screen, col, y, 120, 40, font=font, fontSize=32,
                        name=config["life"]["style"], borderRadius=3,
                        choices=choiceList, values=[0, 1, 2, 3, 4, 5, 6, 7, 8])

    y += (row + m)
    debugLabel = font.render("Debug Info", True, fontColor)
    debugLabelPos = scaleLabel.get_rect(topleft=(x, y + m))
    debugVal = False
    if config['life']['showdebuginfo'] == 'True':
        debugVal = True
    debugToggle = Toggle(screen, col + 15, y + m, 20, 20, font=font, fontSize=32,
                         startOn=debugVal)

    run = True

    # lambda done: run = False

    def done():
        global run
        run = False

    y += (row + m)
    runBtn = Button(screen, x, y + m, 60, 50, text='GO', fontSize=50, radius=10,
                    onClick=done)

    while run:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
                quit()

        screen.fill((0, 0, 0))  # erase previous draw

        screen.blit(title1Label, title1LabelPos)
        screen.blit(title2Label, title2LabelPos)
        screen.blit(scaleLabel, scaleLabelPos)
        screen.blit(popLabel, popLabelPos)
        screen.blit(fsLabel, fsLabelPos)
        screen.blit(widthLabel, widthLabelPos)
        screen.blit(heightLabel, heightLabelPos)
        screen.blit(styleLabel, styleLabelPos)
        screen.blit(debugLabel, debugLabelPos)

        pygame_widgets.update(events)
        pygame.display.update()

    # collect values
    config['life']['scale'] = scaleBox.getText()
    config['life']['poppercent'] = popBox.getText()
    print(str(fullScreen.isEnabled()))
    config['life']['fullscreen'] = str(fullScreen.getValue())
    config['life']['screenwidth'] = widthBox.getText()
    config['life']['screenheight'] = heightBox.getText()
    styleString = str(styleBox.getSelected())
    if styleString == 'None':
        config['life']['style'] = "random"
    else:
        config['life']['style'] = choiceList[int(styleString)]
    print(str(debugToggle.isEnabled()))
    config['life']['showdebuginfo'] = str(debugToggle.getValue())
    with open('settings.ini', 'w') as configfile:
        config.write(configfile)
    print("run >>>>>>>")
    pygame.display.quit()


if __name__ == "__main__":
    getSettings()
