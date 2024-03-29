
from itertools import count
from Asembly_import import read_step_file_asembly
from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Core.BRep import  BRep_Tool_Pnt,BRep_TEdge
from OCC.Core.gp import  gp_Vec, gp_Quaternion, gp_Pnt , gp_Trsf, gp_Ax1
from OCC.Core.TopLoc import TopLoc_Location
from os import path

#from OCC.Core.TopoDS import
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeWire, BRepBuilderAPI_Transform

from OCC.Core.StlAPI import StlAPI_Writer

from OCC.Core.TopoDS import TopoDS_Compound, TopoDS_Solid, TopoDS_Shell

#parts_data = read_step_file_asembly('test ijs part.STEP')
#parts_data = read_step_file_asembly('ijs 3.STEP')
#parts_data = read_step_file_asembly('reconcycle.stp')

#parts_data = read_step_file_asembly('test ijs 2dof.STEP')
#parts_data = read_step_file_asembly('StorageV2.step')
parts_data = read_step_file_asembly('Cutter v7.step')

import os
import numpy as np
import copy
#from scipy.spatial.transform import Rotation as R

#import tf2_py as tf

from tf.transformations import euler_from_quaternion, quaternion_from_euler

#import tf2_ros
#import tf2
from urdf_parser_py import urdf
from urdf_parser_py.urdf import URDF, Link, Visual, Cylinder, Pose, Joint, Inertial, Inertia, JointLimit, Collision, Mesh, Material



# create links


segments_data={}
#najdi vse joint_base in si zapomni njihove lokacije za iskanje parov z joint_add
#definiraj si hiarhijo znotraj skeleta

robot_joints =[]
robot_parts = []
robot_links = []
robot_links_vis_data = []

def changePos2M(segment_location):

    return [segment_location.TranslationPart().X() / 1000, segment_location.TranslationPart().Y() / 1000, segment_location.TranslationPart().Z() / 1000]

def toEuler(segment_location):


    q = np.array([segment_location.GetRotation().X(), segment_location.GetRotation().Y(), segment_location.GetRotation().Z(), segment_location.GetRotation().W()])
    return list(euler_from_quaternion(q))

    
def calculateTfToRoot(joint, joint_list):

    parent_name = joint['parent']

    global_this_tf = joint['location']
    local_tf = gp_Trsf()#copy.deepcopy(global_this_tf)
    found = False
    for other_joint in joint_list:

        if other_joint['child'] == parent_name:
            global_other_tf = other_joint['location']
            local_tf = global_other_tf.Inverted().Multiplied(global_this_tf) 
            found = True
            break

    if found == False: #is to root joint  
            
        local_tf.SetTranslation(gp_Vec(0,0,0)) 
        local_tf.SetRotation(gp_Quaternion(0,0,0,1))

        #local_tf = global_this_tf
    
    return local_tf

avalibel_joint_types = ["fixed","revolute", "prismatic"]


