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

ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"

RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh 



RUN conda --version


RUN pip install catkin_tools


WORKDIR /ros_ws/src

WORKDIR /ros_ws

WORKDIR /scripts_occ

RUN conda create --name=pyoccenv python=3.7
RUN conda init bash

#RUN bash -c "source ${HOME}/.bashrc"
#SHELL ["/bin/bash", "-c"]
#RUN source ~/miniconda3/etc/profile.d/conda.sh
#RUN conda activate pyoccenv
RUN conda install -n pyoccenv -c conda-forge pythonocc-core=7.5.1 occt=7.5.1

# We source the ros_ws workspace as well when entering the container
#RUN cp /ros_entrypoint.sh /tmp_entrypoint.sh
#RUN (head -n -1 /ros_entrypoint.sh && echo 'source "/ros_ws/devel/setup.bash"' && tail -n 1 /ros_entrypoint.sh;) > /tmp_entrypoint.sh
#RUN mv /tmp_entrypoint.sh /ros_entrypoint.sh

# Add a file to help out sourcing the workspaces
#RUN echo "source \"/opt/ros/$ROS_DISTRO/setup.bash\"" >> /source_ws.sh
#RUN echo "source \"/ros_ws/devel/setup.bash\"" >> /source_ws.sh
