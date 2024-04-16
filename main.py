#!/usr/bin/env python
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QListWidgetItem, QVBoxLayout
from PyQt5.QtCore import QObject, pyqtSignal
import json
import threading, time, os, signal, multiprocessing
from multiprocessing import Process, Value

# User defined includes
from socket_transport import *
import PasswordUtil
from seals_implementation import *

# This class contains the functionality for the Home Page of the GUI
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
        self.speed_label.setText("") 
        self.notes_label.setText("")

# Function to call when Create New button is pressed on the home page
    def OpenCreateNew(self):
        self.create_new_gui = CreateNewGUI(self.saved_seals_handler)

# Function to call when Open Library button is pressed on the home page
    def OpenLoadLibrary(self):
        self.load_library_gui = LoadFromLibraryGUI(self.saved_seals_handler, self)

# Function to call when Edit Library button is pressed on the home page 
    def OpenEditLibrary(self):
        self.edit_library_gui = EnterPasswordGUI(self.saved_seals_handler, self)

# Displays the loaded seal to the home page of the GUI, if no seal is loaded, display nothing
    def DisplayPart(self, part_idx):
        # part index -1 means no part loaded
        if (part_idx <0):
            self.part_label.setText("None")
            self.material_label.setText("")
            self.die_label.setText("")
            self.starting_diameter_label.setText("")
            self.ending_diameter_label.setText("")
            self.speed_label.setText("")
            self.notes_label.setText("")
        else:   
            self.saved_seals_handler.load_seals() #refresh list in case it changed
            part = self.saved_seals_handler.saved_seals[part_idx]
            self.part_label.setText(part['part_name'])
            self.material_label.setText(part['material'])
            self.die_label.setText(part['die_name'])
            self.starting_diameter_label.setText(str(part['starting_diameter']))
            self.ending_diameter_label.setText(str(part['ending_diameter']))
            self.speed_label.setText(str(part['speed']))
            self.notes_label.setText(part['notes'])
            self.part_idx = part_idx

            # Call routine to send part to the PLC
            SendSeal(part['starting_measurement'], part['ending_measurement'], part['speed'], part_idx)#commented out while developing without PLC

# Refresh dispaly seal when its updated 
    def RefreshDisplay(self):
        self.DisplayPart(self.part_idx)
    
# When the GUI is closed, send kill sig
    def closeEvent(self, event):
        global heartbeat_kill_sig
        heartbeat_kill_sig.value = 1
        event.accept()
        


# Class for the Create New GUI
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
    
    # When new seal is saved, save the components in the saved seals object
    def CreateNewSaved(self):  
        ending_measurement = float(self.starting_measurement) + (float(self.ending_diameter_line.text()) - float(self.starting_diameter_line.text()))
        new_seal = Seal(part_name=str(self.part_name_line.text()), material=str(self.material_line.text()), die_name=str(self.die_name_line.text()), starting_diameter=str(self.starting_diameter_line.text()), starting_measurement= self.starting_measurement, ending_diameter=str(self.ending_diameter_line.text()), ending_measurement=str(ending_measurement), speed=str(self.speed_line.text()),notes=str(self.notes_line.text()))
        self.saved_seals_handler.saved_seals.append(new_seal.to_dict())
        self.saved_seals_handler.save_seals()
        self.close()
    # Open Set Starting position GUI when set starting position pressed
    def SetStartingPosition(self):
         self.set_starting_position_gui = SetStartingPositionGUI(self.saved_seals_handler, self)
         SendSetupNewPart()
        
# Class for set starting position GUI
class SetStartingPositionGUI(QMainWindow):
    def __init__(self, saved_seals_handler, parent=None):
        super(SetStartingPositionGUI, self).__init__(parent)
        uic.loadUi("SetStartingPosition.ui", self)
        self.show()
        self.starting_position_save_button.clicked.connect(self.SaveStartingPosition)
        
