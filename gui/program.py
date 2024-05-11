import os
import cv2

import numpy as np
import pandas as pd
import dearpygui.dearpygui as dpg

from fitting import fitCircleLS

class AnnotateTab:
    def __init__(self) -> None:
        self.labels = ["pupil", "iris"]
        self.label = self.labels[0]
        self.methods = ("circle_ls", "ellipse")
        self.clear_all_data()
        
        df_columns = ["image", "image_hash"]
        objs = ("points", "circle_center_x", "circle_center_y", "circle_radius", "ellipse")
        for label in self.labels:
            for obj in objs:
                df_columns.append(label+"_"+obj)
        
        self.df = pd.DataFrame(columns=df_columns)
        
        # GUI LAYOUT
        with dpg.tab(label="Annotate", tag = "tab_annotate", parent="tab_bar", order_mode=dpg.mvTabOrder_Fixed):
            dpg.add_text("Разметка изображений")
            with dpg.table(header_row=False):
                dpg.add_table_column()
                dpg.add_table_column()
                with dpg.table_row():
                    
                    with dpg.item_handler_registry(tag = "handler_eye_image"):
                        dpg.add_item_clicked_handler(button=dpg.mvMouseButton_Left, callback = self.drawlist_leftclick_callback)
                        dpg.add_item_clicked_handler(button=dpg.mvMouseButton_Right, callback = self.drawlist_rightclick_callback)
                    
                    with dpg.table_cell():
                        with dpg.child_window(tag="subwindow_work", border=False):
                            with dpg.drawlist(height=512, width=512, tag="drawlist_eye"):
                                dpg.draw_image(texture_tag="texture_eye", tag="image_eye", pmin=(0, 0), pmax=(512, 512))
                                dpg.bind_item_handler_registry(item = "drawlist_eye", handler_registry = "handler_eye_image")
                                
                    with dpg.table_cell():
                        with dpg.child_window(tag="subwindow_sidebar"):
                            dpg.add_text("Labels")
                            dpg.add_radio_button(items=self.labels, default_value=self.label,
                                                 tag="radio_list_labels",
                                                 callback=self.label_change,
                                                 horizontal=True)
                            dpg.add_separator()
                            
                            dpg.add_checkbox(label="Окружность МНК", default_value=True, tag="checkbox_circleLS")
                            dpg.add_checkbox(label="Эллипс МНК", default_value=True, tag="checkbox_ellipse")
                            
                            with dpg.group(horizontal=True):
                                dpg.add_button(label="Построить", callback=self.fit_points)
                                dpg.add_button(label="Очистить точки", callback=self.clear_label_points)
                            dpg.add_separator()
                            
                            dpg.add_input_text(label="Источник", tag="input_source_folder", default_value="D:/Oculograph/iris_dataset/tests_png_full")
                            dpg.add_input_text(label="Выход CSV", tag="input_output_csv", default_value="D:/Oculograph/iris_dataset/data_annotation.csv")
                            dpg.add_separator()
                            
                            with dpg.group(horizontal=True):
                                dpg.add_button(label="Добавить", callback=self.add_to_df)
                                dpg.add_button(label="Отмена", callback=self.cancel_callback)
                                
                            dpg.add_button(label="Сохранить датасет", callback=self.save_dataset)
                            
        self.load_new_random_image()
 
    def clear_all_data(self):
        self.data = {}
        for label in self.labels:
            self.clear_label_data(label)
            
    def clear_label_data(self, label = None):
        if label == None:
            label = self.label
        self.data[label] = {}
        self.data[label]["points"] = []
        self.data[label]["points_tags"] = []
        for method in self.methods:
            self.data[label][method] = None
    
    def load_new_random_image(self):
        source_folder = dpg.get_value("input_source_folder")
        tests_folders = os.listdir(source_folder)

        random_test = np.random.choice(tests_folders, 1)[0]
        random_test_images = os.listdir(source_folder+"/"+random_test)
        random_test_images = list(filter(lambda x: "png" in x, random_test_images))
        
        random_image = np.random.choice(random_test_images, 1)[0]

        self.image_souce_path = source_folder+"/"+random_test+"/"+random_image
        source = cv2.imread(self.image_souce_path, cv2.IMREAD_GRAYSCALE)
        random_part = np.random.binomial(1, 0.5)
        
        if random_part == 0:
            source = source[:, :source.shape[1]//2]
        elif random_part == 1:
            source = source[:, source.shape[1]//2:]
        
        self.image = source
        
        self.image_hash = ".".join(list(map(str, cv2.img_hash.blockMeanHash(self.image, mode=1)[0])))
        if len(self.df["image_hash"].values)>0:
            if self.image_hash in self.df["image_hash"].values:
                self.load_new_random_image()
        
        img = cv2.resize(source, (512, 512))
        img_buf = [(img.flatten()/255)[::-1]]*3
        dpg.set_value("texture_eye", (np.vstack([*img_buf, np.ones((512*512)).tolist()])).T.flatten().tolist())
    
    def label_change(self):
        self.label = dpg.get_value("radio_list_labels")
    
    def drawlist_leftclick_callback(self):
        new_point_coords = dpg.get_drawing_mouse_pos()
        self.data[self.label]["points"].append(new_point_coords)
        new_point_tag = dpg.generate_uuid()
        dpg.draw_circle(new_point_coords, 1.5, 
                        color=[255, 0, 0, 255], fill=[255, 0, 0, 255], 
                        tag=new_point_tag, 
                        parent="drawlist_eye")
        self.data[self.label]["points_tags"].append(new_point_tag)
        print(self.data)
        
    def fit_points(self):
        if len(self.data[self.label]["points"]) > 1:
            if dpg.get_value("checkbox_circleLS"):
                self.data[self.label]["circle_ls"] = fitCircleLS(np.array(self.data[self.label]["points"]))
                circle_tag = self.label + "_circle"
                if dpg.does_item_exist(circle_tag):
                    dpg.delete_item(circle_tag)
                dpg.draw_circle(self.data[self.label]["circle_ls"][0], self.data[self.label]["circle_ls"][1], 
                                color=[0,255,0,255], 
                                tag = circle_tag, 
                                parent="drawlist_eye")
            if dpg.get_value("checkbox_ellipse"):
                if len(self.data[self.label]["points"])>4:
                    self.data[self.label]["ellipse"] = cv2.fitEllipse(np.array(self.data[self.label]["points"]).astype(np.float32))
                
                # THERE IS NO FUNCTION IN DPG TO DRAW ROTATED ELLIPSE
                # TODO DRAW ROTATED ELLIPSE ON IMAGE
                # box_pts = cv2.boxPoints(ellipse)
                # print(box_pts)
                # dpg.draw_ellipse(box_pts[0], box_pts[1], color=[255,0,255,255], tag="ellipse", parent="drawlist_eye")
            
    def drawlist_rightclick_callback(self):
        if self.data[self.label]["points_tags"]:
            if dpg.does_item_exist(self.data[self.label]["points_tags"][-1]):
                dpg.delete_item(self.data[self.label]["points_tags"][-1])
            self.data[self.label]["points"].pop(-1)
            self.data[self.label]["points_tags"].pop(-1)
            
    def clear_label_points(self, *, label = None):
        if label == None:
            label = self.label
        for point_tag in self.data[label]["points_tags"]:
            if dpg.does_item_exist(point_tag):
                dpg.delete_item(item=point_tag)
        
        self.data[label]["points"].clear()
        self.data[label]["points_tags"].clear()
        
    def clear_all_points(self):
        for label in self.labels:
            self.clear_label_points(label=label)
            
    def delete_label_fitting(self, label = None):
        if label == None:
            label = self.label
        self.data[label]["circle_ls"] = None
        self.data[label]["ellipse"] = None
        if dpg.does_item_exist(label+"_circle"):
            dpg.delete_item(label+"_circle")
        if dpg.does_item_exist(label+"_ellipse"):
            dpg.delete_item(label+"_ellipse")
            
    def delete_all_fitting(self):
        for label in self.labels:
            self.delete_label_fitting(label)

    def cancel_callback(self):
        self.load_new_random_image()
        self.clear_all_points()
        self.delete_all_fitting()
        self.clear_all_data()
        
        self.reset_label()
        
    def add_to_df(self):
        data_list = [self.image_souce_path, self.image_hash]
        for label in self.labels:
            data_list.append((np.array(self.data[label]["points"])/4).tolist())
            data_list.append(self.data[label]["circle_ls"][0][0]/4)
            data_list.append(self.data[label]["circle_ls"][0][1]/4)
            data_list.append(self.data[label]["circle_ls"][1]/4)
            data_list.append(self.data[label]["ellipse"])
        
        self.df.loc[len(self.df.index)] = data_list
        
        self.cancel_callback()
        
    def save_dataset(self):
        self.df.to_csv(dpg.get_value("input_output_csv"))
        print("Dataset successfully saved to", dpg.get_value("input_output_csv"))
        
    def reset_label(self):
        dpg.set_value("radio_list_labels", self.labels[0])
        self.label_change()