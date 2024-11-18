#!/bin/bash

byobu new-session -d -s pp
byobu select-pane -t 0
byobu split-window -v
byobu select-pane -t 0

byobu send-keys -t 0 'xhost + && docker exec -it sda5f_container bash -it -c "roslaunch motoman_sda5f_support bringup.launch robot_ip:=10.0.0.2 controller:=fs100 fake_execution:=false"' 'C-m'
sleep 3.
byobu send-keys -t 0 'xhost + && docker exec -it sda5f_container bash -it -c "rosservice call robot_enable"' 'C-m'
sleep 1.
byobu send-keys -t 1 'xhost + && docker exec -it sda5f_container bash -it -c "roslaunch sda5f_motion_plan demo_pickplace.launch fake_execution:=false planning_space:=joint"' 'C-m'

byobu attach -t pp
