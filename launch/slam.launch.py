from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from launch.substitutions import LaunchConfiguration
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution

def generate_launch_description():
    return LaunchDescription([
        Node(
            package="slam_toolbox",
            executable="async_slam_toolbox_node", 
            name="slam_toolbox",
            output="screen",
            parameters=[{
                "use_sim_time": True,
                "base_frame": "base_footprint",
                "odom_frame": "odom",
                "map_frame": "map",
                "scan_topic": "/scan",
                "publish_map": True,
                "map_qos_transient_local": True
                }],
            ),
            # Node(
            # package='rf2o_laser_odometry',
            # executable='rf2o_laser_odometry_node',
            # name='rf2o_laser_odometry',
            # output='screen',
            # parameters=[{
            #     "laser_scan_topic" : "/scan",
            #     "odom_topic" : "/odom",
            #     "publish_tf" : True,
            #     "base_frame_id" : "base_footprint",
            #     "odom_frame_id" : "odom",
            #     "init_pose_from_topic" : "",
            #     "freq" : 10.0}],
            # ),
            # Node(
            # package="tf2_ros",
            # executable="static_transform_publisher",
            # arguments=["0", "0", "0", "0", "0", "0", "odom", "base_footprint"],
            # output="screen"
            # ),

            # Node(
            # package='r2_robot',
            # executable='send_arduino',
            # name='send_arduino_node',
            # output='screen'
            # )  
    ])
