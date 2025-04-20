# sda5f_tutorials

[![support level: community](https://img.shields.io/badge/support%20level-community-lightgray.svg)](http://rosindustrial.org/news/2016/10/7/better-supporting-a-growing-ros-industrial-software-platform)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![License: BSD](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
![repo size](https://img.shields.io/github/repo-size/UOsaka-Harada-Laboratory/sda5f_tutorials)

- ROS packages for YASKAWA MOTOMAN SDA5F tutorial.
  - [sda5f_motion_plan](/catkin_ws/src/sda5f_motion_plan): A package to execute example motions with dual arms.
  - [sda5f_stack](/catkin_ws/src/sda5f_stack): A stack of ros packages to control the motoman sda5f.
- Docker for simulation and control environments for YASKAWA MOTOMAN SDA5F.

## Dependencies

### Docker build environment

- [Ubuntu 22.04 PC](https://ubuntu.com/certified/laptops?q=&limit=20&vendor=Dell&vendor=Lenovo&vendor=HP&release=22.04+LTS)
  - NVIDIA GeForce RTX3070
    - NVIDIA Driver 470.199.02
    - CUDA 11.4
  - Docker 23.0.1
  - Docker Compose 2.4.1
  - NVIDIA Docker 2.12.0

### SDA5F with OnRobot grippers

- [Ubuntu 20.04 PC](https://ubuntu.com/certified/laptops?q=&limit=20&vendor=Dell&vendor=Lenovo&vendor=HP&release=20.04+LTS)
  - [ROS Noetic](https://wiki.ros.org/noetic/Installation/Ubuntu)
    - [onrobot](https://github.com/UOsaka-Harada-Laboratory/onrobot)
    - [Byobu](https://www.byobu.org/)
- [YASKAWA Motoman SDA5F](https://www.motoman.com/en-us/products/robots/industrial/assembly-handling/sda-series/sda5f)  
- [OnRobot RG6](https://onrobot.com/en/products/rg6-gripper)
- [OnRobot VGC10](https://onrobot.com/en/products/vgc10)

## Installation

### Teach pendant

1. Follow the instructions on [ROS Wiki](https://wiki.ros.org/motoman_driver/Tutorials).

### Host machine

1. Connect an Ethernet cable between the host computer and the Ethernet port of SDA5F's controller
2. Set the network configuration as below  
    <img src=image/network.png width=280>  
    - The ros node expects to reach the robot at the IP `10.0.0.2`. You can change the IP with pendant  
        <img src=image/pendant_network.jpeg width=280>  
    - This IP is set to the `robot_ip` argument as below  
        ```bash
        roslaunch motoman_sda5f_support roslaunch bringup.launch robot_ip:=10.0.0.2 controller:=fs100 fake_execution:=false
        ```
3. Build the docker environment as below  
    ```bash
    sudo apt install byobu && git clone git@github.com:UOsaka-Harada-Laboratory/sda5f_tutorials.git --depth 1 && cd sda5f_tutorials && COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker compose build --no-cache --parallel   
    ```

## Usage with docker

### Using utility scripts

1. Build and run the docker environment
    - Create and start docker containers in the initially opened terminal
        ```bash
        docker compose up
        ```

#### Simulation

2. Run a demonstration on the host machine

    - Visualizing the model  
        ```bash
        ./utils/sda5f_rviz.sh
        ```  
        <img src=image/sda5f_rviz.sh.gif height=300>

    - Executing the moveit  
        ```bash
        ./utils/sda5f_moveit_sim.sh
        ```  
        <img src=image/sda5f_moveit_sim.sh.gif height=300>

    - Executing a waving-arms demonstration  
        ```bash
        ./utils/sda5f_wavearms_fake.sh
        ```  
        <img src=image/sda5f_wavearms_fake.sh.gif height=300>

    - Executing a pick-and-place demonstration  
        ```bash
        ./utils/sda5f_pickplace_fake.sh
        ```  
        <img src=image/sda5f_pickplace_fake.sh.gif height=300>

#### Real robot

2. Turn on the controller FS100  
    <img src=image/controller.jpeg width=200>

3. Switch the key's direction to Remote  
    <img src=image/pendant_key.jpeg width=200>

4. Run a demonstration on the host machine  

   - Executing the moveit  
     ```bash
     ./utils/sda5f_moveit_real.sh
     ```  
     <img src=image/sda5f_moveit_real.sh.gif height=300>

   - Executing a waving-arms demonstration  
     ```bash
     ./utils/sda5f_wavearms.sh
     ```  
     <img src=image/sda5f_wavearms.sh.gif height=300>

   - Executing a pick-and-place demonstration  
     ```bash
     ./utils/sda5f_pickplace.sh
     ```  
     <img src=image/sda5f_pickplace.sh.gif height=300>

### Manually execute commands

1. Build and run the docker environment
    - Create and start docker containers in the initially opened terminal
        ```bash
        docker compose up
        ```
    - Execute the container in another terminal
        ```bash
        xhost + && docker exec -it sda5f_container bash
        ```

2. Run a demonstration in the container  
    ```bash
    byobu
    ```
    - First command & F2 to create a new window & Second command ...
    - Ctrl + F6 to close the selected window

## Author / Contributor

[Takuya Kiyokawa](https://takuya-ki.github.io/)  
[Tomohiro Motoda](https://tomohiromotoda.github.io/)

We always welcome collaborators!

## License

Please refer to each package.xml of the ROS packages
