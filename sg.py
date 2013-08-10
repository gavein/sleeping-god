#!/usr/bin/python2
# -*- coding: utf-8 -*-


import random
import libtcodpy as libtcod


# Actual size of the window.
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

# Size of the map.
MAP_WIDTH = 80
MAP_HEIGHT = 45

# How many planetes in system. At least one.
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
FOV_ALGO = libtcod.FOV_BASIC
FOV_LIGHT = True
FOV_RADIUS = 40

# Cargo variables.
CARGO_WATER = "cargo_water"
CARGO_MINERALS = "cargo_minerals"

# Game states.
EXIT = "exit"
PLAYING = "playing"


systemstar_x = MAP_WIDTH / 2
systemstar_y = MAP_HEIGHT / 2
# 20 frame-per-second maximum.
LIMIT_FPS = 20

# Colors.
SPACE_DARK_COLOR = libtcod.Color(0, 0, 66)
SPACE_LIGHT_COLOR = libtcod.Color(0, 0, 204)
PLANET_DARK_COLOR = libtcod.Color(0, 99, 99)
PLANET_LIGHT_COLOR = libtcod.Color(0, 99, 204)


class GameObject:
    # This is a generic game object: the spacevessel, an item, the planets...
    # It's always represented by a character on screen.
    def __init__(self, pos_x, pos_y, char, label, color, blocks=False):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.char = char
        self.label = label
        self.color = color
        self.blocks = blocks

    def draw(self):
        if libtcod.map_is_in_fov(fov_map, self.pos_x, self.pos_y):
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.pos_x, self.pos_y, self.char, libtcod.BKGND_NONE)

    def clear(self):
        libtcod.console_put_char(con, self.pos_x, self.pos_y, " ", libtcod.BKGND_NONE)

    def info(self):
        return (self.pos_x,
                self.pos_y,
                self.char,
                self.label,
                self.color,
                self.blocks)


class Vessel(GameObject):
    def __init__(
            self, pos_x, pos_y, char, label, color, blocks,
            cargo={}):
        GameObject.__init__(
                self, pos_x, pos_y, char,
                label, color, blocks)
        self.cargo = cargo
        self.cargo_keys = [CARGO_MINERALS, CARGO_WATER]
        for key in self.cargo_keys:
            if not self.cargo.has_key(key):
                self.cargo[key] = 0
    
    def move(self, dx, dy):
        if not is_blocked(self.pos_x+dx, self.pos_y+dy):
            self.pos_x += dx
            self.pos_y += dy

    def transfer_resources_from(self, target):
        minerals = target.minerals
        water = target.water
        self.cargo[CARGO_MINERALS] += minerals
        self.cargo[CARGO_WATER] += water
        target.minerals = 0
        target.water = 0

    def cargo_info(self, key):
        if self.cargo.has_key(key):
            return self.cargo[key]


class Planet(GameObject):
    def __init__(
            self, pos_x, pos_y, char, label, color, blocks,
            minerals, water, terralike=False, human_population=0):

        GameObject.__init__(
                self, pos_x, pos_y, char,
                label, color, blocks)
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


class Tile:
    # A tile of the map and its properties.
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        self.explored = False
        if block_sight is None:
            block_sight = blocked
        self.block_sight = block_sight


def spacevessel_move_or_attack(dx, dy):
    global fov_recompute

    x = spacevessel.pos_x + dx
    y = spacevessel.pos_y + dy

    target = None
    for obj in gameobjects:
        if obj.pos_x == x and obj.pos_y == y:
            target = obj
            break

    if target is not None:
        print "====>>> There is %s." % target.label
        if isinstance(target, Planet):
            print "On planet:\nMinerals: %s\nWater: %s\nTerraformed: %s\nHuman population: %s" % target.info()
            spacevessel.transfer_resources_from(target)
            print "Now on planet:\nMinerals: %s\nWater: %s\nTerraformed: %s\nHuman population: % s" % target.info()
    else:
        spacevessel.move(dx, dy)
        fov_recompute = True


def handle_keys():
    key = libtcod.console_wait_for_keypress(True)

    if key.vk == libtcod.KEY_ESCAPE:
        return "exit"

    if game_state == PLAYING:
        if libtcod.console_is_key_pressed(libtcod.KEY_UP):
            spacevessel_move_or_attack(0, -1)
        elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
            spacevessel_move_or_attack(0, 1)
        elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
            spacevessel_move_or_attack(-1, 0)
        elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
            spacevessel_move_or_attack(1, 0)
        else:
            return "didnt-take-turn"

