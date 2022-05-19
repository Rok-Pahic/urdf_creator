from Asembly_import import read_step_file_asembly
from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Core.BRep import  BRep_Tool_Pnt,BRep_TEdge
from OCC.Core.gp import  gp_Vec,gp_Quaternion, gp
from OCC.Core.TopLoc import TopLoc_Location
from os import path

#from OCC.Core.TopoDS import
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeWire
#data=read_step_file_asembly('D:\modeling\skelet.STEP')

#root_path='D:\modeling\Double_pendulum'

#data=read_step_file_asembly('D:\modeling\Double_pendulum\Body_CAD\Skelet\skelet_DP.STEP')

#data=read_step_file_asembly('D:\modeling\Double_pendulum\Body_CAD\Whole_Body_DP.STEP')

data=read_step_file_asembly('/home/rok/Documents/Python-projects/urdf_creator/test/skelet_DP.STEP')

for u in data:
    ee,ww,h,hir_trans=data[u]
    print(ee)
    print(u.Location().Transformation().TranslationPart().Coord())




from scipy.spatial.transform import Rotation as R


from urdf_parser_py import urdf
from urdf_parser_py.urdf import URDF, Link, Visual, Cylinder, Pose, Joint, Inertial, Inertia, JointLimit, Collision


# ROBOT META DATA

robot=URDF()
robot.name='fifi'
robot.version='1.1'

# create links


segments_data={}
#najdi vse joint_base in si zapomni njihove lokacije za iskanje parov z joint_add
#definiraj si hiarhijo znotraj skeleta
joint_base_data=[]
for u in data:
    segment_name, segment_color, segment_hierarchy, segment_trans= data[u]
    segment_location = u.Location().Transformation()
    segment_location =[segment_location.TranslationPart().X() / 1000, segment_location.TranslationPart().Y() / 1000, segment_location.TranslationPart().Z() / 1000]
    #segments_data={segment_hierarchy[-1]:{segment_name:segment_location}}

    #zloži elemente v dictionary po hiarhiji
    if segment_hierarchy[-1] in segments_data:
        segments_data[segment_hierarchy[-1]].update({segment_name: u})
    else  :
        segments_data.update({segment_hierarchy[-1]:{segment_name:u}})

    if segment_name== 'joint_base':
        joint_base_data.append([segment_location ,segment_hierarchy])



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
file_handle = open("robot.xml","w")
#print(robot)


robot.gazebos=['control']

file_handle.write(robot.to_xml_string())

print('FINISH')
