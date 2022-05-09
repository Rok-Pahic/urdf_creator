
#from OCC.Display.SimpleGui import init_display
from OCC.Display.WebGl import threejs_renderer
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs

from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Trsf, gp_Ax1, gp_Quaternion, gp_EulerSequence

from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_Transform
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism

from OCC.Core.GC import GC_MakeArcOfCircle

from math import pi
   
import argparse 

#

parser = argparse.ArgumentParser()

parser.add_argument('name', type=str)
parser.add_argument('type', type=str)
parser.add_argument('length', type=float)
parser.add_argument('dim1', type=float)
parser.add_argument('dim2', type=float, default=0)
parser.add_argument('--render', action='store_true')

args = parser.parse_args()
print(args)

object_type = args.type
object_length = args.length
object_wide = args.dim1
object_hight = args.dim2
render = args.render

if object_type=="celinder":
    object = BRepPrimAPI_MakeCylinder(object_wide, object_length)

    move1 = gp_Trsf()
    q_r = gp_Quaternion()
    q_r.SetEulerAngles(gp_EulerSequence(1),0,pi/2,0)
    move1.SetRotation(q_r)
    object = BRepBuilderAPI_Transform(object.Shape(), move1, False)

    move2 = gp_Trsf()
    move2.SetTranslation(gp_Vec(-object_length/2,0,0))
    object = BRepBuilderAPI_Transform(object.Shape(), move2, False)
 

elif object_type=="eliptic":

    eliptic_radius = object_hight/2
    pn1 = gp_Pnt(0, object_wide/2 -eliptic_radius, -eliptic_radius)
    pn2 = gp_Pnt(0,object_wide/2,0)
    pn3 = gp_Pnt(0, object_wide/2 -eliptic_radius, eliptic_radius)
    pn4 = gp_Pnt(0, -(object_wide/2 -eliptic_radius), -eliptic_radius)
    pn5= gp_Pnt(0, -object_wide/2,0)
    pn6 = gp_Pnt(0, -(object_wide/2 -eliptic_radius), eliptic_radius)


    points=[pn1, pn2, pn3]

    shape_wire = BRepBuilderAPI_MakeWire()

    edge = BRepBuilderAPI_MakeEdge(GC_MakeArcOfCircle(pn1,pn2,pn3).Value()).Edge()
    shape_wire.Add(edge)
    edge = BRepBuilderAPI_MakeEdge(pn1,pn4).Edge()
    shape_wire.Add(edge)
    edge = BRepBuilderAPI_MakeEdge(pn6,pn3).Edge()
    shape_wire.Add(edge)
    edge = BRepBuilderAPI_MakeEdge(GC_MakeArcOfCircle(pn4,pn5,pn6).Value()).Edge()
    shape_wire.Add(edge)

    face = BRepBuilderAPI_MakeFace(shape_wire.Wire())

    object = BRepPrimAPI_MakePrism(face.Face(), gp_Vec(gp_Pnt(-object_length/2, 0.0, 0.0 ), gp_Pnt(object_length/2, 0.0, 0.0 )))


    move2 = gp_Trsf()
    move2.SetTranslation(gp_Vec(-object_length/2,0,0))
    object = BRepBuilderAPI_Transform(object.Shape(), move2, False)

else:
    print("Non defined shape type!")



if render:
    my_renderer = threejs_renderer.ThreejsRenderer()
    #my_renderer.DisplayShape(object)
    my_renderer.DisplayShape(object.Shape())
    my_renderer.render()
else:
    step_writer = STEPControl_Writer()
    step_writer.Transfer(object.Shape(),STEPControl_AsIs)
    step_writer.Write("test.stp")