for part in parts_data:
    part_data = parts_data[part]

    if len(part_data)==4: #type(part) == TopoDS_Solid or type(part) == TopoDS_Compound or type(part) == TopoDS_Shell: #check id solid or compound
        segment_name, segment_color, segment_hierarchy, segment_trans = part_data

        print(segment_hierarchy)
        print(segment_name)

        segment_location = part.Location().Transformation()


        segment_position = changePos2M(segment_location)
        segment_q_orientation = [segment_location.GetRotation().X(), segment_location.GetRotation().Y(), segment_location.GetRotation().Z(), segment_location.GetRotation().W()]
        print(segment_location)
        #Parse joints data
        if segment_hierarchy[1] == "URDF" or segment_hierarchy[1] == "urdf": #check for urdf
            joint_name = segment_hierarchy[2] 
            if joint_name.find("joint_")==0:

                connection_name = joint_name[6:]
                connection_id_string = "_to_"
                ind = connection_name.find(connection_id_string)
                parent_name = connection_name[0:ind]
                connection_name = connection_name[len(parent_name)+len(connection_id_string):]
                ind = connection_name.find("_")
                child_name = connection_name[0:ind]

                if child_name == "": #chec if this is root link
                    root_link_name = parent_name
                    child_name = parent_name #to enable moving everithing to this frame
                    parent_name = "" #"root joint doesnt have parent"

  
                joint_data = {}
                joint_data["name"] = parent_name + "_" + child_name
                
                for test_type in avalibel_joint_types: #iterate trough avalibel type and set correct one
                    if segment_name.find(test_type)==0:
                        joint_data["type"] = test_type
                        break

                joint_data["parent"] = parent_name
                joint_data["child"] = child_name
                joint_data["position"] = segment_position
                joint_data["rotation"] = segment_q_orientation
                joint_data["location"] = segment_location
                robot_joints.append(joint_data)

                #DEFINE LINKS
                #Test child links and add
                if not child_name in robot_links:
                    robot_links.append(child_name)

                #Create links
                if parent_name !="": #not epty root mark
                    if not parent_name in robot_links:
                        robot_links.append(parent_name)




            else:

                print("PROBLEM: Not correct naming of joints in URDF asembly")
                print(joint_name)


        else:

            if type(part) == TopoDS_Solid:#== TopoDS_Compound : #

                if False:            
                    if not(segment_hierarchy[1] in robot_links) and not(segment_hierarchy[1] in robot_links_vis_data): #make list of links at top hiarchie
                    #segments_data={segment_hierarchy[-1]:{segment_name:segment_location}}        
                        robot_links_vis_data.append(segment_hierarchy[1])

                        #zloži elemente v dictionary po hiarhiji
                        if segment_hierarchy[-1] in segments_data:
                            segments_data[segment_hierarchy[-1]].update({segment_name: part})
                        else:
                            segments_data.update({segment_hierarchy[-1]:{segment_name:part}})
                robot_part = {}
                robot_part["name"] = segment_name
                robot_part["location"] = segment_location
                robot_part["hierarchy"] = segment_hierarchy
                robot_part["part"] = part
                robot_part["color"] = [segment_color.Red(),segment_color.Green(),segment_color.Blue()]
                robot_parts.append(robot_part)

            if type(part) == TopoDS_Shell:
                robot_part = {}
                robot_part["name"] = segment_name
                robot_part["location"] = segment_location
                robot_part["hierarchy"] = segment_hierarchy
                robot_part["part"] = part
                robot_part["color"] = [segment_color.Red(),segment_color.Green(),segment_color.Blue()]
                robot_parts.append(robot_part)


    else:
        segment_name, segment_color = parts_data[part]


#asembly = TopoDS_Compound()
#TopoDS_Bilder
#for part in robot_parts:
    #asembly
    
    


#PREPARE TRANSFORM MATRIX

for joint in robot_joints:

    tf = calculateTfToRoot(joint, robot_joints)

    joint["local_tf"] = tf

    pass


#CREATE STLS

package_path = "/ros_ws/src/test_rospkg"


#convert to stls
from OCC.Extend.DataExchange import write_stl_file

from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh


#stl_output_dir = os.path.abspath(os.path.join(".","models/"))


stl_output_dir = package_path + "/meshes" #"os.path.abspath("/ros_ws/src/test_rospkg/meshes")
output_files = []
file_names = []

test_count = 0
max_parts = 2000
#root_link_name ="Base"
colors_values = []
colors_names = []
color_counter = 0
materials = []


link_meshes = {}

for name in robot_links: #preapre empty matrixes for link meshes

    link_meshes[name] = []

