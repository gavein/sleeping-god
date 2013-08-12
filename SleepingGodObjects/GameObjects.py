#!/usr/bin/python2
# -*- coding: utf-8 -*-


import libtcodpy as libtcod


class GameObject:

    '''
    General game object.
    Represents object by a character on screen.
    '''

    def __init__(
                 self,
                 pos_x,
                 pos_y,
                 char,
                 label,
                 color,
                 blocks=False):

        self.pos_x = pos_x
        self.pos_y = pos_y
        self.char = char
        self.label = label
        self.color = color
        self.blocks = blocks

    def draw(self, con, fov_map):
        if libtcod.map_is_in_fov(fov_map, self.pos_x, self.pos_y):
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_print(con, self.pos_x, self.pos_y, self.char)

    def clear(self, con):
        libtcod.console_print(con, self.pos_x, self.pos_y, " ")

    def info(self):
        return (
                self.pos_x,
                self.pos_y,
                self.char,
                self.label,
                self.color,
                self.blocks)

