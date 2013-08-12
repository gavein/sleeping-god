#!/usr/bin/python2
# -*- coding: utf-8 -*-


class Player:
    def __init__(
                 self,
                 life_max=50,
                 intelligence=10,
                 charisma=0):

        self.life_max = life_max
        self.life_cur = life_max - 10
        self.intelligence = intelligence
        self.charisma = charisma
