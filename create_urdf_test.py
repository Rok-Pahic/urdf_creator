from Asembly_import import read_step_file_asembly



from OCC.Core.STEPControl import STEPControl_Reader


from OCC.Core.TopoDS import TopoDS_Iterator


from urdf_parser_py import urdf
from urdf_parser_py.urdf import URDF, Link, Visual, Cylinder, Pose, Joint, Inertial, Inertia, JointLimit, Collision

step_reader = STEPControl_Reader()
step_reader.ReadFile('test ijs.STEP')
#step_reader.ReadFile('TEst1 v2.step')
nv_steps= step_reader.NbRootsForTransfer()
for i in range(1,nv_steps+1):
    #print(i)
    step_reader.TransferRoot(1)
    print("break")
    #print(step_reader.NbRootsForTransfer())
    print(step_reader.NbShapes())
    for j in range(1,step_reader.NbShapes()+1):
    
        myshape = step_reader.Shape()
        
        print(myshape.NbChildren())
        it = TopoDS_Iterator(myshape)
        while it.More():
            test = it.Value()
            print(it.Value())
            it.Next()


myshape = step_reader.Shape()
myshape.NbChildren()




step_reader = STEPControl_Reader()
step_reader.ReadFile('test ijs part.STEP')
step_reader.TransferRoot(1)

print(step_reader.NbShapes())

myshape = step_reader.OneShape()
print(myshape)
print(myshape.NbChildren())









step_strocture=read_step_file_asembly('test ijs part.STEP')

for u in step_strocture:
    ee,ww,h,hir_trans=step_strocture[u]
    print(ee)
    print(u.Location().Transformation().TranslationPart().Coord())

it = TopoDS_Iterator(myshape)
while it.More():
    test = it.Value()
    print(it.Value())
    it.Value().TShape().
    it.Next()
 
        

test.NbChildren()
it = TopoDS_Iterator(test)
it.Value().NbChildren()

for i in myshape:
    print(i)


from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_SOLID

topExp = TopExp_Explorer()
topExp.Init(myshape, TopAbs_SOLID)

item = topExp.Current()


#Iteration trough objects
#Find Joints and crete joint and links

for segment in step_strocture:
    segment_name, segment_color, segment_hierarchy,segment_trans = step_strocture[segment]

    if segment_name == "Joints":
        joint_strocture = segment
  
    print(segment_name)


print(joint_strocture.Location().Transformation())
print(joint_strocture.NbChildren())

for i in joint_strocture:
    print(i)
#print(joint_strocture.Composed())

v=2