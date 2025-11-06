# launch/all_in_one_launch.py

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration

def generate_launch_description():

    # 다른 패키지들의 경로
    livox_ros_driver2_pkg = get_package_share_directory('livox_ros_driver2')
    fast_lio_pkg = get_package_share_directory('fast_lio')
    slam_toolbox_pkg = get_package_share_directory('slam_toolbox')
    pointcloud_to_laserscan_pkg = get_package_share_directory('pointcloud_to_laserscan')
    go2w_description_pkg = get_package_share_directory('go2w_description')
    # nav2_bringup_pkg = get_package_share_directory('nav2_bringup')
    orbbec_camera_pkg = get_package_share_directory('orbbec_camera')
    # 현재 패키지('go2w_bringup')의 경로를 가져옵니다.
    go2w_bringup_pkg = get_package_share_directory('go2w_bringup')

    # go2w_bringup 패키지 내의 config 파일 경로를 지정합니다. (가장 중요한 수정사항)
    fast_lio_config = os.path.join(go2w_bringup_pkg, 'config', 'mid360.yaml')
    slam_toolbox_config = os.path.join(go2w_bringup_pkg, 'config', 'localization_params_online_async.yaml')
    # nav2_bringup_config = os.path.join(go2w_bringup_pkg, 'config', 'nav2_params.yaml')
    
    default_rviz_config_path = os.path.join(go2w_bringup_pkg, 'config', 'default.rviz')
    rviz_cfg = LaunchConfiguration('rviz_cfg')
    declare_rviz_config_file_cmd = DeclareLaunchArgument(
        'rviz_cfg', default_value=default_rviz_config_path,
        description='Full path to the RVIZ config file to use'
    )

    return LaunchDescription([
        declare_rviz_config_file_cmd,
        # 1. Livox LiDAR 드라이버 실행
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(livox_ros_driver2_pkg, 'launch_ROS2', 'msg_MID360_launch.py')
            )
        ),

        # 2. Fast-LIO 실행
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(fast_lio_pkg, 'launch', 'mapping.launch.py')
            ),
            launch_arguments={'config_file': fast_lio_config, 'rviz':'false'}.items()
        ),

        # 3. slam_toolbox 실행
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(slam_toolbox_pkg, 'launch', 'online_sync_launch.py')
            ),
            launch_arguments={'params_file': slam_toolbox_config}.items()
        ),

        # 4. pointcloud_to_laserscan 실행
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pointcloud_to_laserscan_pkg, 'launch', 'sample_pointcloud_to_laserscan_launch.py')
            )
        ),

        # 5. go2w 로봇 모델 로드
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(go2w_description_pkg, 'launch', 'load_go2w.launch.py')
            ),
            launch_arguments={'use_jsp': 'jsp', 'use_rviz': 'false'}.items()
        ),

        # 6. go2w 키보드 컨트롤러 실행
        Node(
            package='go2w_keyboard',
            executable='sport_controller',
            name='sport_controller',
            output='screen'
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(orbbec_camera_pkg, 'launch', 'gemini_330_series.launch.py')
            )
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            output="screen",
            arguments=["-d", rviz_cfg],
        ),
    ])