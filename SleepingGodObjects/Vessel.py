#!/usr/bin/python2
# -*- coding: utf-8 -*-


from Constants import WEAR_AT_TURN, OXYGEN_AT_TURN, CARGO_WATER, CARGO_MINERALS
from SleepingGodObjects.GameObjects import GameObject


class Vessel(GameObject):
    def __init__(
                 self,
                 pos_x,
                 pos_y,
                 char,
                 label,
                 color,
                 blocks,
                 cargo={},
                 oxygen=0,
                 hull=0,
                 wear_resistance=0):

        GameObject.__init__(
                            self,
                            pos_x,
                            pos_y,
                            char,
                            label,
                            color,
                            blocks)

        self.cargo = cargo
        self.cargo_keys = [
                CARGO_WATER,
                CARGO_MINERALS
                          ]
        for key in self.cargo_keys:
            if not self.cargo.has_key(key):
                self.cargo[key] = 0
        self.oxygen = oxygen
        self.oxygen_max = oxygen
        self.hull = hull
        self.wear = hull
        self.wear_resistance = wear_resistance

    def move(self, dx, dy):
       self.pos_x += dx
       self.pos_y += dy
       turn_wear = WEAR_AT_TURN - self.wear_resistance
       self.wear -= turn_wear
       self.oxygen -= OXYGEN_AT_TURN

    def cargo_info(self, key):
        if self.cargo.has_key(key):
            return self.cargo[key]



class PlayerVessel(Vessel):

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
                 oxygen=0,
                 hull=0,
                 wear_resistance=0,
                 propulsion=SOLAR_SAIL):

        Vessel.__init__(
                        self,
                        pos_x,
                        pos_y,
                        char,
                        label,
                        color,
                        blocks,
                        cargo,
                        oxygen,
                        hull,
                        wear_resistance)

        self.propulsion = propulsion
        self.abilities = []

    def increase_resources(self, minerals, water):
        self.cargo[CARGO_MINERALS] += minerals
        self.cargo[CARGO_WATER] += water

    def add_ability(self, ability):
        self.abilities.append(ability)

    def get_ability_name(self, abilitY):
        return ability.name

    def get_ability_description(self, ability):
        return ability.description

    def use_ability(self, ability, *args):
        if ability in self.abilities:
            ability.use(args)
