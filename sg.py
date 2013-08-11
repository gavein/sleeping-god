#!/usr/bin/python2
# -*- coding: utf-8 -*-


import random
import textwrap
import libtcodpy as libtcod


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
FOV_ALGO = libtcod.FOV_BASIC
FOV_LIGHT = True
FOV_RADIUS = 40

# Cargo variables.
CARGO_WATER = "cargo_water"
CARGO_MINERALS = "cargo_minerals"

WEAR_AT_TURN = 3

# Game states.
EXIT = "exit"
PLAYING = "playing"


# 20 frame-per-second maximum.
LIMIT_FPS = 20

# Colors.
SPACE_DARK_COLOR = libtcod.Color(0, 0, 66)
SPACE_LIGHT_COLOR = libtcod.Color(0, 0, 204)
PLANET_DARK_COLOR = libtcod.Color(0, 99, 99)
PLANET_LIGHT_COLOR = libtcod.Color(0, 99, 204)

# System star coordinates. Always at center.
systemstar_x = MAP_WIDTH / 2
systemstar_y = MAP_HEIGHT / 2


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

    def draw(self):
        if libtcod.map_is_in_fov(fov_map, self.pos_x, self.pos_y):
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_print(con, self.pos_x, self.pos_y, self.char)

    def clear(self):
        libtcod.console_print(con, self.pos_x, self.pos_y, " ")

    def info(self):
        return (
                self.pos_x,
                self.pos_y,
                self.char,
                self.label,
                self.color,
                self.blocks)


class Vessel(GameObject):
    SOLAR_SAIL = u"фотонный парус"
    def __init__(
                 self,
                 pos_x,
                 pos_y,
                 char,
                 label,
                 color,
                 blocks,
                 cargo={},
                 hull=0,
                 wear_resistance=0,
                 propulsion=SOLAR_SAIL):

        GameObject.__init__(
                            self,
                            pos_x,
                            pos_y,
                            char,
                            label,
                            color,
                            blocks)
        self.cargo = cargo
        self.cargo_keys = [CARGO_MINERALS, CARGO_WATER]
        for key in self.cargo_keys:
            if not self.cargo.has_key(key):
                self.cargo[key] = 0
        self.hull = hull
        self.wear = hull
        self.wear_resistance = wear_resistance
        self.propulsion = propulsion
        self.abilities = []
    
    def move(self, dx, dy):
        if not is_blocked(self.pos_x+dx, self.pos_y+dy):
            self.pos_x += dx
            self.pos_y += dy
            turn_wear = WEAR_AT_TURN - self.wear_resistance
            self.wear -= turn_wear

    def increase_resources(self, minerals, water):
        self.cargo[CARGO_MINERALS] += minerals
        self.cargo[CARGO_WATER] += water

    def cargo_info(self, key):
        if self.cargo.has_key(key):
            return self.cargo[key]

    def add_ability(self, ability):
        self.abilities.append(ability)

    def use_ability(self, ability, *args):
        if ability in self.abilities:
            ability.use(args)

    def get_ability_name(self, ability):
        return ability.name

    def get_ability_description(self, ability):
        return ability.description


class Ability:
    def __init__(
                 self,
                 name,
                 description,
                 ability_type,
                 use_function=None, *args):
        self.name = name
        self.description = description
        self.ability_type = ability_type
        self.use_function = use_function

    def use(self, *args):
        if self.use_function is None:
            message(u"%s не может быть использовано." % self.name)
        else:
            self.use_function(*args)


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


def transfer_resources(source, target):
    # Transfer resources.
    # Source is planet.
    # Target is spacevessel.
    minerals = source.minerals
    water = source.water
    message(u"Ты получил %s единиц минералов и %s единиц воды. Пригодность планеты для жизни: %s. Человеческое население: %s душ." % source.info())
    target.increase_resources(minerals, water)
    source.minerals = 0
    source.water = 0

resource_transfer_ability = Ability(name=u"Извлечение ресурсов",
                                    description=u"",
                                    ability_type=0,
                                    use_function=transfer_resources)



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
        if isinstance(target, Planet):
            planet_menu(u"Ты вышел на орбиту %s. Что сделать?" % target.label, target)
    else:
        spacevessel.move(dx, dy)
        fov_recompute = True


def handle_keys():
    global key
    #key = libtcod.console_wait_for_keypress(True)

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
                spaceobject = GameObject(x, y, u"v", u"судно", libtcod.desaturated_green, True)
            else:
                spaceobject = GameObject(x, y, u"s", u"станция", libtcod.darker_green, True)
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
    map[systemstar_x][systemstar_y].block_sight = True
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
                        char=u"p",
                        label=u"планета",
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

