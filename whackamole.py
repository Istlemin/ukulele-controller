import numpy as np
import arcade
from collections import namedtuple
from typing import List
import time
from enum import Enum
from ukulele import Song, Tuning
from device import Microphone, Device
import threading

# --- Set up the constants

# Size of the screen
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Whack-a-mole"

BACKGROUND_COLOR = (125,244,56)

def Vec(x,y):
    return np.float32([x,y])

class Entity:
    def __init__(self):
        pass

    def update(self, tick):
        pass

    def draw(self):
        pass

class Mole(Entity):
    def __init__(self,pos,sprite_scale,lifetime=10):
        self.pos = np.copy(pos)

        self.pos[0] += np.random.uniform(low=-10,high=10)

        self.lifetime = lifetime
        self.time_until_dead = -100

        self.mole_sprite = arcade.Sprite("resources/mole.png", sprite_scale)
        self.mole_offset = -50
        
        self.disappear_after = 1e18

        self.whacked = False

    def whack(self):
        if self.disappear_after < 1000:
            return
        self.disappear_after = 0.3
        self.whacked = True

    def update(self,delta_time):
        if self.time_until_dead == -100:
            self.time_until_dead = self.lifetime
            return True
        self.time_until_dead -= delta_time
        self.disappear_after -= delta_time

        if self.disappear_after<0:
            return False
            
        self.disappear_after -= delta_time
        self.mole_offset += delta_time*200
        self.mole_offset = min(self.mole_offset,0)
        if self.disappear_after>1000:
            self.time_until_dead -= delta_time
        if self.time_until_dead<0:      
            print("Dead!")
            time.sleep(1)
            exit()

        return True

    def draw(self):
        self.mole_sprite.center_x = self.pos[0]
        self.mole_sprite.center_y = self.pos[1]+self.mole_offset
        c = int(255*self.time_until_dead/self.lifetime)
        self.mole_sprite.color = (255,c,c)
        self.mole_sprite.draw()
        arcade.draw_rectangle_filled(self.pos[0],self.pos[1]-65,70,60,BACKGROUND_COLOR)

class MoleHole(Entity):
        
    def __init__(self,pos, rate=0.1):
        self.r=20
        self.pos = np.copy(pos)
        self.color = arcade.color.DARK_BROWN

        self.sprite_scale = self.r*0.008
        self.hole_sprite = arcade.Sprite("resources/mole_hole.png", self.sprite_scale)
        self.grass_sprite = arcade.Sprite("resources/mole_grass.png", self.sprite_scale)

        self.hole_sprite.center_x = self.pos[0]
        self.hole_sprite.center_y = self.pos[1]
        self.grass_sprite.center_x = self.pos[0]
        self.grass_sprite.center_y = self.pos[1]

        self.moles = []

    def new_mole(self):
        self.moles.append(Mole(self.pos,self.sprite_scale))

    def update(self, delta_time):
        self.moles = [mole for mole in self.moles if mole.update(delta_time)]
                
    def whack(self):
        for mole in self.moles:
            if not mole.whacked:
                mole.whack()
                return True
        return False

    def draw(self):
        self.hole_sprite.draw()
        
        for mole in self.moles:
            mole.draw()

        self.grass_sprite.draw()

class Hammer:
    def __init__(self,pos,hit):
        self.pos = pos
        self.lifetime = 0.5
        if hit:
            self.sprite = arcade.Sprite("resources/hammer_hit.png", 0.3)
            self.sprite.center_x = pos[0]+20
            self.sprite.center_y = pos[1]+45
        else:
            self.sprite = arcade.Sprite("resources/hammer.png", 0.3)
            self.sprite.center_x = pos[0]+10
            self.sprite.center_y = pos[1]+10
    
    def update(self,delta_time):
        self.lifetime-=delta_time
    
    def draw(self):
        self.sprite.draw()

class Score:
    def __init__(self):
        self.pos = Vec(10,10)
        self.value = 0

    def give_score(self, x):
        self.value += x

    def draw(self):
        arcade.draw_text(str(self.value),self.pos[0],self.pos[1],(80,80,80),font_size=20)

Collision = namedtuple("Collision", "pos normal")

class MoleSong:
    def __init__(self,moles : List[MoleHole], path,tuning=Tuning()):
        self.song = Song(path)
        self.tuning = tuning
        self.moles = moles
        
        self.note_interval = 1
        self.note_interval_counter = self.note_interval
        self.note_index = 0
    
    def update(self,delta_time):
        self.note_interval_counter -= delta_time
        if self.note_interval_counter<0:
            self.note_interval_counter = self.note_interval
            if self.note_index>=len(self.song.notes):
                return
            note = self.song.notes[self.note_index]
            if note is not None:
                string,fret = self.tuning.note_to_string(note)
                self.moles[string*4+fret].new_mole()
            self.note_index += 1

class UkuleleInput:
    def __init__(self, tuning:Tuning = Tuning()):
        self.mic = Microphone()
        self.device = Device()
        self.last = None
        self.tuning = tuning

        self.c = 0
        thread = threading.Thread(target=self.run)
        thread.start()

    def run(self):
        while True:
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


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.background_color = BACKGROUND_COLOR
        margin = 100
        self.moles : List[MoleHole] = [
            MoleHole(Vec(x,y) + np.random.uniform(low=-30,high=30),rate=0.000001)
            for y in np.linspace(margin,height-margin,4)
            for x in np.linspace(margin,width-margin,4)
        ]

        self.hammers : List[Hammer] = []

        self.score = Score()

        self.song = MoleSong(self.moles, "songs/twinkletwinkle.song")

        #self.ukulele_input = UkuleleInput()

    def on_update(self, delta_time):
        #self.ukulele_input.update(delta_time)
        inp = self.ukulele_input.get_note()
        if inp is not None:
            print("INPUT! ", inp)
            self.whack(*inp)

        self.song.update(delta_time)
        for mole in self.moles:
            mole.update(delta_time)
        
        for hammer in self.hammers:
            hammer.update(delta_time)
        
        self.hammers = [hammer for hammer in self.hammers if hammer.lifetime>0]

    def on_draw(self):
        entities = self.moles[::-1] + self.hammers

        self.clear()
        for entity in entities:
            entity.draw()
        
        self.score.draw()
    
    def whack(self,row,col):
        if row*4+col>=len(self.moles):
            return
        mole = self.moles[row*4+col]
        did_hit = mole.whack()
        self.hammers.append(Hammer(mole.pos,did_hit))

        if did_hit:
            self.score.give_score(50)
        else:
            self.score.give_score(-100)


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

        self.whack(3-key_row,key_col)
        


def main():
    """ Main function """
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()