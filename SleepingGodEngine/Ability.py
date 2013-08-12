#!/usr/bin/python2
# -*- coding: utf-8 -*-



class Ability:
    def __init__(
                 self,
                 name,
                 description,
                 use_function=None):
        self.name = name
        self.description = description
        self.use_function = use_function

    def use(self, *args):
        if self.use_function is None:
            message(u"%s не может быть использовано." % self.name)
        else:
            self.use_function(*args)


class AutoAbility(Ability):
    def __init__(
                 self,
                 name,
                 description,
                 use_function=None):

        Ability.__init__(
                         self,
                         name,
                         description,
                         use_function)

    def use(self, *args):
        if self.use_function is None:
            message(u"%s не может быть использовано." % self.name)
        else:
            self.use_function()


