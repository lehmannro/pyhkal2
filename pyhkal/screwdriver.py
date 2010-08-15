#!/usr/bin/env python

import yaml

class Screwdriver(object):
    def __init__(self, location):
        self.location = location
        self.montage = {}
        self.screw()

    def __getitem__(self, item):
        return self.montage[item]

    def get(self, item, default=None):
        return self.montage.get(item, default)

    def screw(self):
        with open(self.location) as f:
            self.montage.update(yaml.load(f))
