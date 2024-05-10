import dearpygui.dearpygui as dpg
from program import AnnotateTab

def add_main_window():
    with dpg.window(label="Primary Window", tag="window_primary", menubar=True):
        dpg.add_tab_bar(tag="tab_bar")
        
    annotate_tab = AnnotateTab()
                            
        