from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QListWidgetItem, QVBoxLayout
from PyQt5.QtCore import QObject, pyqtSignal
import json

# User defined includes
from socket_transport import *

class HomePageGUI(QMainWindow):

    def __init__(self):
        super(HomePageGUI, self).__init__()
        uic.loadUi("HomePage.ui", self)
        self.show()
        self.create_new_button.clicked.connect(self.OpenCreateNew)
        self.load_library_button.clicked.connect(self.OpenLoadLibrary)
        self.edit_library_button.clicked.connect(self.OpenEditLibrary)
       
        self.part_idx = -1  # Initialize part_idx
       
        
        self.saved_seals_handler = SavedSeals()
        self.saved_seals_handler.load_seals()
        
        # Connect the signal to the DisplayPart method
        self.saved_seals_handler.seals_updated.connect(self.RefreshDisplay)
        
        # Initilize parts loaded visual to nothing
        self.part_label.setText("None")
        self.material_label.setText("")
        self.die_label.setText("")
        self.starting_diameter_label.setText("")
        self.ending_diameter_label.setText("")
        self.notes_label.setText("")

    def OpenCreateNew(self):
        self.create_new_gui = CreateNewGUI(self.saved_seals_handler)

    def OpenLoadLibrary(self):
        self.load_library_gui = LoadFromLibraryGUI(self.saved_seals_handler, self)
    def OpenEditLibrary(self):
        self.edit_library_gui = EditLibraryGUI(self.saved_seals_handler, self)
        

    def DisplayPart(self, part_idx):
        if (part_idx <0):
            self.part_label.setText("None")
            self.material_label.setText("")
            self.die_label.setText("")
            self.starting_diameter_label.setText("")
            self.ending_diameter_label.setText("")
            self.notes_label.setText("")
        else:   
            self.saved_seals_handler.load_seals() #refresh list in case it changed
            part = self.saved_seals_handler.saved_seals[part_idx]
            self.part_label.setText(part['part_name'])
            self.material_label.setText(part['material'])
            self.die_label.setText(part['die_name'])
            self.starting_diameter_label.setText(str(part['starting_diameter']))
            self.ending_diameter_label.setText(str(part['ending_diameter']))
            self.notes_label.setText(part['notes'])
            self.part_idx = part_idx

            # Call routine to send part to the PLC
            SendSeal(15.05, 21.125)#commented out while developing without PLC
        
    def RefreshDisplay(self):
        self.DisplayPart(self.part_idx)



class CreateNewGUI(QMainWindow):
    starting_measurement = -1
    def __init__(self, saved_seals_handler):
        super(CreateNewGUI, self).__init__()
        uic.loadUi("CreateNew.ui", self)
        self.show()
        self.create_new_save_button.clicked.connect(self.CreateNewSaved)
        self.set_starting_position_button.clicked.connect(self.SetStartingPosition)
        self.saved_seals_handler = saved_seals_handler
        self.saved_seals_handler.load_seals()
     
    def CreateNewSaved(self):  
        new_seal = Seal(part_name=str(self.part_name_line.text()), material=str(self.material_line.text()), die_name=str(self.die_name_line.text()), starting_diameter=str(self.starting_diameter_line.text()), starting_measurement= self.starting_measurement, ending_diameter=str(self.ending_diameter_line.text()), notes=str(self.notes_line.text()))
        self.saved_seals_handler.saved_seals.append(new_seal.to_dict())
        self.saved_seals_handler.save_seals()
        self.close()
    def SetStartingPosition(self):
         self.set_starting_position_gui = SetStartingPositionGUI(self.saved_seals_handler, self)
         SendSetupNewPart()
        
class SetStartingPositionGUI(QMainWindow):
    def __init__(self, saved_seals_handler, parent=None):
        super(SetStartingPositionGUI, self).__init__(parent)
        uic.loadUi("SetStartingPosition.ui", self)
        self.show()
        
        self.starting_position_save_button.clicked.connect(self.SaveStartingPosition)
        
    def SaveStartingPosition(self):
        self.parent().starting_diameter_line.setText(self.measured_starting_diameter_line.text())
        byte_measurement = SendSavedStarting()
        self.parent().starting_measurement = byte_measurement.decode("utf-8")
        print(f"Received this message in GUI: {self.parent().starting_measurement}\n")

        self.close()
        

