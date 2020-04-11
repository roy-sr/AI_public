import numpy as np
from random import random, randint
import matplotlib.pyplot as plt
import time
import sys

# Importing the Kivy packages
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


ddqn = False

if ddqn:
    from Network_run import MainNetwork
else:
    from network import MainNetwork


last_x = 0
last_y = 0
n_points = 0
length = 0


mind = MainNetwork(5,3,0.9)
action2rotation = [0,20,-20]
last_reward = 0
scores = []


maze_file = ["maze_train0","maze_train1","maze_level0","maze_level1","maze_level2","maze_level3"]
start_pointX = [780,0,780,740,680,585]
start_pointY = [0,580,0,200,30,20]
end_pointX =   [0,780,20,0,500,585]
end_pointY =   [580,0,580,400,599,570]

maze_number = 3

maze_array = pd.read_csv(maze_file[maze_number] + ".csv",header=None)
maze_magnified = np.kron(maze_array, np.ones((10,10)))





first_update = True
def init():
    global white_space
    global goal_x
    global goal_y
    global first_update
    white_space = maze_magnified.copy()
    goal_x = end_pointX[maze_number]
    goal_y = end_pointY[maze_number]
    print("Goal : ",end_pointX[maze_number], " - " , end_pointY[maze_number])
    first_update = False


last_distance = 0



class Agent(Widget):
    
    angle = NumericProperty(0)
    rotation = NumericProperty(0)
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    sensor1_x = NumericProperty(0)
    sensor1_y = NumericProperty(0)
    sensor1 = ReferenceListProperty(sensor1_x, sensor1_y)
    sensor2_x = NumericProperty(0)
    sensor2_y = NumericProperty(0)
    sensor2 = ReferenceListProperty(sensor2_x, sensor2_y)
    sensor3_x = NumericProperty(0)
    sensor3_y = NumericProperty(0)
    sensor3 = ReferenceListProperty(sensor3_x, sensor3_y)
    signal1 = NumericProperty(0)
    signal2 = NumericProperty(0)
    signal3 = NumericProperty(0)
    
    
          

    def move(self, rotation):
        self.pos = Vector(*self.velocity) + self.pos
        self.rotation = rotation
        self.angle = self.angle + self.rotation
        self.sensor1 = Vector(30, 0).rotate(self.angle) + self.pos
        self.sensor2 = Vector(30, 0).rotate((self.angle+30)%360) + self.pos
        self.sensor3 = Vector(30, 0).rotate((self.angle-30)%360) + self.pos
        
        self.signal1 = 1 if (int(np.sum(white_space[int(self.sensor1_x)-10:int(self.sensor1_x)+10, int(self.sensor1_y)-10:int(self.sensor1_y)+10]))/400 > 0.5) else int(np.sum(white_space[int(self.sensor1_x)-10:int(self.sensor1_x)+10, int(self.sensor1_y)-10:int(self.sensor1_y)+10]))/400.
        self.signal2 = 1 if (int(np.sum(white_space[int(self.sensor2_x)-10:int(self.sensor2_x)+10, int(self.sensor2_y)-10:int(self.sensor2_y)+10]))/400 > 0.5) else int(np.sum(white_space[int(self.sensor2_x)-10:int(self.sensor2_x)+10, int(self.sensor2_y)-10:int(self.sensor2_y)+10]))/400.
        self.signal3 = 1 if (int(np.sum(white_space[int(self.sensor3_x)-10:int(self.sensor3_x)+10, int(self.sensor3_y)-10:int(self.sensor3_y)+10]))/400 > 0.5) else int(np.sum(white_space[int(self.sensor3_x)-10:int(self.sensor3_x)+10, int(self.sensor3_y)-10:int(self.sensor3_y)+10]))/400.
        
        
        if self.sensor1_x>maze_width-10 or self.sensor1_x<10 or self.sensor1_y>maze_height-10 or self.sensor1_y<10:
            self.signal1 = 1.
        if self.sensor2_x>maze_width-10 or self.sensor2_x<10 or self.sensor2_y>maze_height-10 or self.sensor2_y<10:
            self.signal2 = 1.
        if self.sensor3_x>maze_width-10 or self.sensor3_x<10 or self.sensor3_y>maze_height-10 or self.sensor3_y<10:
            self.signal3 = 1.

