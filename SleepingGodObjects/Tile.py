#!/usr/bin/python2
# -*- coding: utf-8 -*-



class Tile:

    '''
    A tile of the map and its properties.
    '''

    def __init__(
                 self,
                 blocked,
                 block_sight=None):

        self.blocked = blocked
        self.explored = False
        if block_sight is None:
            block_sight = blocked
        self.block_sight = block_sight

