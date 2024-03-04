#!/bin/bash
sudo ip route add 192.168.1.177 via 192.168.77.2
cd /home/jetseal/GUI
python main.py