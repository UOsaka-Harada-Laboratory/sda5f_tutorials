cmake_minimum_required(VERSION 3.0.2)
project(sda5f_motion_plan)

find_package(catkin REQUIRED COMPONENTS
    rospy
    std_msgs
    geometry_msgs
    industrial_msgs
    tf
    moveit_core
    moveit_ros_planning_interface
    message_generation
)

add_message_files(
    FILES
    OnRobotRGInput.msg
    OnRobotVGInput.msg
) 

add_service_files(
    FILES
    SetCommand.srv
)

generate_messages(
    DEPENDENCIES
)

catkin_package(
    CATKIN_DEPENDS
        rospy
        std_msgs
        geometry_msgs
        industrial_msgs
        tf
        moveit_core
        moveit_ros_planning_interface
)

include_directories(
    ${catkin_INCLUDE_DIRS}
)

catkin_install_python(
    PROGRAMS
        scripts/demo_pickplace_joint_fake.py
        scripts/demo_pickplace_joint.py
        scripts/demo_wavearms.py
        scripts/demo_wavearms_fake.py
        scripts/object_tf_publisher.py
    DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})
