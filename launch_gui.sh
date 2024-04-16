#!/bin/bash
sudo ip link set eth0 up
sudo ip addr add 10.66.66.1/24 dev eth0
sudo ip route add 192.168.1.177 via 10.66.66.1   
cd /home/jetseal/GUI
python main.py