def is_blocked(x, y):
    if map[x][y].blocked:
        return True
    for obj in gameobjects:
        if obj.blocks and obj.pos_x == x and obj.pos_y == y:
            return True
    return False

def place_objects():
    num_objects = random.randint(0, MAX_OBJECT_IN_SPACE)

    for obj in xrange(num_objects):
        x = random.randint(0, MAP_WIDTH-1)
        y = random.randint(0, MAP_HEIGHT-1)
        if not is_blocked(x, y):
            dice = random.randint(0, 100)
            if dice < 80:
                spaceobject = GameObject(x, y, "v", "vessel", libtcod.desaturated_green, True)
            else:
                spaceobject = GameObject(x, y, "s", "station", libtcod.darker_green, True)
            map[x][y].block_sight = True
            gameobjects.append(spaceobject)

def set_planet_properties():
    minerals = random.randint(MIN_MINERALS, MAX_MINERALS)
    water = random.randint(MIN_WATER, MAX_WATER)

    terralike = random.choice([True, False])
    if terralike:
        human_population = random.randint(0, MAX_POPULATION)
    else:
        human_population = 0

    return (minerals,
            water,
            terralike,
            human_population)

def make_map():
    global map

    map = [[ Tile(False)
        for y in xrange(MAP_HEIGHT) ]
        for x in xrange(MAP_WIDTH) ]

    map[systemstar_x][systemstar_y].blocked = True
    map[systemstar_x][systemstar_y].block_sight = False
    libtcod.console_set_char_background(con, systemstar_x, systemstar_y, libtcod.yellow, libtcod.BKGND_SET)

    #planets = []
    num_planetes = random.randint(MIN_PLANETES, MAX_PLANETES)
    apsis = 2

    for p in xrange(num_planetes):
        direction = random.randint(0, 1)
        if direction == 1:
            x = systemstar_x + apsis
        else:
            x = systemstar_x - apsis
        y = random.randint(0, MAP_HEIGHT-1)

        if x >= MAP_WIDTH or x <= 0:
            break

        m, w, t, p = set_planet_properties()

        planet = Planet(pos_x=x,
                        pos_y=y,
                        char="p",
                        label="planet",
                        color=libtcod.black,
                        blocks=True,
                        minerals=m,
                        water=w,
                        terralike=t,
                        human_population = p)
        #planets.append(planet)
        gameobjects.append(planet)

        map[x][y].blocked = True
        map[x][y].block_sight = True

        apsis += apsis

    place_objects()


def render_all():
    global fov_recompute

    if fov_recompute:
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, spacevessel.pos_x, spacevessel.pos_y, FOV_RADIUS, FOV_LIGHT, FOV_ALGO)

        for y in xrange(MAP_HEIGHT):
            for x in xrange(MAP_WIDTH):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                if not visible:
                    if map[x][y].explored:
                        if x == systemstar_x and y == systemstar_y:
                            col = libtcod.yellow
                        else:
                            col = SPACE_DARK_COLOR
                        libtcod.console_set_char_background(con, x, y, col, libtcod.BKGND_SET)
                else:
                    if x == systemstar_x and y == systemstar_y:
                        col = libtcod.yellow
                    else:
                        col = SPACE_LIGHT_COLOR
                    libtcod.console_set_char_background(con, x, y, col, libtcod.BKGND_SET)
                    map[x][y].explored = True

    for gameobject in gameobjects:
        gameobject.draw()

    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    libtcod.console_set_default_foreground(con, libtcod.gray)
    libtcod.console_print_ex(0, 1, SCREEN_HEIGHT-3, libtcod.BKGND_NONE, libtcod.LEFT,
            "Water: %s" % spacevessel.cargo_info(CARGO_WATER))
    libtcod.console_print_ex(0, 1, SCREEN_HEIGHT-2, libtcod.BKGND_NONE, libtcod.LEFT,
            "Minerals: %s" % spacevessel.cargo_info(CARGO_MINERALS))


################################
# Initialization & Main Loop
################################

libtcod.console_set_custom_font("dejavu10x10_gs_tc.png", libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, "Sleeping God Alpha", False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

spacevessel = Vessel(
        pos_x=0, pos_y=0, char="@", label="player",
        color=libtcod.white, blocks=True, cargo={})
gameobjects = [spacevessel]

make_map()

fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
for y in xrange(MAP_HEIGHT):
    for x in xrange(MAP_WIDTH):
        libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)

fov_recompute = True
game_state = PLAYING
player_action = None

while not libtcod.console_is_window_closed():

    render_all()

    libtcod.console_flush()

    for gameobject in gameobjects:
        gameobject.clear()


    player_action = handle_keys()
    if player_action == EXIT:
        break
