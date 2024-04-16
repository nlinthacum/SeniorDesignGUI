#implementation of Seal class and SavedSeals class as used in the GUI
# seals are saved in JSON format in the SavedSeals.json file

#!/usr/bin/env python
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject, pyqtSignal
import json
import threading, time, os, signal, multiprocessing

class Seal:
    def __init__(self, part_name, material, die_name, starting_diameter, starting_measurement, ending_diameter, ending_measurement, speed, notes):
        self.part_name = part_name
        self.material = material
        self.die_name = die_name
        self.starting_diameter = starting_diameter
        self.starting_measurement = starting_measurement
        self.ending_diameter = ending_diameter
        self.ending_measurement = ending_measurement
        self.speed = speed
        self.notes = notes


    def to_dict(self):
        return {
            "part_name": self.part_name,
            "material": self.material,
            "die_name": self.die_name,
            "starting_diameter": self.starting_diameter,
            "starting_measurement": self.starting_measurement,
            "ending_diameter": self.ending_diameter,
            "ending_measurement": self.ending_measurement,
            "speed": self.speed,
            "notes": self.notes
        }

    def __str__(self):
        return f"Seal - Part Name: {self.part_name}, Material: {self.material}, Ending Distance: {self.ending_distance}"

class SavedSeals(QObject):
    seals_updated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.saved_seals = list()

    def load_seals(self):
        try:
            with open("SavedSeals.json", 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.saved_seals = data
                else:
                    print("Invalid data format in SavedSeals.json. Expected a list.")
        except FileNotFoundError:
            print("SavedSeals.json not found. Creating a new file.")

    def save_seals(self):
        with open("SavedSeals.json", 'w') as f:
            json.dump(self.saved_seals, f, indent=2)
        self.seals_updated.emit()  # Emit the signal when the list is updated