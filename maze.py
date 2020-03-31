# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 08:59:43 2020

@author: macrosoft
"""


from random import random
from kivy.app import App 
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle
from kivy.uix.filechooser import FileChooserListView, FileChooserIconView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image, AsyncImage
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.clock import Clock
import pandas as pd
import numpy as np




class MyPaintWidget(Widget):
    def __init__(self, **kwargs):
        # ON LOAD  
        super(MyPaintWidget, self).__init__(**kwargs)
        color = (1, 1, 1)
        maze_array = pd.read_csv("Maze.csv",header=None)
        maze_magnified = np.kron(maze_array, np.ones((10,10)))
        with self.canvas:
            print(self.width)
            Color(*color)
            d = 1.
            for i in range(maze_magnified.shape[0]):
                for j in range(maze_magnified.shape[1]):
                    if maze_magnified[i][j] > 0:
                        Ellipse(pos=(i, j), size=(d, d))
                                    
            
    def on_touch_down(self, touch):
        #color = (random(), random(), random())
        color = (1, 1, 1)
        with self.canvas:
            Color(*color)
            d = 100.
            #touch.ud['line'] = Line(points=(touch.x, touch.y))
            Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))

    #def on_touch_move(self, touch):
        #touch.ud['line'].points += [touch.x, touch.y]
    # def update(self, *args):
    #     print(self.width , "-",self.height)

class MyPaintApp(App):
    def build(self):
        # parent = MyBackground()
        # painter = MyPaintWidget()
        # parent.add_widget(painter)
        parent = MyPaintWidget()
        #Clock.schedule_interval(parent.update, 1.0/30.0)
        return parent

if __name__ == '__main__':
    MyPaintApp().run()
    
    
    
    
    