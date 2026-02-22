from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from launch.substitutions import LaunchConfiguration
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
import os
def generate_launch_description():

    urdf_path = PathJoinSubstitution([
        FindPackageShare("r2_robot"),
        "urdf",
        "robot.urdf"
    ])
    rviz_config = PathJoinSubstitution([
        FindPackageShare("r2_robot"),
        "rviz",
        "r2_robot.rviz"
    ])

    channel_type =  LaunchConfiguration('channel_type', default='serial')
    serial_port = LaunchConfiguration('serial_port', default='/dev/ttyUSB0')
    serial_baudrate = LaunchConfiguration('serial_baudrate', default='115200')

    pkg_gazebo = get_package_share_directory('gazebo_ros')
    pkg_stage = get_package_share_directory('r2_robot')
    frame_id = LaunchConfiguration('frame_id', default='laser')
    inverted = LaunchConfiguration('inverted', default='false')
    angle_compensate = LaunchConfiguration('angle_compensate', default='true')
    scan_mode = LaunchConfiguration('scan_mode', default='Sensitivity')

    world = os.path.join(
        pkg_stage,
        'worlds',
        'arena.world'
    )

    robot_description = Command(["xacro ", urdf_path])
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': world}.items()
    )
    spawn_bot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'my_robot',
            '-x', '-1.4',
            '-y', '-5.5',
            '-z', '0.05',
            '-Y', '1.57'
        ],
        output='screen'
    )
    state_pub = Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            output="screen",
            parameters=[{"robot_description": robot_description,"use_sim_time":True}],
    )
    joint_pub = Node(
            package="joint_state_publisher_gui",
            executable="joint_state_publisher_gui",
            parameters=[{"use_sim_time": True}],
            output="screen",
    )
    rviz = Node(
            package="rviz2",
            executable="rviz2",
            arguments=["-d", rviz_config],
            parameters=[{"use_sim_time":True}],
            output="screen",
    )
    rplidar = Node(
            package='rplidar_ros',
            executable='rplidar_node',
            name='rplidar_node',
            parameters=[{'channel_type':channel_type,
                        'serial_port': serial_port,
                        'serial_baudrate': serial_baudrate,
                        'frame_id': frame_id,
                        'inverted': inverted,
                        'angle_compensate': angle_compensate}],
            output='screen')

    return LaunchDescription([
        # rplidar,  
        gazebo,
        state_pub,
        joint_pub,
        spawn_bot,
        rviz,
    ])