def choice_menu(header, options, width):
    if len(options) > 26: raise ValueError(u"Cannot have a menu with more than 26 options.")

    header_hight = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    height = len(options) + header_hight

    menu_console = libtcod.console_new(width, height)

    libtcod.console_set_default_foreground(menu_console, libtcod.white)
    libtcod.console_print_rect_ex(menu_console, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    # Print options.
    y = header_hight
    letter_index = ord(u"a")
    for option_text in options:
        text = "(%s) %s" % (chr(letter_index), option_text)
        libtcod.console_print(menu_console, 0, y, text)
        y += 1
        letter_index += 1

    x = SCREEN_WIDTH / 2 - width / 2
    y = SCREEN_HEIGHT / 2 - height / 2
    libtcod.console_blit(menu_console, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    index = key.c - ord(u"a")
    if index >= 0 and index < len(options):
        return index
    return None

def planet_menu(header, target_planet):
    abilities = spacevessel.abilities
    if len(abilities) == 0:
        abilities_name_list = [u"Ты ничего не можешь сделать."]
    else:
        abilities_name_list = [a.name for a in abilities]
    index = choice_menu(header, abilities_name_list, PLANET_MENU_WIDTH)
    if index is None:
        return None
    return abilities[index].use(target_planet, spacevessel)

def display_spacevessel_info(console, foreground_col=libtcod.grey):
    libtcod.console_set_default_foreground(console, libtcod.darker_amber)
    libtcod.console_print(console, 1, 1, u"  -- Судно --")
    libtcod.console_print(console, 1, 2, u"Износ      : %s/%s" % (spacevessel.wear, spacevessel.hull))
    libtcod.console_print(console, 1, 3,
            u"Стойкость: %s" % spacevessel.wear_resistance)
    libtcod.console_print(console, 1, 4,
            u"Двигатель: %s" % spacevessel.propulsion)

    libtcod.console_set_default_foreground(console, libtcod.grey)
    libtcod.console_print(console, 1, 6,
            u"  -- Трюмы --")
    libtcod.console_print(console, 1, 7,
            u"Вода     : %s" % spacevessel.cargo_info(CARGO_WATER))
    libtcod.console_print(console, 1, 8,
            u"Минералы  : %s" % spacevessel.cargo_info(CARGO_MINERALS))
    
    libtcod.console_set_default_foreground(console, libtcod.darker_lime)
    libtcod.console_print(console, 1, 10,
            u"  -- Человек --")
    libtcod.console_print(console, 1, 11,
            u"Жизнь: %s/%s" % (player.life_cur, player.life_max))
    libtcod.console_print(console, 1, 12,
            u"Ум: %s" % player.intelligence)
    libtcod.console_print(console, 1, 13,
            u"Харизма: %s" % player.charisma)

def message(new_msg, color=libtcod.white):
    msg_lines = textwrap.wrap(new_msg, MSG_CONSOLE_WIDTH)
    for msg_line in msg_lines:
        if  len(game_msgs) == MSG_CONSOLE_HEIGHT - 1:
            del game_msgs[0]
        game_msgs.append((msg_line, color))

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

    libtcod.console_clear(cargo_info_console)
    libtcod.console_clear(msg_console)

    display_spacevessel_info(cargo_info_console)

    y = 1
    for (msg_line, color) in game_msgs:
        libtcod.console_set_default_foreground(msg_console, color)
        libtcod.console_print(msg_console, MSG_X, y,  msg_line)
        y += 1
    libtcod.console_blit(cargo_info_console, 0, 0, SCREEN_WIDTH-MAP_WIDTH, MAP_HEIGHT, 0, MAP_WIDTH, 0)
    libtcod.console_blit(msg_console, 0, 0, MAP_WIDTH, MSG_CONSOLE_HEIGHT, 0, 0, MAP_HEIGHT)


################################
# Initialization & Main Loop
################################

#libtcod.console_set_custom_font("terminal8x8_aa_ro.png", libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
libtcod.console_set_custom_font("consolas_unicode_10x10.png", libtcod.FONT_LAYOUT_ASCII_INROW | libtcod.FONT_TYPE_GRAYSCALE, 32, 64)
#libtcod.console_map_ascii_codes_to_font("А", 32, 0, 5)
#libtcod.console_map_ascii_codes_to_font("а", 32, 0, 6)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, "Sleeping God Alpha", False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
cargo_info_console = libtcod.console_new(SCREEN_WIDTH-MAP_WIDTH, MAP_HEIGHT)
msg_console = libtcod.console_new(MAP_WIDTH, MSG_CONSOLE_HEIGHT)

spacevessel = Vessel(
        pos_x=0, pos_y=0, char=u"@", label=u"игрок",
        color=libtcod.white, blocks=True, cargo={},
        hull=300, wear_resistance=1)
player = Player()
gameobjects = [spacevessel]

spacevessel.add_ability(resource_transfer_ability)
make_map()

fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
for y in xrange(MAP_HEIGHT):
    for x in xrange(MAP_WIDTH):
        libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)

fov_recompute = True
game_state = PLAYING
player_action = None
game_msgs = []

message(u"Космос открывает свои просторы в игре Sleeping God.", libtcod.red)

mouse = libtcod.Mouse()
key = libtcod.Key()

while not libtcod.console_is_window_closed():

    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
    render_all()

    libtcod.console_flush()

    for gameobject in gameobjects:
        gameobject.clear()


    player_action = handle_keys()
    if player_action == EXIT:
        break

    if game_state == PLAYING and player_action != "didnt-take-turn":
        pass
