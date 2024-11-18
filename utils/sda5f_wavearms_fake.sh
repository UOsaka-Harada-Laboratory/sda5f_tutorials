#!/bin/bash

byobu new-session -d -s pp_fake
byobu select-pane -t 0
byobu split-window -h
byobu select-pane -t 0
byobu split-window -h

byobu send-keys -t 0 'xhost + && docker exec -it sda5f_container bash -it -c "roslaunch motoman_sda5f_support bringup.launch robot_ip:=10.0.0.2 controller:=fs100 fake_execution:=true"' 'C-m'
sleep 3.
byobu send-keys -t 2 'xhost + && docker exec -it sda5f_container bash -it -c "roslaunch sda5f_motion_plan demo_wavearms.launch fake_execution:=true"' 'C-m'

byobu attach -t pp_fake
