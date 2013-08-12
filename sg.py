#!/usr/bin/python2
# -*- coding: utf-8 -*-


import random
import textwrap
import libtcodpy as libtcod

from Constants import *
from SleepingGodObjects.GameObjects import GameObject
from SleepingGodObjects.Vessel import Vessel, PlayerVessel
from SleepingGodObjects.Planet import Planet
from SleepingGodObjects.Player import Player
from SleepingGodObjects.Tile import Tile

from SleepingGodEngine.Ability import Ability, AutoAbility


# System star coordinates. Always at center.
systemstar_x = MAP_WIDTH / 2
systemstar_y = MAP_HEIGHT / 2








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

def landing_and_repair_vessel():
    spacevessel.wear = spacevessel.hull
    message(u"Ты приземлился на планете и починил своё судно.", libtcod.dark_chartreuse)

resource_transfer_ability = Ability(name=u"Извлечение ресурсов",
                                    description=u"",
                                    use_function=transfer_resources)
repair_ability = AutoAbility(name=u"Призмелиться и чинить судно.",
                         description=u"",
                         use_function=landing_and_repair_vessel)



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
            message(u"Перед тобою %s." % target.label, libtcod.darker_amber)
    else:
        spacevessel.move(dx, dy)
        fov_recompute = True


def handle_keys():
    global key
    #key = libtcod.console_wait_for_keypress(True)

    if key.vk == libtcod.KEY_ESCAPE:
        return "exit"

    if game_state == PLAYING:
        if key.vk == libtcod.KEY_UP:
            spacevessel_move_or_attack(0, -1)
        elif key.vk == libtcod.KEY_DOWN:
            spacevessel_move_or_attack(0, 1)
        elif key.vk == libtcod.KEY_LEFT:
            spacevessel_move_or_attack(-1, 0)
        elif key.vk == libtcod.KEY_RIGHT:
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
                spaceobject = Vessel(x, y, u"v", u"судно", libtcod.desaturated_green, True)
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

def get_spacevessel_info():
    spacevessel_info = [
        u" -- Судно -- ",
        u"Износ: %s/%s" % (spacevessel.wear, spacevessel.hull),
        u"Стойкость: %s" % spacevessel.wear_resistance,
        u"Двигатель: %s" % spacevessel.propulsion,
        u"Кислород: %s/%s" % (spacevessel.oxygen, spacevessel.oxygen_max),
        u" ",
        u" -- Трюмы -- ",
        u"Вода: %s" % spacevessel.cargo_info(CARGO_WATER),
        u"Минералы: %s" % spacevessel.cargo_info(CARGO_MINERALS),
        u" ",
        u" -- Человек -- ",
        u"Жизнь: %s/%s" % (player.life_cur, player.life_max),
        u"Ум: %s" % player.intelligence,
        u"Харизма: %s" % player.charisma
        ]
    return spacevessel_info


def display_spacevessel_info(console, spacevessel_info, foreground_col=libtcod.grey):
    libtcod.console_set_default_foreground(console, foreground_col)
    y = 1
    for each in spacevessel_info:
        libtcod.console_print(console, 1, y, each)
        y += 1

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
        gameobject.draw(con, fov_map)

    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    libtcod.console_clear(cargo_info_console)
    libtcod.console_clear(msg_console)

    display_spacevessel_info(cargo_info_console, get_spacevessel_info())

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

libtcod.console_set_custom_font("consolas_unicode_10x10.png", libtcod.FONT_LAYOUT_ASCII_INROW | libtcod.FONT_TYPE_GRAYSCALE, 32, 64)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, "Sleeping God Alpha", False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
cargo_info_console = libtcod.console_new(SCREEN_WIDTH-MAP_WIDTH, MAP_HEIGHT)
msg_console = libtcod.console_new(MAP_WIDTH, MSG_CONSOLE_HEIGHT)

spacevessel = PlayerVessel(
        pos_x=0, pos_y=0, char=u"@", label=u"игрок",
        color=libtcod.white, blocks=True, cargo={},
        oxygen=500,
        hull=300, wear_resistance=1)
player = Player()
gameobjects = [spacevessel]

spacevessel.add_ability(resource_transfer_ability)
spacevessel.add_ability(repair_ability)

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
        gameobject.clear(con)


    player_action = handle_keys()
    if player_action == EXIT:
        break

    if game_state == PLAYING and player_action != "didnt-take-turn":
        pass
