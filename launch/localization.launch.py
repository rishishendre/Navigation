from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():

    pkg_share = FindPackageShare('r2_robot')

    # default files inside your package
    default_map = PathJoinSubstitution([pkg_share, 'maps', 'mymap.yaml'])
    default_params = PathJoinSubstitution([pkg_share, 'config', 'nav2_param.yaml'])

    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')

    # arguments so you can override from terminal
    declare_map = DeclareLaunchArgument(
        'map',
        default_value=default_map,
        description='Map yaml file'
    )

    declare_params = DeclareLaunchArgument(
        'params_file',
        default_value=default_params,
        description='Nav2 parameters file'
    )

    declare_sim = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true'
    )

    # LOCALIZATION
    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('nav2_bringup'),
                'launch',
                'bringup_launch.py'
            ])
        ),
        launch_arguments={
            'map': map_yaml,
            'use_sim_time': use_sim_time,
            'params_file': params_file
        }.items()
    )

    # NAVIGATION
    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('nav2_bringup'),
                'launch',
                'navigation_launch.py'
            ])
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'params_file': params_file
        }.items()
    )

    return LaunchDescription([
        declare_map,
        declare_params,
        declare_sim,
        localization,
        navigation
    ])
