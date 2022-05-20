#! /bin/sh
ros_ws_path=$2
part_name=$1
package_tail="_rospkg"
package_name="${part_name}${package_tail}"
echo $package_name
cd $ros_ws_path
catkin_create_pkg $package_name
cd $package_name
mkdir geometry
