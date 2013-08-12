#!/usr/bin/python2
# -*- coding: utf-8 -*-


from libtcodpy import FOV_BASIC, Color


# Game constants.
# Actual size of the window.
SCREEN_WIDTH = 85
SCREEN_HEIGHT = 58

# Size of the map.
MAP_WIDTH = 63
MAP_HEIGHT = 45

# Message console.
MSG_CONSOLE_WIDTH = MAP_WIDTH - 2
MSG_CONSOLE_HEIGHT = SCREEN_HEIGHT - MAP_HEIGHT
MSG_X = 2

# Planet menu.
PLANET_MENU_WIDTH = 50

# How many planets in system. At least one.
MIN_PLANETES = 1
MAX_PLANETES = 10
MAX_OBJECT_IN_SPACE = 20

# Planet resources.
MIN_MINERALS = 10
MAX_MINERALS = 200
MAX_POPULATION = 1000
MIN_WATER = 100
MAX_WATER = 10000

# FOV parameters.
FOV_ALGO = FOV_BASIC
FOV_LIGHT = True
FOV_RADIUS = 40

# Cargo variables.
CARGO_WATER = "cargo_water"
CARGO_MINERALS = "cargo_minerals"

WEAR_AT_TURN = 3
OXYGEN_AT_TURN = 1

# Game states.
EXIT = "exit"
PLAYING = "playing"


# 20 frame-per-second maximum.
LIMIT_FPS = 20

# Colors.
SPACE_DARK_COLOR = Color(0, 0, 66)
SPACE_LIGHT_COLOR = Color(0, 0, 204)
PLANET_DARK_COLOR = Color(0, 99, 99)
PLANET_LIGHT_COLOR = Color(0, 99, 204)
