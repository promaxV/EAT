import dearpygui.dearpygui as dpg

from fonts import *
from textures.eyes import *
from windows.primary_window import *

from program import *

dpg.create_context()
dpg.create_viewport(title="EyeAnnotationTool")
dpg.setup_dearpygui()

add_fonts()
add_eyes_textures()

add_main_window()
    
dpg.set_primary_window("window_primary", value=True)
    
dpg.show_viewport()
# dpg.toggle_viewport_fullscreen()

while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame()

dpg.destroy_context()