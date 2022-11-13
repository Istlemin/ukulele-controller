import numpy as np
import arcade
from collections import namedtuple
from typing import List
import time

# --- Set up the constants

# Size of the screen
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Pong4"

BACKGROUND_COLOR = arcade.color.ALMOND

def Vec(x,y):
    return np.float32([x,y])

class Entity:
    def __init__(self):
        pass

    def update(self):
        pass

    def draw(self):
        pass

class Ball(Entity):

    def __init__(self,pos,vel,r=20,color=arcade.color.DARK_BROWN):
        self.pos = pos
        self.vel = vel
        self.r = 20
        self.size = Vec(r,r)
        self.color = arcade.color.DARK_BROWN

    def update(self):
        self.pos += self.vel
        
        dead = False
        if self.pos[0] > SCREEN_WIDTH - self.r:
            dead = True
        if self.pos[1] > SCREEN_HEIGHT - self.r:
            dead = True
        if self.pos[0] < self.r:
            dead = True
        if self.pos[1] < self.r:
            dead = True
        
        if dead:            
            print("Dead!")
            time.sleep(2)
            exit()

    def draw(self):
        arcade.draw_circle_filled(self.pos[0],
                                     self.pos[1],
                                     self.r,
                                     self.color)

Collision = namedtuple("Collision", "pos normal")

def aabb_overlap(pos1,size1,pos2,size2):
    topleft = np.minimum(pos1+size1,pos2+size2)
    bottomright  = np.maximum(pos1-size1,pos2-size2)
    if topleft[0]>bottomright[0] and topleft[1]>bottomright[1]:
        return (topleft+bottomright)/2
    else:
        return None

class Paddle(Entity):
    def __init__(self, frompos, topos, size):
        self.frompos = frompos
        self.topos = topos
        self.pos = (frompos+topos)/2
        self.size = size
        self.color = arcade.color.PANSY_PURPLE

    def setpos(self, p):
        self.pos = p*self.topos+(1-p)*self.frompos

    def update(self):
        pass

    def intersects_ball(self,ball):
        intersection = aabb_overlap(self.pos,self.size,ball.pos,ball.size)
        if intersection is None:
            return None
        
        normal = intersection-ball.pos
        normal /= np.linalg.norm(normal)
    
        return Collision(intersection,normal)

    def draw(self):
        arcade.draw_rectangle_filled(self.pos[0],self.pos[1],self.size[0]*2,self.size[1]*2,self.color)

PADDLE_WALL_DIST = 20
PADDLE_THICKNESS = 20
PADDLE_WIDTH = 100

def make_paddles(win_width,win_height, wall_dist = 20, width = 100, thickness = 20) -> List[Paddle]:
    return [
        Paddle(Vec(width,win_height-wall_dist), Vec(win_width - width,win_height-wall_dist), Vec(width, thickness)/2),
        Paddle(Vec(wall_dist, width), Vec(wall_dist,win_height - width), Vec(thickness, width)/2),
        Paddle(Vec(win_width - wall_dist, width), Vec(win_width - wall_dist,win_height - width), Vec(thickness, width)/2),
        Paddle(Vec(width,wall_dist), Vec(win_width - width,wall_dist), Vec(width, thickness)/2),
    ]

class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.ball = Ball(Vec(200,300),Vec(2,3))

        self.paddles : List[Paddle] = make_paddles(width, height)
        self.background_color = BACKGROUND_COLOR

        self.entities : List[Entity] = [self.ball] + self.paddles

    def on_update(self, delta_time):
        self.ball.update()

        for paddle in self.paddles:
            inter = paddle.intersects_ball(self.ball)
            if inter is not None:
                self.ball.vel -= 2*np.dot(inter.normal,self.ball.vel)*inter.normal

    def on_draw(self):
        self.clear()
        for entity in self.entities:
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

        self.paddles[key_row].setpos((key_col)/3)
        


def main():
    """ Main function """
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()