# Save starting position is pressed let the PLC know and receive value from PLC
    def SaveStartingPosition(self):
        self.parent().starting_diameter_line.setText(self.measured_starting_diameter_line.text())
        byte_measurement = SendSavedStarting()
        self.parent().starting_measurement = byte_measurement.decode("utf-8")
        print(f"Received this message in GUI: {self.parent().starting_measurement}\n")
        self.close()
    
    def closeEvent(self, event):
        event.accept() #close the window
        

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

    # Fill the list of seals in library
    def PopulateList(self, saved_seals_handler):
        # Populate QListWidget with data
        for item_data in self.saved_seals_handler.saved_seals:
            list_item = QListWidgetItem(f"{item_data['part_name']} - {item_data['material']} - {item_data['die_name']}")
            list_item.setData(1, item_data)  # Store the entire data in the item's data
            self.LoadFromLibraryList.addItem(list_item)

    # Load the selected part to the main gui page
    def LoadToMain(self):
        # getting current selected row
        part_idx = self.LoadFromLibraryList.currentRow()
        print(self.parent())
        self.parent().DisplayPart(part_idx)
        self.close()

# Class for editing the library of seals
class EditLibraryGUI(QMainWindow):
    starting_measurement = -1
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
            self.speed_line.setText(str(part_data['speed']))
            self.notes_line.setText(part_data['notes'])
            self.starting_measurement = part_data['starting_measurement']

#Update the edited seal
    def EditSaved(self):
        part_idx = self.LoadFromLibraryList.currentRow()
        ending_measurement = float(self.starting_measurement) + (float(self.ending_diameter_line.text()) - float(self.starting_diameter_line.text()))
        new_seal = Seal(part_name=str(self.part_name_line.text()), material=str(self.material_line.text()), die_name=str(self.die_name_line.text()), starting_diameter=str(self.starting_diameter_line.text()), starting_measurement= self.starting_measurement, ending_diameter=str(self.ending_diameter_line.text()), ending_measurement=str(ending_measurement), speed=str(self.speed_line.text()), notes=str(self.notes_line.text()))
        self.saved_seals_handler.saved_seals[part_idx] = new_seal.to_dict()
        self.saved_seals_handler.save_seals()
        self.close()
    # Remove a seal
    def DeletePart(self):
        part_idx = self.LoadFromLibraryList.currentRow()
        self.parent().part_idx = -1 #to void any currently loaded part. Needed becasue delete changes the index of items
        self.saved_seals_handler.saved_seals.pop(part_idx)
        self.saved_seals_handler.save_seals()
        self.close()
    # Edit the starting diameter functionality
    def EditStartingDiameter(self):
        self.set_starting_position_gui = SetStartingPositionGUI(self.saved_seals_handler, self)
        SendSetupNewPart()
        
# Class for the password functionality for editing seals  
class EnterPasswordGUI(QMainWindow):
    def __init__(self, saved_seals_handler,parent=None):
        super(EnterPasswordGUI, self).__init__(parent)
        uic.loadUi("EnterPassword.ui", self)
        self.show()
        self.saved_seals_handler = saved_seals_handler
        self.enter_button.clicked.connect(self.PasswordEnter)
        self.password_label.setText("") 
     
    def PasswordEnter(self):  
        entered_password = str(self.password_line.text())
        if (PasswordUtil.CheckPassword(entered_password)):
            self.edit_library_gui = EditLibraryGUI(self.saved_seals_handler, self)
            self.close()
        else:
            self.password_label.setText("Incorrect Password!") 

heartbeat_kill_sig = multiprocessing.Value('i', 0)
heartbeat_kill_sig.value = 0 
heartbeat_process = Process(target=Heartbeat, args=(heartbeat_kill_sig,))

def main():
    InitializeConnection()
    app = QApplication([])
    window = HomePageGUI()
    
    heartbeat_kill_sig.value = 0 
    heartbeat_process = Process(target=Heartbeat, args=(heartbeat_kill_sig,))
    heartbeat_process.start()


    app.exec_()
    


if __name__ == '__main__':
    main()