import dearpygui.dearpygui as dpg

def add_fonts():
    with dpg.font_registry():
        with dpg.font("./gui/fonts/Roboto-Regular.ttf", 16, tag="default_font"):
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
            
    dpg.bind_font("default_font")