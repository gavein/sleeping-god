#!/usr/bin/python2
# -*- coding: utf-8 -*-


from SleepingGodObjects.GameObjects import GameObject


class Planet(GameObject):
    def __init__(
                 self,
                 pos_x,
                 pos_y,
                 char,
                 label,
                 color,
                 blocks,
                 minerals,
                 water,
                 terralike=False,
                 human_population=0):

        GameObject.__init__(
                            self,
                            pos_x,
                            pos_y,
                            char,
                            label,
                            color,
                            blocks)

        self.minerals = minerals
        self.water = water
        self.terralike = terralike
        self.human_population = human_population

    def info(self):
        return (
                self.minerals,
                self.water,
                self.terralike,
                self.human_population)