# LoadFromLibraryList is name of list
class LoadFromLibraryGUI(QMainWindow):
    def __init__(self, saved_seals_handler, parent=None):
        super(LoadFromLibraryGUI, self).__init__(parent)
        uic.loadUi("LoadFromLibrary.ui", self)
        self.show()
        self.saved_seals_handler = saved_seals_handler
        self.saved_seals_handler.load_seals()
        self.PopulateList(saved_seals_handler)
        self.load_button.clicked.connect(self.LoadToMain)

    
    def PopulateList(self, saved_seals_handler):
        # Populate QListWidget with data
        for item_data in self.saved_seals_handler.saved_seals:
            list_item = QListWidgetItem(f"{item_data['part_name']} - {item_data['material']} - {item_data['die_name']}")

            list_item.setData(1, item_data)  # Store the entire data in the item's data
            self.LoadFromLibraryList.addItem(list_item)
    def LoadToMain(self):
        # getting current selected row
        part_idx = self.LoadFromLibraryList.currentRow()
        print(self.parent())
        self.parent().DisplayPart(part_idx)
        self.close()


class EditLibraryGUI(QMainWindow):
    def __init__(self, saved_seals_handler,parent=None):
        super(EditLibraryGUI, self).__init__(parent)
        uic.loadUi("EditLibrary.ui", self)
        self.show()
        self.saved_seals_handler = saved_seals_handler
        
        self.edit_save_button.clicked.connect(self.EditSaved)
        self.delete_part_button.clicked.connect(self.DeletePart)
        self.edit_starting_diameter_button.clicked.connect(self.EditStartingDiameter)
        
         # Populate QListWidget with data
        for item_data in self.saved_seals_handler.saved_seals:
            list_item = QListWidgetItem(f"{item_data['part_name']} - {item_data['material']} - {item_data['die_name']}")

            list_item.setData(1, item_data)  # Store the entire data in the item's data
            self.LoadFromLibraryList.addItem(list_item)
       
    #    Update every time the selected line changes
        self.LoadFromLibraryList.currentRowChanged.connect(self.update_text)
        
         # Set values for the initially selected row
        self.update_text(self.LoadFromLibraryList.currentRow())
         
    def update_text(self, selected_row):
        if selected_row >= 0:
            part_data = self.saved_seals_handler.saved_seals[selected_row]
            self.part_name_line.setText(part_data['part_name'])
            self.material_line.setText(part_data['material'])
            self.die_name_line.setText(part_data['die_name'])
            self.starting_diameter_line.setText(str(part_data['starting_diameter']))
            self.ending_diameter_line.setText(str(part_data['ending_diameter']))
            self.notes_line.setText(part_data['notes'])
    def EditSaved(self):
        part_idx = self.LoadFromLibraryList.currentRow()
        new_seal = Seal(part_name=str(self.part_name_line.text()), material=str(self.material_line.text()), die_name=str(self.die_name_line.text()),starting_diameter=str(self.starting_diameter_line.text()), ending_diameter=str(self.ending_diameter_line.text()), notes=str(self.notes_line.text()))
        self.saved_seals_handler.saved_seals[part_idx] = new_seal.to_dict()
        self.saved_seals_handler.save_seals()
        self.close()
    def DeletePart(self):
        part_idx = self.LoadFromLibraryList.currentRow()
        self.parent().part_idx = -1 #to void any currently loaded part. Needed becasue delete changes the index of items
        self.saved_seals_handler.saved_seals.pop(part_idx)
        self.saved_seals_handler.save_seals()
        self.close()
    def EditStartingDiameter(self):
        self.set_starting_position_gui = SetStartingPositionGUI(self.saved_seals_handler, self)
        
  
    
    
        
    

class Seal:
    def __init__(self, part_name, material, die_name, starting_diameter, starting_measurement, ending_diameter, notes):
        self.part_name = part_name
        self.material = material
        self.die_name = die_name
        self.starting_diameter = starting_diameter
        self.starting_measurement = starting_measurement
        self.ending_diameter = ending_diameter
        self.notes = notes


    def to_dict(self):
        return {
            "part_name": self.part_name,
            "material": self.material,
            "die_name": self.die_name,
            "starting_diameter": self.starting_diameter,
            "starting_measurement": self.starting_measurement,
            "ending_diameter": self.ending_diameter,
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

    



def main():
    app = QApplication([])
    window = HomePageGUI()
    app.exec_()


if __name__ == '__main__':
    main()