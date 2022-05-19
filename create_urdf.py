from Asembly_import import read_step_file_asembly


from urdf_parser_py import urdf
from urdf_parser_py.urdf import URDF, Link, Visual, Cylinder, Pose, Joint, Inertial, Inertia, JointLimit, Collision

data=read_step_file_asembly('/home/rok/Documents/Python-projects/urdf_creator/test/skelet_DP.STEP')