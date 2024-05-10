import numpy as np
import dearpygui.dearpygui as dpg

def add_eyes_textures():
    
    db_root_folder = "./ADD FOLDER HERE"
    
    with dpg.texture_registry():
        dpg.add_dynamic_texture(width = 512, height = 512,
                                default_value = np.full((512*512*4), 1),
                                tag = "texture_eye")