for part in robot_parts:

    print(part)
    #file_name = part['hierarchy'][-1]+"-"+part["name"]+".stl"
    if test_count>max_parts:
        break
    test_count = test_count + 1


    made_name = part["name"]
    #for h_name in part['hierarchy']:
        #made_name = h_name + made_name
    name_counter = 0
    file_name = made_name + str(name_counter)
   
    while file_name in file_names:

        name_counter = name_counter + 1
        file_name = made_name + str(name_counter)
        

    file_names.append(file_name)    

    file_name = file_name + ".stl"

    output_file = os.path.join(stl_output_dir,file_name)
    #stl_writer = StlAPI_Writer()
    #stl_writer.SetASCIIMode(True)
    #mesh = BRepMesh_IncrementalMesh( part["part"], 0.1, False, 0.1, True
    #)       


    #mesh = BRepMesh_IncrementalMesh(my_box, 0.1)
    #mesh.Perform()
    trfs = gp_Trsf()
    trfs.SetScale(gp_Pnt(),0.001)
    scaled_part = BRepBuilderAPI_Transform(part['part'], trfs).Shape()
    
    
    write_stl_file(scaled_part, output_file )
    output_files.append(file_name)

    #PREPARE new color

    if part["color"] in colors_values:
        color_name = colors_names[colors_values.index(part["color"])]

        
    else:
        colors_values.append(part["color"])
        
        color_name = "color"+str(color_counter)
        colors_names.append(color_name)
        materials.append(Material(name = color_name, color = urdf.Color(part["color"]+[1]) ))
        color_counter = color_counter + 1

    part["material_name"] = color_name

    #FIND_LINK_name:
    current_name = part["name"] 

    if "link_" in current_name: #search for link definition in part name
        current_name = current_name[5:]
        current_name = current_name[0:current_name.find("_")]
    else: #search for link defition in hiearchy
        for parent_name in part["hierarchy"]:
            if "link_" in parent_name:
                current_name = parent_name[5:]
                current_name = current_name[0:current_name.find("_")]
                break
            else:
                current_name = root_link_name

    if current_name in robot_links:

        link_meshes[current_name].append({"mesh_name":file_name,"mesh_material":color_name,"color_value":part["color"]})

    else:
        print("error: no link name")



# ROBOT META DATA

robot=URDF()
#robot.materials = materials

robot.name='fifi'

robot.version='1.0'


#CREATE ROBOT JOINTS

for joint in robot_joints:

    if joint["parent"]!="":#if root link joint dont add it to the joints
        joint_limit=JointLimit(effort=1000, lower=-1.548, upper=1.548, velocity=0.5)
        or_j = toEuler(joint["local_tf"])
        pos_j = changePos2M(joint["local_tf"])
        
        #pos_j = joint["position"]
        Pos1 = Pose(xyz=pos_j, rpy=or_j)#'zyx'
        #Pos1 = Pose(xyz=[0,0,0], rpy=[0,0,0,])#'zyx'
        new_joint = Joint( name= joint["name"], parent=joint["parent"], child=joint["child"], joint_type=joint["type"],
                            axis=[0, 0, 1], origin=Pos1,
                            limit=joint_limit, dynamics=None, safety_controller=None,
                            calibration=None, mimic=None)



        robot.add_joint(new_joint)
    else:
        root_location_in_step = joint["location"]



#robot.add_material(Mat1)

#CREATE ROBOT LINKS
relative_mesh_path = "meshes/"
stl_urdf_root ="package://test_rospkg/"



if True:

    counter = 0
    already_defined_colors = []
    for link_name in robot_links:

        #if link_name != root_link_name: #this is overjuped because we add it leater
            #search for coresponding joint
        urdf_link = Link(name = link_name, visual = None, inertial = None, collision = None)#, origin = link_pose

        #add visuals

        for mesh in link_meshes[link_name]:
            meshpath = stl_urdf_root + relative_mesh_path + mesh["mesh_name"]

            #ADD MATERIALS
            Mat1 = Material(name = mesh["mesh_material"], color = urdf.Color(mesh["color_value"]+[1]))
            #if mesh["mesh_material"] in already_defined_colors: #check if you have already somwhere defined this color if not define it
                #Mat1 = Material(name = mesh["mesh_material"] )
            #else:
                #already_defined_colors.append(mesh["mesh_material"])
                #Mat1 = Material(name = mesh["mesh_material"], color = urdf.Color(mesh["color_value"]+[1]))

            #translation = changePos2M(tf)
            if link_name == root_link_name:
                mesh_location = root_location_in_step
            else:
                for joint in robot_joints:
                    if link_name == joint["child"]:
                        mesh_location = joint["location"]
                        break

            translation  = changePos2M(mesh_location.Inverted())# [0,0,0]
            #or_part = toEuler(tf)
            or_part = toEuler(mesh_location.Inverted())#0,0,0]

            Mesh_to_joint_pose = Pose(xyz=translation,rpy=or_part)#'zyx'


            Vis1 = Visual(geometry=Mesh(filename= meshpath), material=Mat1, origin=Mesh_to_joint_pose, name=None)

            #Vis1 = Visual(geometry=Cylinder(radius=0.005, length=0.5), material=None, origin=Pos1, name=None)
            urdf_link.add_aggregate('visual', Vis1)
   

        robot.add_link(urdf_link)