class Sensor1(Widget):
    pass
class Sensor2(Widget):
    pass
class Sensor3(Widget):
    pass

# Creating the game class

class MainWidget(Widget):

    agent = ObjectProperty(None)
    sensor1 = ObjectProperty(None)
    sensor2 = ObjectProperty(None)
    sensor3 = ObjectProperty(None)
    
    def serve_agent(self):
        self.agent.pos = self.position
        self.agent.velocity = Vector(6, 0)
        

    def update(self, dt):

        global mind
        global last_reward
        global scores
        global last_distance
        global goal_x
        global goal_y
        global maze_width
        global maze_height

        
        maze_width = self.width
        maze_height = self.height
        if first_update:
            self.step_counter = 0
            self.run_counter = 0
            init()

        xx = goal_x - self.agent.x
        yy = goal_y - self.agent.y
        orientation = Vector(*self.agent.velocity).angle((xx,yy))/180.
        last_signal = [self.agent.signal1, self.agent.signal2, self.agent.signal3, orientation, -orientation]
        action = mind.update(last_reward, last_signal)
        scores.append(mind.score())
        rotation = action2rotation[action]
        self.agent.move(rotation)
        distance = np.sqrt((self.agent.x - goal_x)**2 + (self.agent.y - goal_y)**2)
        self.sensor1.pos = self.agent.sensor1
        self.sensor2.pos = self.agent.sensor2
        self.sensor3.pos = self.agent.sensor3

        if white_space[int(self.agent.x),int(self.agent.y)] > 0:
            self.agent.velocity = Vector(1, 0).rotate(self.agent.angle)
            last_reward = -1
        else:
            self.agent.velocity = Vector(6, 0).rotate(self.agent.angle)
            last_reward = -0.1
            if distance < last_distance:
                last_reward = 0.2

        if self.agent.x < 10:
            self.agent.x = 10
            last_reward = -1
        if self.agent.x > self.width - 10:
            self.agent.x = self.width - 10
            last_reward = -1
        if self.agent.y < 10:
            self.agent.y = 10
            last_reward = -1
        if self.agent.y > self.height - 10:
            self.agent.y = self.height - 10
            last_reward = -1

        if distance < 50:
            if (maze_file[maze_number].find("maze_train") != -1):           
                goal_x = self.width-goal_x
                goal_y = self.height-goal_y
                print("Direction Changed")
            else:
                dateTimeObj = datetime.now()
                # log file 
                log_file = open(maze_file[maze_number] + "_logfile.txt", "a")
                log_file.writelines("End : " + str(dateTimeObj) + "\n")
                log_file.writelines("Steps : " + str(self.step_counter) + " _DDQN_" +str(ddqn) + " Run counter : " + str(self.run_counter) +"\n")
                log_file.close()   
                
                if self.run_counter <  10:
                    if self.run_counter % 2 == 0:
                        goal_x = start_pointX[maze_number]
                        goal_y = start_pointY[maze_number]
                    else:
                        goal_x = end_pointX[maze_number]
                        goal_y = end_pointY[maze_number]
                    print("Direction Changed Evaluation : " , goal_x , " " , goal_y)  
                    self.run_counter += 1
                else:
                    sys.exit()


                
        last_distance = distance
        self.step_counter += 1
        

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
                        
    def on_touch_down(self, touch):
        global length,n_points,last_x,last_y
        with self.canvas:
            Color = (1, 0, 0)
            d=10.
            touch.ud['line'] = Line(points = (touch.x, touch.y), width = 10)
            last_x = int(touch.x)
            last_y = int(touch.y)
            n_points = 0
            length = 0
            white_space[int(touch.x),int(touch.y)] = 1
            print("X : ",int(touch.x),"Y : ",int(touch.y))

    def on_touch_move(self, touch): 
        global length,n_points,last_x,last_y
        if touch.button=='left':
            touch.ud['line'].points += [touch.x, touch.y]
            x = int(touch.x)
            y = int(touch.y)
            length += np.sqrt(max((x - last_x)**2 + (y - last_y)**2, 2))
            n_points += 1.
            density = n_points/(length)
            touch.ud['line'].width = int(20*density + 1)
            white_space[int(touch.x) - 10 : int(touch.x) + 10, int(touch.y) - 10 : int(touch.y) + 10] = 1
            last_x = x
            last_y = y


          


