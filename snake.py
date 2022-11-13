import numpy as np
import arcade
from collections import namedtuple
from typing import List
import time
from enum import Enum
from ukulele import Song, Tuning
from device import Microphone, Device
import threading
import random

# --- Set up the constants

# Size of the screen
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Snake"

BACKGROUND_COLOR = (200,200,200)

def Vec(x,y):
    return np.float32([x,y])

class Entity:
    def __init__(self):
        pass

    def update(self, tick):
        pass

    def draw(self):
        pass

GRID = 20

class Snake(Entity):
    def __init__(self,pos,color):
        self.pos = np.copy(pos)
        self.dir = Vec(1,0)
        self.tail = []
        self.eaten = 5
        self.died = False
        self.color = color

    def update(self):
        self.pos += self.dir*GRID
        self.tail = self.tail[0 if self.eaten else 1:] + [np.copy(self.pos)]
        self.eaten = max(0,self.eaten-1)

        if not (0<=self.pos[0]<SCREEN_WIDTH and 0<=self.pos[1]<SCREEN_HEIGHT):
            self.died = True

    def go_dir(self,new_dir):
        if tuple(-new_dir) == tuple(self.dir):
            return
        self.dir = new_dir

    def eat_apple(self):
        self.eaten += 1

    def draw(self):
        for cell in self.tail:
            arcade.draw_rectangle_filled(cell[0],cell[1],GRID-1,GRID-1,self.color)

class Apple:
    def __init__(self,pos):
        self.pos = pos

    def draw(self):
        arcade.draw_rectangle_filled(self.pos[0],self.pos[1],GRID-1,GRID-1,arcade.color.CANDY_APPLE_RED)


class Score:
    def __init__(self):
        self.pos = Vec(10,10)
        self.value = 0

    def give_score(self, x):
        self.value += x

    def draw(self):
        arcade.draw_text(str(self.value),self.pos[0],self.pos[1],(80,80,80),font_size=20)


class UkuleleInput:
    def __init__(self, tuning:Tuning = Tuning()):
        self.mic = Microphone()
        self.device = Device()
        self.last = None
        self.tuning = tuning

        self.c = 0
        self.should_run=True
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def run(self):
        while self.should_run:
            self.mic.tick(self.device)

    def update(self,delta_time):
        self.c+=1
        if self.c%5==0:
            self.mic.tick(self.device)
    
    def get_note(self):
        note = self.device.get_state()
        if note is not None and self.last!=note:
            self.last = note
            return self.tuning.note_to_string(note)
        self.last = note       

def randpos():
    return Vec(random.randint(0,10)*GRID,random.randint(0,10)*GRID) + Vec(GRID//2,GRID//2)

class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.background_color = BACKGROUND_COLOR

        self.snakes = [Snake(randpos(),c) for c in [arcade.color.SKY_BLUE, arcade.color.GREEN]]
        self.apples = [Apple(randpos()) for i in range(2)]

        self.score = Score()

        self.ukulele_input = UkuleleInput()

        self.period = 1
        self.c = self.period

    def on_update(self, delta_time):
        
        self.c -= delta_time
        if self.c>0:
            return
            
        inp = self.ukulele_input.get_note()
        if inp is not None:
            key_row, key_col = inp
            self.snakes[key_row].go_dir([
                Vec(-1,0),
                Vec(0,1),
                Vec(0,-1),
                Vec(1,0)
            ][key_col])
            
        self.c = self.period

        allcells = set()
        for snake in self.snakes:
            snake.update()
            allcells |= set(tuple(p) for p in snake.tail[:-1])
            
        for snake in self.snakes:
            if tuple(snake.pos) in allcells:
                snake.died=True

            for apple in self.apples:
                if tuple(apple.pos)==tuple(snake.pos):
                    snake.eat_apple()
                    while True:
                        apple.pos = randpos()
                        if tuple(apple.pos) not in allcells:
                            break
        
            if snake.died:
                time.sleep(1)
                #self.ukulele_input.should_run = False
                exit()

    def on_draw(self):
        self.clear()
        
        for entity in self.snakes + self.apples:
            entity.draw()
    
    def on_key_press(self, key, modifiers):
        k = arcade.key
        key_grid = [
            [k.KEY_1,k.KEY_2,k.KEY_3,k.KEY_4],
            [k.Q,k.W,k.E,k.R],
            [k.A,k.S,k.D,k.F],
            [k.Z,k.X,k.C,k.V]
        ]

        matching_key = [(i,j) for i in range(4) for j in range(4) if key_grid[i][j]==key] 
        if matching_key == []:
            return
        [(key_row,key_col)] = matching_key

        self.snakes[key_row].go_dir([
            Vec(-1,0),
            Vec(0,1),
            Vec(0,-1),
            Vec(1,0)
        ][key_col])
        


def main():
    """ Main function """
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()