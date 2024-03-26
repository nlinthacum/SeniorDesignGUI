# Python code that logs the start and end measurements from the PLC

from os import wait
import socket
import time
import csv
import datetime
from seals_implementation import *

csv_filename = 'stretcher_log.csv'

def logging_routine(data):
    print("in the logging routine with data: " + str(data))

def append_distances_to_csv(part, start_measurement, end_measurement, stretch_duration):

    name = part['part_name']
    print("This part name: " + str(name))

    # Define the headers for the CSV file
    headers = ['Seal Name', 'Material', 'Speed (in/min)', 'Timestamp', 'Stretch Duration (s)', 'Start Target Measurement (in)', 'End Target Measurement (in)', \
               'Start Measurement (in)', 'End Measurement (in)']

    # Prepare the data to be written to the CSV file
    # Note: part['starting_measurement'] and part['ending_measurement'] refer to the target positions
    data = [part['part_name'], part['material'], part['speed'], datetime.datetime.now(), stretch_duration, part['starting_measurement'], \
            part['ending_measurement'], start_measurement, end_measurement]

    # Check if the file already exists or not
    file_exists = True
    try:
        # Attempt to open the file in read mode to check if it exists
        with open(csv_filename, 'r') as f:
            pass
    except FileNotFoundError:
        # If the file doesn't exist, set the flag to False
        file_exists = False

    # Open the CSV file in append mode and write the data
    with open(csv_filename, 'a', newline='') as f:
        writer = csv.writer(f)
        
        # Write headers only if the file doesn't exist
        if not file_exists:
            writer.writerow(headers)
        
        # Write the data
        writer.writerow(data)

# Old Example usage:
# start_distance = 10
# end_distance = 20
# csv_filename = 'stretcher_log.csv'
# append_distances_to_csv(start_distance, end_distance, csv_filename)


