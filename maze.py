# Importing the libraries
import numpy as np
from random import random, randint
import matplotlib.pyplot as plt
import time

# Kivy lib
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse, Line
from kivy.config import Config
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from random import random
from kivy.app import App 
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle
from kivy.uix.filechooser import FileChooserListView, FileChooserIconView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image, AsyncImage
import pandas as pd
from datetime import datetime





# Run parameters
maze_file = ["maze_train0","maze_train1","maze_train2","maze_level1","maze_level2","maze_level3"]
start_pointX = [800,0,800,800,435,585]
start_pointY = [0,600,0,190,0,0]
end_pointX =   [0,800,0,0,500,585]
end_pointY =   [600,0,600,400,600,600]


run_number = 3

maze_array = pd.read_csv(maze_file[run_number] + ".csv",header=None)
maze_magnified = np.kron(maze_array, np.ones((10,10)))  # Magnify from 80x60 to 800x600

# Initializing the map
first_update = True
def init():

    global goal_x
    global goal_y

    white_space = maze_magnified.copy()
    goal_x = end_pointX[run_number]
    goal_y = end_pointY[run_number]


# Creating the agent class

class Agent(Widget):
    
    angle = NumericProperty(0)

# Creating the MainWidget class

class MainWidget(Widget):

    agent = ObjectProperty(None)
    sensor1 = ObjectProperty(None)
    sensor2 = ObjectProperty(None)
    sensor3 = ObjectProperty(None)
    
    vel_x = NumericProperty(start_pointX[run_number])
    vel_y = NumericProperty(start_pointX[run_number])
    position = ReferenceListProperty(vel_x,vel_y)
  

    def serve_agent(self):
        self.agent.pos = Vector(self.position) + self.pos
        
    def update(self, _x):
        print("MainWidget Update")


# Adding the painting tools

class MyPaintWidget(Widget):
    def __init__(self, **kwargs):
        # ON LOAD  
        super(MyPaintWidget, self).__init__(**kwargs)
        color = (1, 0, 0)
        with self.canvas:
            #print(self.width)
            Color(*color)
            d = 1.
            for i in range(maze_magnified.shape[0]):
                for j in range(maze_magnified.shape[1]):
                    if maze_magnified[i][j] > 0:
                        Ellipse(pos=(i, j), size=(d, d))

          

# Adding the API Buttons (start, pause, save and load)

class MainApp(App):

    def build(self):
        self.parent = MainWidget()
        self.parent.serve_agent()
        self.My_Clock = Clock
        self.painter = MyPaintWidget()
        startbtn = Button(text = 'Start')
        pausebtn = Button(text = 'Pause', pos = (self.parent.width, 0))
        savebtn = Button(text = 'Save Memory', pos = (2 *self.parent.width, 0))
        loadbtn = Button(text = 'Load Memory', pos = (3 * self.parent.width, 0))

        startbtn.bind(on_release = self.start)
        savebtn.bind(on_release = self.save)
        loadbtn.bind(on_release = self.load)
        pausebtn.bind(on_release = self.on_pause)
        self.parent.add_widget(self.painter)
        self.parent.add_widget(startbtn)
        self.parent.add_widget(savebtn)
        self.parent.add_widget(loadbtn)
        self.parent.add_widget(pausebtn)
        return self.parent

    def start(self, obj):
        self.My_Clock.schedule_interval(self.parent.update, 1.0/30.0) #This invokes MainWidget.update routine. We need to write our code there [MainWidget.update]
        print("Clicked Start")

    def save(self, obj):
        print("Clicked Save")


    def load(self, obj):
        print("Clicked load")
        
    def on_pause(self, obj):
        self.My_Clock.unschedule(self.parent.update) # Stops the clock
        print("Paused")



# Running the whole thing
if __name__ == '__main__':
    MainApp().run()