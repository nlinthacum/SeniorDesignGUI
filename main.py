from PyQt5.QtWidgets import *
from PyQt5 import uic
import json

class HomePageGUI(QMainWindow):

    def __init__(self):
        super(HomePageGUI, self).__init__()
        uic.loadUi("HomePage.ui", self)
        self.show()
        self.create_new_button.clicked.connect(self.OpenCreateNew)
        
        self.saved_seals_handler = SavedSeals()
        self.saved_seals_handler.load_seals()

    def OpenCreateNew(self):
        self.create_new_gui = CreateNewGUI(self.saved_seals_handler)

class CreateNewGUI(QMainWindow):
    def __init__(self, saved_seals_handler):
        super(CreateNewGUI, self).__init__()
        uic.loadUi("CreateNew.ui", self)
        self.show()
        self.create_new_save_button.clicked.connect(self.CreateNewSaved)
        self.saved_seals_handler = saved_seals_handler
        self.saved_seals_handler.load_seals()
     
     #TODO update these values wiith real values
    def CreateNewSaved(self):  
        new_seal = Seal(part_name=str(self.part_name_line.text()), material=str(self.material_line.text()), die_name=str(self.die_name_line.text()), ending_diameter=str(self.ending_diameter_line.text()), notes=str(self.notes_line.text()))
        self.saved_seals_handler.saved_seals.append(new_seal.to_dict())
        self.saved_seals_handler.save_seals()



class Seal:
    def __init__(self, part_name, material, die_name, ending_diameter, notes):
        self.part_name = part_name
        self.material = material
        self.die_name = die_name
        self.ending_diameter = ending_diameter
        self.notes = notes

    def to_dict(self):
        return {
            "part_name": self.part_name,
            "material": self.material,
            "die_name": self.die_name,
            "ending_diameter": self.ending_diameter,
            "notes": self.notes
        }

    def __str__(self):
        return f"Seal - Part Name: {self.part_name}, Material: {self.material}, Ending Distance: {self.ending_distance}"

class SavedSeals:
    def __init__(self):
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
    



def main():
    app = QApplication([])
    window = HomePageGUI()
    app.exec_()


if __name__ == '__main__':
    main()