#meshes = []
if False:
    counter = 0
    first_time_color_definition = np.zeros(len(colors_names))
    for mesh in output_files:
        part  = robot_parts[counter]
        meshpath = stl_urdf_root + relative_mesh_path + mesh

        #prepare_material
        color_index = colors_values.index(robot_parts[counter]["color"])
        if first_time_color_definition[color_index] == 0:
            first_time_color_definition[color_index] = 1
            Mat1 = materials[color_index]
        else:
            Mat1 = Material(name = colors_names[color_index] )

        tf = part["location"]

        #translation = changePos2M(tf)
        translation  = changePos2M(root_location_in_step.Inverted())# [0,0,0]
        #or_part = toEuler(tf)
        or_part = toEuler(root_location_in_step.Inverted())#0,0,0]

        Pos1 = Pose(xyz=translation,rpy=or_part)#'zyx'
                
        Vis1 = Visual(geometry=Mesh(filename= meshpath),material=Mat1, origin=Pos1, name=None)


        urdf_link.add_aggregate('visual', Vis1)
        counter = counter + 1



    robot.add_link(urdf_link)

#SAVE URDF


urdf_path = package_path +"/urdf/part1.urdf"

file_handle = open(urdf_path,"w")
#print(robot)


robot.gazebos = ['control']


file_handle.write(robot.to_xml_string())
file_handle.close()
#print(robot.to_xml_string())
print('FINISH')









print("end")






