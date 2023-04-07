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


class Settings:
    def __init__(self, life):
        xmax = 500  # Width of screen in pixels
        ymax = 800  # Height of screen in pixels

        self.life = life
        if self.life.screen is None:
            self.screen = pygame.display.set_mode((xmax, ymax), 0, 24)
        else:
            self.screen = life.screen

        self.config = configparser.ConfigParser()
        if os.path.exists("{}\\{}".format(os.getcwd(), 'settings.ini')):
            self.config.read('settings.ini')
        else:
            self.config.add_section('life')
            self.config['life']['scale'] = '2'
            self.config['life']['poppercent'] = '0.06'
            self.config['life']['fullscreen'] = 'True'
            self.config['life']['screenwidth'] = '2000'
            self.config['life']['screenheight'] = '500'
            self.config['life']['style'] = 'random'
            self.config['life']['showdebuginfo'] = 'False'

        self.screen.fill((0, 0, 0))
        pygame.display.flip()

        x, y, m, col, row = 40, 40, 10, 200, 40
        self.font = pygame.font.Font("C:\\Windows\\Fonts\\DejaVuSansMono.ttf", 18)
        self.fontColor = (0, 255, 0)
        self.title1Label = self.font.render("Game of Life algorithm - John Horton Conway", True, self.fontColor)
        self.title1LabelPos = self.title1Label.get_rect(topleft=(x, y + m))

        y += (row + m)
        self.title2Label = self.font.render("GUI and Entropy - John Dole", True, self.fontColor)
        self.title2LabelPos = self.title2Label.get_rect(topleft=(x, y + m))

        y += (row + m)
        self.scaleLabel = self.font.render("Scale", True, self.fontColor)
        self.scaleLabelPos = self.scaleLabel.get_rect(topleft=(x, y + m))
        self.scaleBox = TextBox(self.screen, col, y, 40, 40, font=self.font, fontSize=32)
        self.scaleBox.setText(self.config["life"]["scale"])

        y += (row + m)
        self.popLabel = self.font.render("Population", True, self.fontColor)
        self.popLabelPos = self.scaleLabel.get_rect(topleft=(x, y + m))
        self.popBox = TextBox(self.screen, col, y, 60, 40, font=self.font, fontSize=32)
        self.popBox.setText(self.config["life"]["poppercent"])

        y += (row + m)
        self.fsLabel = self.font.render("Full Screen", True, self.fontColor)
        self.fsLabelPos = self.fsLabel.get_rect(topleft=(x, y + m))
        fsValStr = self.config['life']['fullscreen']
        fsVal = False
        if fsValStr == 'True':
            fsVal = True
        self.fullScreen = Toggle(self.screen, col + 15, y + m, 20, 20, font=self.font, fontSize=32,
                                 startOn=fsVal)

        y += (row + m)
        self.widthLabel = self.font.render("Window Width", True, self.fontColor)
        self.widthLabelPos = self.scaleLabel.get_rect(topleft=(x, y + m))
        self.widthBox = TextBox(self.screen, col, y, 60, 40, font=self.font, fontSize=32)
        self.widthBox.setText(self.config["life"]["screenwidth"])

        y += (row + m)
        self.heightLabel = self.font.render("Window Height", True, self.fontColor)
        self.heightLabelPos = self.scaleLabel.get_rect(topleft=(x, y + m))
        self.heightBox = TextBox(self.screen, col, y, 60, 40, font=self.font, fontSize=32)
        self.heightBox.setText(self.config["life"]["screenheight"])

        y += (row + m)
        self.styleLabel = self.font.render("Life Style", True, self.fontColor)
        self.styleLabelPos = self.scaleLabel.get_rect(topleft=(x, y + m))

        self.choiceList = ['random', 'circle', 'circleEdge', 'vertical', 'horizontal', 'rectangles', 'squares', 'whole',
                           'drawn']
        self.styleBox = Dropdown(self.screen, col, y, 120, 40, font=self.font, fontSize=32,
                                 name=self.config["life"]["style"], borderRadius=3,
                                 choices=self.choiceList, values=[0, 1, 2, 3, 4, 5, 6, 7, 8])

        y += (row + m)
        self.debugLabel = self.font.render("Debug Info", True, self.fontColor)
        self.debugLabelPos = self.scaleLabel.get_rect(topleft=(x, y + m))
        debugVal = False
        if self.config['life']['showdebuginfo'] == 'True':
            debugVal = True
        self.debugToggle = Toggle(self.screen, col + 15, y + m, 20, 20, font=self.font, fontSize=32,
                                  startOn=debugVal)

        y += (row + m)
        self.runBtn = Button(self.screen, x, y + m, 60, 50, text='GO', fontSize=50, radius=10,
                             onClick=self.done)

        self.run = True

    def done(self):
        self.run = False

    def getSettings(self):

        while self.run:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.run = False
                    quit()

            self.screen.fill((0, 0, 0))  # erase previous draw

            self.screen.blit(self.title1Label, self.title1LabelPos)
            self.screen.blit(self.title2Label, self.title2LabelPos)
            self.screen.blit(self.scaleLabel, self.scaleLabelPos)
            self.screen.blit(self.popLabel, self.popLabelPos)
            self.screen.blit(self.fsLabel, self.fsLabelPos)
            self.screen.blit(self.widthLabel, self.widthLabelPos)
            self.screen.blit(self.heightLabel, self.heightLabelPos)
            self.screen.blit(self.styleLabel, self.styleLabelPos)
            self.screen.blit(self.debugLabel, self.debugLabelPos)

            if self.life.running is False:
                try:
                    pygame_widgets.update(events)
                    pygame.display.update()
                except Exception as e:
                    print(e)

    def close(self):
        # collect values
        self.config['life']['scale'] = self.scaleBox.getText()
        self.config['life']['poppercent'] = self.popBox.getText()
        self.config['life']['fullscreen'] = str(self.fullScreen.getValue())
        self.config['life']['screenwidth'] = self.widthBox.getText()
        self.config['life']['screenheight'] = self.heightBox.getText()
        styleString = str(self.styleBox.getSelected())
        if styleString == 'None':
            self.config['life']['style'] = "random"
        else:
            self.config['life']['style'] = self.choiceList[int(styleString)]
        self.config['life']['showdebuginfo'] = str(self.debugToggle.getValue())
        with open('settings.ini', 'w') as configfile:
            self.config.write(configfile)
            configfile.close()

        pygame_widgets.WidgetHandler.removeWidget(self.scaleBox)
        pygame_widgets.WidgetHandler.removeWidget(self.popBox)
        pygame_widgets.WidgetHandler.removeWidget(self.fullScreen)
        pygame_widgets.WidgetHandler.removeWidget(self.widthBox)
        pygame_widgets.WidgetHandler.removeWidget(self.heightBox)
        pygame_widgets.WidgetHandler.removeWidget(self.styleBox)
        pygame_widgets.WidgetHandler.removeWidget(self.debugToggle)
