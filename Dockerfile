FROM ros:noetic-ros-core-focal

# Set some environment variables for the GUI
ENV HOME=/root \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8 \
    LC_ALL=C.UTF-8

# Install cli tools
RUN set -ex; \
    apt update && apt install -y \
    python3-pip \
    screen \
    vim \
    nano \
    net-tools \
    iputils-ping \
    git \
    wget 


######################
#OCC :
#####################


RUN apt-get install -y wget git build-essential libgl1-mesa-dev libfreetype6-dev libglu1-mesa-dev libzmq3-dev libsqlite3-dev libicu-dev python3-dev libgl2ps-dev libfreeimage-dev libtbb-dev ninja-build bison autotools-dev automake libpcre3 libpcre3-dev tcl8.6 tcl8.6-dev tk8.6 tk8.6-dev libxmu-dev libxi-dev libopenblas-dev libboost-all-dev swig libxml2-dev cmake rapidjson-dev

RUN dpkg-reconfigure --frontend noninteractive tzdata


############################################################
# OCCT 7.5.3                                               #
# Download the official source package from git repository #
############################################################
WORKDIR /opt/build
RUN wget 'https://git.dev.opencascade.org/gitweb/?p=occt.git;a=snapshot;h=fecb042498514186bd37fa621cdcf09eb61899a3;sf=tgz' -O occt-fecb042.tar.gz
RUN tar -zxvf occt-fecb042.tar.gz >> extracted_occt753_files.txt
RUN mkdir occt-fecb042/build
WORKDIR /opt/build/occt-fecb042/build

RUN ls /usr/include
RUN cmake -G Ninja \
 -DINSTALL_DIR=/opt/build/occt753 \
 -DBUILD_RELEASE_DISABLE_EXCEPTIONS=OFF \
 ..

RUN ninja install

RUN echo "/opt/build/occt753/lib" >> /etc/ld.so.conf.d/occt.conf
RUN ldconfig

RUN ls /opt/build/occt753
RUN ls /opt/build/occt753/lib

#############
# pythonocc #
#############
WORKDIR /opt/build
RUN git clone https://github.com/tpaviot/pythonocc-core
WORKDIR /opt/build/pythonocc-core
#RUN git checkout 7.5.1
WORKDIR /opt/build/pythonocc-core/build

RUN cmake \
 -DOCE_INCLUDE_PATH=/opt/build/occt753/include/opencascade \
 -DOCE_LIB_PATH=/opt/build/occt753/lib \
 -DPYTHONOCC_BUILD_TYPE=Release \
 ..

RUN make -j3 && make install 

############
# svgwrite #
############
RUN pip install svgwrite


RUN pip install catkin_tools

RUN set -ex; \
    apt update && apt install -y \
    ros-noetic-urdfdom-py \
    ros-noetic-tf


WORKDIR /ros_ws/src



WORKDIR /ros_ws

WORKDIR /scripts_occ



# We source the ros_ws workspace as well when entering the container
#RUN cp /ros_entrypoint.sh /tmp_entrypoint.sh
#RUN (head -n -1 /ros_entrypoint.sh && echo 'source "/ros_ws/devel/setup.bash"' && tail -n 1 /ros_entrypoint.sh;) > /tmp_entrypoint.sh
#RUN mv /tmp_entrypoint.sh /ros_entrypoint.sh

# Add a file to help out sourcing the workspaces
#RUN echo "source \"/opt/ros/$ROS_DISTRO/setup.bash\"" >> /source_ws.sh
#RUN echo "source \"/ros_ws/devel/setup.bash\"" >> /source_ws.sh
