from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()

display.DisplayShape(u)
display.View_Iso()
display.FitAll()
start_display()

u.__class__