if False:
    from OCC.Core.TopExp import TopExp_Explorer
    ex = TopExp_Explorer()
    ex.Init(part["part"],1)
    while ex.More():
        ex.Next()

    t = TopologyExplorer(part["part"])
    t.edges()
    for o in t.edges(): #t.solids():
        print(o)

    mesh.myParameters
    mesh.GetStatusFlags()
    part["part"].NbChildren() 


    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox

    my_box = BRepPrimAPI_MakeBox(10.,20.,30.).Shape()




    from OCC.Core.STEPControl import STEPControl_Reader
    step_reader = STEPControl_Reader()
    step_reader.ReadFile( 'test ijs part.STEP' )
    step_reader.TransferRoot()
    myshape = step_reader.Shape()
    print("File readed")

    stl_writer = StlAPI_Writer()
    stl_writer.SetASCIIMode(True)
    stl_writer.Write(myshape, output_file)
    print(stl_writer.Write(myshape, output_file))

    mesh = BRepMesh_IncrementalMesh(myshape, 0.0001)
    writer = StlAPI_Writer()
    writer.Write(mesh.Shape(), output_file)

    print("Written")



    for u in data:

        segment_name, segment_color, segment_hierarchy, segment_trans= data[u]
        print('CHOSEN bone:')
        print(segment_name)
        if segment_name.find('bone') >= 0:

            from OCC.Core.AIS import AIS_Shape
            #ustvari novi link
            Pos2 = Pose(xyz=[0, 0, 0], rpy=[0, 0, 0])
            Link1 = Link(name=segment_hierarchy[-1], visual=None, inertial=None, collision=None, origin=Pos2)

            segment_location = u.Location().Transformation()#
            print('segment')
            print(segment_location.TranslationPart().Y())


            # t.number_of_vertices()
            # t.number_of_wires()
            # t.number_of_edges()
            #


            check_joint_add=False
            #check id add joint then get bone in its cordinate sistem
            for u2 in data:
                u2name,u2color,u2hiarhi,u2trans= data[u2]

                print('SEARCH:')
                print(u2name)
                if u2hiarhi==segment_hierarchy and u2name=='joint_add':
                    loc = u2trans[-1].Inverted()
                    #joint_obj=u2
                    check_joint_add=True

            if check_joint_add:
                loc=loc.Multiplied(segment_trans[-1])
                #origin=joint_obj.Location()
            else:
                loc = TopLoc_Location()
                for l in segment_trans:
                    #print("    take loc       :", l)
                    loc = loc.Multiplied(l)

                #origin=u.Location()
            #topo=u.copy()
            #topo.Location(loc)

            t = TopologyExplorer(u, ignore_orientation=True)
            for z in t.edges():
                # Wire_bilder.Add(z)
                # print(z.Location().Transformation().TranslationPart().Y())
                # get edge to segment cordinate sistem
                #z.Location(z.Location().Divided(origin))
                z.Location(loc)
                ex = []
                ey = []
                ez = []
                for ui in t.vertices_from_edge(z):
                    # print(ui.Location().Transformation().TranslationPart().Coord())
                    ver_loc = BRep_Tool_Pnt(ui)
                    ex.append(ver_loc.X()/1000)
                    ey.append(ver_loc.Y()/1000)
                    ez.append(ver_loc.Z()/1000)


                    #print(ver_loc.Coord())



                # t1=TopologyExplorer(z)
                # t1.number_of_vertices()
                # t1.number_of_edges()

                # wire_relative_position = z.Location().Divided(
                #     u.Location()).Transformation()
                #z.Location().Transformation().TranslationPart().X()

                # t.number_of_compounds()
                # t.number_of_comp_solids()
                #
                # u.ShapeType()
                #izracunaj dolzine
                dx = (ex[0] - ex[1])
                dy = (ey[0] - ey[1])
                dz = (ez[0] - ez[1])
                #izracunaj dolzino valja
                L=(dx**2+dy**2+dz**2)**(1/2)
                #rotacijo glede na Z os!
                segment_rotation=gp_Quaternion(gp_Vec(0,0,1),gp_Vec(dx,dy,dz))
                #segment_rotation = R.from_quat([segment_location.GetRotation().X(),segment_location.GetRotation().Y(),segment_location.GetRotation().Z(),segment_location.GetRotation().W()])
                segment_rotation = R.from_quat([segment_rotation.X(),segment_rotation.Y(),segment_rotation.Z(),segment_rotation.W()])
                #povprecne pozicije in rotacija
                Pos1 = Pose(xyz=[(ex[0] + ex[1]) / 2, (ey[0] + ey[1])/ 2, (ez[0] + ez[1])/ 2],rpy=segment_rotation.as_euler('xyz'))#'zyx'
                #Pos1 = Pose(xyz=[loc_edge.TranslationPart().X()/1000, loc_edge.TranslationPart().Y()/1000,loc_edge.TranslationPart().Z()/1000], rpy=segment_rotation.as_euler('zyx'))

                Vis1 = Visual(geometry=Cylinder(radius=0.005, length=L), material=None, origin=Pos1, name=None)

                Link1.add_aggregate('visual', Vis1)
                Link1.get_aggregate_list('visual')

            link_colision=Collision(geometry=Cylinder(radius=0.005, length=L),origin=Pos1)  
            
            Link1.add_aggregate('collision', link_colision)
            Link1.get_aggregate_list('collision') 
            link_inertia=Inertia(ixx=1,ixy=0,ixz=0,iyy=1,iyz=0,izz=1)
            link_mass=1
            Inert=Inertial(mass=link_mass,inertia=link_inertia,origin=Pos1)    
            Link1.inertial=Inert
            robot.add_link(Link1)


    i=0
    ## CREATE JOINTS

    for u in data:
        segment_name, segment_color, segment_hierarchy,segment_trans = data[u]

        # Poglej za joint_add

        if segment_name == 'joint_add':

            segment_location= u.Location().Transformation()
            joint_position=[segment_location.TranslationPart().X() / 1000
                , segment_location.TranslationPart().Y() / 1000
                , segment_location.TranslationPart().Z() / 1000]
            # Poisci na keri baze pride

            for j in range(0,len(joint_base_data)):

                if [round(num,6) for num in joint_position]==[round(num,6) for num in joint_base_data[j][0]]:



                    #if parent link hase own add clculate this joint base position in its reference frame
                    if 'joint_add' in segments_data[joint_base_data[j][1][-1]]:

                        loc = TopLoc_Location()
                        for l in reversed(data[segments_data[joint_base_data[j][1][-1]]['joint_add']][-1]):
                            loc = loc.Multiplied(l.Inverted())
                        for l in segment_trans:
                            # print("    take loc       :", l)
                            loc = loc.Multiplied(l)
                        #u.Location().Transformation().TranslationPart().Coord()
                        #segments_data[joint_base_data[j][1][-1]]['joint_add'].Location().Transformation().TranslationPart().Coord()

                        joint_relative_position=loc.Transformation()
                        #joint_relative_position=u.Location().Divided(segments_data[joint_base_data[j][1][-1]]['joint_add'].Location()).Transformation()

                        joint_relative_trans=[joint_relative_position.TranslationPart().X() / 1000
                        ,joint_relative_position.TranslationPart().Y() / 1000
                        ,joint_relative_position.TranslationPart().Z() / 1000]
                        #degbug segments_data[joint_base_data[j][1][-1]]['joint_add'].Location().Transformation().TranslationPart().X()
                        segment_rotation = R.from_quat([joint_relative_position.GetRotation().X(), joint_relative_position.GetRotation().Y(),
                                                joint_relative_position.GetRotation().Z(), joint_relative_position.GetRotation().W()])

                        Pos1 = Pose(xyz=joint_relative_trans, rpy=segment_rotation.as_euler('xyz'))#[0 ,0 ,0])

                    else:
                        segment_rotation = R.from_quat(
                            [segment_location.GetRotation().X(), segment_location.GetRotation().Y(),
                            segment_location.GetRotation().Z(), segment_location.GetRotation().W()])

                        Pos1 = Pose(xyz= joint_position, rpy=segment_rotation.as_euler('xyz'))
                    Pos2 = Pose(xyz=[0,0,0], rpy=[0,0,0])
                    Vis1 = Visual(geometry=Cylinder(radius=0.05, length=0.2), material=None, origin=Pos1, name=None)


                    joint_limit=JointLimit(effort=1000, lower=0.0, upper=0.548, velocity=0.5)
                    Joint1= Joint( name='Joint'+str(segment_hierarchy[-1])+str(joint_base_data[j][1][-1]), parent=joint_base_data[j][1][-1], child=segment_hierarchy[-1], joint_type='revolute',
                            axis=[0, 0, 1], origin=Pos1,
                            limit=joint_limit, dynamics=None, safety_controller=None,
                            calibration=None, mimic=None)
                    i=i+1
                    robot.add_joint(Joint1)

                    # #dodaj vizualizacijo med sklepi
                    #
                    # #sredina celindra
                    # JV_position=[x/2 for x in joint_position]
                    # Pos_jv=Pose(xyz= JV_position, rpy=segment_rotation.as_euler('zyx'))
                    #
                    # Vis1 = Visual(geometry=Cylinder(radius=0.02, length=0.2), material=None, origin=Pos_jv, name=None)
                    #
                    # Link1 = Link(name=segment_hierarchy[-1], visual=None, inertial=None, collision=None,
                    #              origin=Pos2)
                    # Link1.add_aggregate('visual', Vis1)
                    # Link1.get_aggregate_list('visual')
                    # robot.add_link(Link1)

    #Link1.visual=Vis1





    #robot1= URDF.from_xml_file('pi_robot.xml')




    # robot.to_xml()
    #
    # robot.to_xml_string()
    # robot1.to_xml_string()

    #