class MainApp(App):

    initpos_x = NumericProperty(start_pointX[maze_number])
    initpos_y = NumericProperty(start_pointY[maze_number])
    position = ReferenceListProperty(initpos_x, initpos_y)  
    print("Start : ",initpos_x, " - " , initpos_y)
    
    def build(self):

        self.parent = MainWidget()
        #self.parent.serve_agent()
        self.parent.agent.pos = self.position
        self.parent.agent.velocity = Vector(6, 0)
        self.My_Clock = Clock
        if (maze_file[maze_number].find("maze_train") != -1):    
            pass
        else:
            dateTimeObj = datetime.now()
            # log file 
            log_file = open(maze_file[maze_number] + "_logfile.txt", "a")
            log_file.writelines("\nStart : " + str(dateTimeObj) + "\n")
            log_file.close()
            self.My_Clock.schedule_interval(self.parent.update, 1.0/45.0)
            mind.load()
            if ddqn:
                mind.target_load()
                print("Target Loaded")
            
        self.painter = MyPaintWidget()
        startbtn = Button(text = 'Start')
        pausebtn = Button(text = 'Pause', pos = (self.parent.width, 0))
        savebtn = Button(text = 'Save Memory', pos = (2 *self.parent.width, 0))
        loadbtn = Button(text = 'Load Memory', pos = (3 * self.parent.width, 0))
        clearbtn = Button(text = 'Clear frame', pos = (4 * self.parent.width, 0))

        startbtn.bind(on_release = self.start)
        savebtn.bind(on_release = self.save)
        loadbtn.bind(on_release = self.load)
        pausebtn.bind(on_release = self.on_pause)
        clearbtn.bind(on_release = self.clear_canvas)
        self.parent.add_widget(self.painter)
        self.parent.add_widget(startbtn)
        self.parent.add_widget(savebtn)
        self.parent.add_widget(loadbtn)
        self.parent.add_widget(pausebtn)
        self.parent.add_widget(clearbtn)
        return self.parent

    def start(self, obj):
        self.My_Clock.schedule_interval(self.parent.update, 1.0/60.0)

    def save(self, obj):
        print("saving mind...")
        dateTimeObj = datetime.now()
        file_name = str(maze_file[maze_number]) + '_' + str(dateTimeObj.year) + '_' + str(dateTimeObj.month) + '_' + str(dateTimeObj.day) + str(dateTimeObj.hour) + '_' + str(dateTimeObj.minute) + '_' + str(dateTimeObj.second) + '_' + str(dateTimeObj.microsecond)
        file_name = file_name + "_DDQN_" +str(ddqn)
        mind.save(scores, file_name)
        plt.plot(scores)
        plt.savefig(file_name + ".png")
        plt.show()

    def load(self, obj):
        print("loading last saved mind...")
        mind.load()
        
    def on_pause(self, obj):
        self.My_Clock.unschedule(self.parent.update)
        print("Paused")
        
    def clear_canvas(self, obj):
        global white_space
        self.painter.canvas.clear()
        white_space = maze_magnified.copy()



# Main run
if __name__ == '__main__':
    MainApp().run()


