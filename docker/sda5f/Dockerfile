FROM nvidia/opengl:1.2-glvnd-devel-ubuntu20.04

# setting environmental variables
ENV DEBIAN_FRONTEND noninteractive

RUN apt update -y && apt install -y --no-install-recommends curl lsb-release wget gnupg
RUN sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
RUN curl -sSL 'http://keyserver.ubuntu.com/pks/lookup?op=get&search=0xC1CF6E31E6BADE8868B172B4F42ED6FBAB17C654' | apt-key add -

RUN apt update -y && apt install -y --no-install-recommends tzdata
RUN apt update -y && apt install -y --no-install-recommends \
    ros-noetic-desktop-full \
    ros-noetic-gazebo-ros-pkgs \
    ros-noetic-gazebo-ros-control \
    ros-noetic-ros-control \
    ros-noetic-ros-controllers \
    ros-noetic-control-toolbox \
    ros-noetic-moveit \
    ros-noetic-effort-controllers \
    ros-noetic-forward-command-controller \
    ros-noetic-joint-state-controller \
    ros-noetic-joint-trajectory-controller \
    ros-noetic-joint-state-publisher-gui \
    ros-noetic-position-controllers \
    ros-noetic-velocity-controllers \
    ros-noetic-tf \
    ros-noetic-tf2-tools \
    ros-noetic-robot-state-publisher \
    ros-noetic-genpy \
    ros-noetic-industrial-core \
    ros-noetic-roslint \
    ros-noetic-trac-ik-kinematics-plugin \
    software-properties-common \
    python3-osrf-pycommon \
    python3-catkin-tools \
    libcanberra-gtk* \
    build-essential \
    python3-rosdep \
    libudev-dev \
    python3-pip \
    imagemagick \
    net-tools \
    byobu \
    dbus \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /catkin_ws/src && \
    /bin/bash -c "cd /catkin_ws/src && source /opt/ros/noetic/setup.bash && catkin_init_workspace" && \
    /bin/bash -c "cd /catkin_ws && source /opt/ros/noetic/setup.bash && catkin build" && \
    echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc && \
    echo "source /catkin_ws/devel/setup.bash" >> ~/.bashrc && \
    echo "export ROS_PACKAGE_PATH=\${ROS_PACKAGE_PATH}:/catkin_ws" >> ~/.bashrc && \
    echo "export ROS_WORKSPACE=/catkin_ws" >> ~/.bashrc

WORKDIR /catkin_ws/src/
RUN git clone https://github.com/ros-industrial/industrial_core.git -b melodic \
    && cd industrial_core \
    && git reset --hard edcffadd039b413b126eac8eb49b655f4c1cc00b
RUN git clone https://github.com/UOsaka-Harada-Laboratory/onrobot.git \
    && cd onrobot \
    && git reset --hard cf4399b848461977851c37a3a832a2352d8db369
RUN git clone https://github.com/roboticsgroup/roboticsgroup_upatras_gazebo_plugins.git \
    && cd roboticsgroup_upatras_gazebo_plugins \
    && git reset --hard 15187abc17f22dbd3fa720d70ad50de74a668b7c
WORKDIR /catkin_ws/
RUN pip install pyassimp==4.1.3 --ignore-installed

# Generates bash commands
WORKDIR /catkin_ws/src/
# real robot
RUN echo "roslaunch motoman_sda5f_support bringup.launch robot_ip:=10.0.0.2 controller:=fs100 fake_execution:=false" >> ~/.bash_history
RUN echo "roslaunch motoman_sda5f_moveit_config demo_wavearms.launch fake_execution:=false" >> ~/.bash_history
RUN echo "roslaunch sda5f_motion_plan demo_pickplace.launch fake_execution:=false planning_space:=joint" >> ~/.bash_history
# simulation
RUN echo "roslaunch motoman_sda5f_support test_sda5f_with_onrobot.launch" >> ~/.bash_history
RUN echo "roslaunch motoman_sda5f_moveit_config demo_sim.launch" >> ~/.bash_history
RUN echo "rosrun sda5f_motion_plan object_tf_publisher.py" >> ~/.bash_history
RUN echo "roslaunch motoman_sda5f_support bringup.launch robot_ip:=10.0.0.2 controller:=fs100 fake_execution:=true" >> ~/.bash_history
RUN echo "roslaunch sda5f_motion_plan demo_wavearms.launch fake_execution:=true" >> ~/.bash_history
RUN echo "roslaunch sda5f_motion_plan demo_pickplace.launch fake_execution:=true planning_space:=joint" >> ~/.bash_history
