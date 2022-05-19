#! /bin/sh

echo Chose part name:
read part_name
package_tail="_rospkg"
package_name="${part_name}${package_tail}"
echo $package_name
cd /ros_ws/src
catkin_create_pkg $package_name
cd $package_name
mkdir urdf
