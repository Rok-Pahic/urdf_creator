# from OCC.Extend.DataExchange import read_step_file_with_names_colors
#
#
# from OCC.Extend.DataExchange import read_step_file
# from OCC.Extend.DataExchange import read_step_file_with_names_colors
# from OCC.Extend.TopologyUtils import TopologyExplorer
# from OCC.Display.SimpleGui import init_display
# from OCC.Core.STEPControl import STEPControl_Reader
#
# reader=STEPControl_Reader()
#
# tr = reader.WS().TransferReader()
#
# reader.ReadFile('D:\modeling\TESTGIT.STEP')
# reader.ReadFile('D:\modeling\Assem8.STEP')
# reader.TransferRoots()
# reader.NbShapes()
# shape = reader.OneShape()
#
#
# compound = read_step_file('D:\modeling\Assem8.STEP',as_compound=False)
# compound = read_step_file('D:\modeling\TESTGIT.STEP',as_compound=False)
# compound = read_step_file_with_names_colors('D:\modeling\skelet.STEP')
#
# compound = read_step_file_with_names_colors('D:\modeling\Assem8.STEP')
#

#TRY IMPORT ASEMBLY




from OCC.Core.TDF import TDF_LabelSequence, TDF_Label





labels = TDF_LabelSequence()

# create an handle to a document
#doc = TDocStd_Document(TCollection_ExtendedString("pythonocc-doc"))

# Get root assembly
#shape_tool = XCAFDoc_DocumentTool_ShapeTool(doc.Main())
#color_tool = XCAFDoc_DocumentTool_ColorTool(doc.Main())
#shape_tool.GetFreeShapes(labels)





##
for u in compound:
    ee,ww=compound[u]
    print(ee)
    print(u.Location().Transformation().TranslationPart().X())




compound.Location().FirstDatum().Transformation().TranslationPart().X()
compound.Location().Transformation().TranslationPart().X()
compound.Location().Transformation().TranslationPart().Y()
compound.Location().Transformation().TranslationPart().Z()

t = TopologyExplorer(u)

t.number_of_vertices()
t.number_of_edges()
t.number_of_compounds()
t.number_of_comp_solids()

ver=t.compounds()

ver=t.vertices()
i=0
ver=t.edges()
for q in ver:
    i=i+1
    print(i)
    # print(q.Location().FirstDatum().Transformation().TranslationPart().X())
    # print(q.Location().FirstDatum().Transformation().TranslationPart().Y())
    # print(q.Location().FirstDatum().Transformation().TranslationPart().Z())
    print(q.Location().Transformation().TranslationPart().X())
    print(q.Location().Transformation().TranslationPart().Y())
    print(q.Location().Transformation().TranslationPart().Z())
    #print(t.number_of_edges_from_vertex(q))




q=next(ver)
t.topoFactory[5]

display, start_display, add_menu, add_function_to_menu = init_display()


# display.EraseAll()
#     for solid in t.solids():
#         color = Quantity_Color(random.random(),
#                                random.random(),
#                                random.random(),
#                                Quantity_TOC_RGB)
#         display.DisplayColoredShape(solid, color)
#     display.FitAll()
#
#


display, start_display, add_menu, add_function_to_menu = init_display()


def kocka(event=None):
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
    #display.EraseAll()
    my_box= BRepPrimAPI_MakeBox(10., 20., 30.)
    display.DisplayShape(my_box.Shape())

def valj(event=None):
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    #display.EraseAll()
    my_cylinder = BRepPrimAPI_MakeCylinder(60, 200)
    display.DisplayShape(my_cylinder.Shape())

add_menu('enostaven primer')
add_function_to_menu('enostaven primer', kocka)
add_function_to_menu('enostaven primer', valj)
display.View_Iso()
display.FitAll()

start_display()
