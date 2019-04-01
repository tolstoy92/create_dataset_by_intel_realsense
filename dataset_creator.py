import tkinter
from tkinter import Button, Entry, Label, StringVar, Text, END, font
import cv2
import PIL.Image, PIL.ImageTk
import datetime
import pyrealsense2 as rs
import numpy as np
import os
import json


class App:
    def __init__(self, window, window_title):

        self.WRITE_VIDEO = False
        self.color_video_writer = None
        self.depth_writer = None

        self.window = window

        self.window.protocol("WM_DELETE_WINDOW", self._delete_window)
        self.window.bind("<Destroy>", self._destroy)

        self.window.title(window_title)

        self.rs_width, self.rs_height, self.fps = 1280, 720, 30
        self.rs_video = RealSenseVideoCapture(self.rs_width, self.rs_height, self.fps)

        self.canvas_img = tkinter.Canvas(window, width=640, height=480)
        self.canvas_depth = tkinter.Canvas(window, width=640, height=480)
        self.canvas_img.grid(row=0, column=0)
        self.canvas_depth.grid(row=0, column=1)

        wideo_writer_button = Button(window, text='Write video', command=self.write_video)
        wideo_writer_button.grid(row=4, column=1)

        make_photo_button = Button(window, text='Make photo', command=self.make_photos)
        make_photo_button.grid(row=7, column=0)

        width_area_label = Label(self.window, text='WIDTH')
        height_area_label = Label(self.window, text='HEIGHT')
        mass_area_label = Label(self.window, text='MASS')

        self.info = Text(self.window, height=1, width = 20)
        self.info.grid(row = 8, column=0)

        self.cucumber_width = StringVar()
        self.cucumber_height = StringVar()
        self.cucumber_mass = StringVar()

        self.width_area = Entry(self.window, textvariable=self.cucumber_width)
        self.height_area = Entry(self.window, textvariable=self.cucumber_height)
        self.mass_area = Entry(self.window, textvariable=self.cucumber_mass)

        width_area_label.grid(row=1, column=0)
        self.width_area.grid(row=2, column=0)
        height_area_label.grid(row=3, column=0)
        self.height_area.grid(row=4, column=0)
        mass_area_label.grid(row=5, column=0)
        self.mass_area.grid(row=6, column=0)

        self.photo_counter = 0
        self.geom_mass_dict = {}

        self.delay = 1
        self.update()

        self.window.mainloop()

    def write_video(self):
        self.WRITE_VIDEO = not self.WRITE_VIDEO

    def write_data_in_dict(self, name, width: str, height: str, mass: str):
        try:
            w = float(width)
            h = float(height)
            m = float(mass)
            self.geom_mass_dict[name] = w, h, m
            return True
        except:
            return False

    def make_photos(self):
        self.info.delete('1.0', END)
        time = str(datetime.datetime.now())[:-3]
        if self.cucumber_width.get() and self.cucumber_height.get() and self.cucumber_mass.get():
            if self.write_data_in_dict(time, self.cucumber_width.get(),
                                       self.cucumber_height.get(), self.cucumber_mass.get()):
                photos_dir = 'photos'
                if not photos_dir in list(os.listdir(os.getcwd())):
                    os.mkdir(os.path.join(os.getcwd(), photos_dir))
                path = os.path.join(os.getcwd(), photos_dir)
                color_photo_name = 'image.png'
                depth_photo_name = 'depth.png'

                cv2.imwrite(os.path.join(path, time + '_' + color_photo_name), self.image)
                cv2.imwrite(os.path.join(path, time + '_' + depth_photo_name), self.rgb_depth)
                self.photo_counter += 1
                self.width_area.delete(0, 'end')
                self.height_area.delete(0, 'end')
                self.mass_area.delete(0, 'end')

                self.info["bg"] = 'green'
                self.info.insert(END, 'Saved photo #{}!'.format(self.photo_counter))
        else:
            self.info["bg"] = 'red'
            self.info.insert(END, 'Wrong data!'.format(self.photo_counter))

    def update(self):

        color_frame, depth_frame = self.rs_video.get_aligned_frames()
        self.image = self.rs_video.rs_frame_to_cv_image(color_frame)
        self.img_to_show = self.image.copy()

        depth_cv = self.rs_video.rs_frame_to_cv_image(depth_frame)
        depth_cv = self.rs_video.rechannel_depth(depth_cv)
        self.rgb_depth = cv2.cvtColor(depth_cv, cv2.COLOR_GRAY2BGR)

        depth_colormap = self.rs_video.colorize_depth_cv_image(self.rgb_depth)

        if self.WRITE_VIDEO:
            video_folder = self.create_video_folder()
            self.write_videos(video_folder)

        else:
            self.stop_video_writers()

        image = cv2.cvtColor(self.img_to_show, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (640, 480))
        depth_colormap = cv2.cvtColor(depth_colormap, cv2.COLOR_BGR2RGB)
        depth_colormap = cv2.resize(depth_colormap, (640, 480))

        self.pil_img = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(image))
        self.pil_depth = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(depth_colormap))

        self.canvas_img.create_image(0, 0, image=self.pil_img, anchor=tkinter.NW)
        self.canvas_depth.create_image(0, 0, image=self.pil_depth, anchor=tkinter.NW)

        self.window.after(self.delay, self.update)

    def write_videos(self, all_videos_folder):
        if not self.color_video_writer or not self.depth_writer:

            self.color_video_writer = VideoWriter(self.fps, (self.rs_width, self.rs_height))
            self.depth_writer = VideoWriter(self.fps, (self.rs_width, self.rs_height))

            video_folder = self.color_video_writer.create_path_to_save_video(all_videos_folder)

            color_video_name = 'color_video.avi'
            depth_video_name = 'depth_video.avi'

            self.color_video_writer.init_writer(os.path.join(video_folder, color_video_name))
            self.depth_writer.init_writer(os.path.join(video_folder, depth_video_name))
        else:
            self.color_video_writer.write_frame(self.image)
            self.depth_writer.write_frame(self.rgb_depth)

        cv2.circle(self.img_to_show, (50, 50), 7, (0, 0, 255), 20)
        cv2.putText(self.img_to_show, 'REC', (83, 70), 1, cv2.FONT_HERSHEY_COMPLEX, (0, 0, 255), 3)

    def stop_video_writers(self):
        if self.color_video_writer:
            self.color_video_writer.stop()
            self.color_video_writer = None
        if self.depth_writer:
            self.depth_writer.stop()
            self.depth_writer = None

    def create_video_folder(self):
        video_folder_name = 'videos'
        path_to_video_folder = os.path.join(os.getcwd(), video_folder_name)
        if not video_folder_name in os.listdir(os.getcwd()):
            os.mkdir(path_to_video_folder)
        return video_folder_name

    def cut_img(self, img, x_right, x_left, y_top, y_bot):
        img = img[y_top: -y_bot, x_right: -x_left]
        return img

    def _delete_window(self):
        try:
            self.window.destroy()
        except:
            pass

    def _destroy(self, event):
        try:
            self.rs_video.stop()
        except:
            pass
        try:
            self.color_video_writer.stop()
        except:
            pass
        try:
            self.depth_writer.stop()
        except:
            pass
        try:
            anat_file_name = 'annotation.json'
            if anat_file_name in os.listdir(os.getcwd()):
                with open(os.path.join(os.getcwd(), anat_file_name)) as fp:
                    data = json.load(fp)
            else:
                data = {}
            data.update(self.geom_mass_dict)

            with open(os.path.join(os.getcwd(), anat_file_name), 'w') as fp:
                json.dump(data, fp)
        except:
            pass

class RealSenseVideoCapture:
    def __init__(self, video_width, video_height, fps):
        self.pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.depth, video_width, video_height, rs.format.z16, fps)
        config.enable_stream(rs.stream.color, video_width, video_height, rs.format.bgr8, fps)
        self.pipeline.start(config)

    def get_rs_frames(self):
        return self.pipeline.wait_for_frames()

    def rs_frame_to_cv_image(self, frame):
        cv_image = np.asanyarray(frame.get_data())
        return cv_image

    def rechannel_depth(self, depth_img):
        depth = cv2.convertScaleAbs(depth_img, alpha=0.03)
        return depth

    def colorize_depth_cv_image(self, depth_img):
        depth_colormap = cv2.applyColorMap(depth_img, cv2.COLORMAP_JET)
        return depth_colormap

    def get_aligned_frames(self):
        align = rs.align(rs.stream.color)
        frameset = self.get_rs_frames()
        frameset = align.process(frameset)
        aligned_depth_frame = frameset.get_depth_frame()
        color_frame = frameset.get_color_frame()
        return color_frame, aligned_depth_frame

    def stop(self):
        self.pipeline.stop()


class VideoWriter():
    def __init__(self, fps, resolution):
        self.fps = fps
        self.resolution = resolution
        self.fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')

    def init_writer(self, path_to_save):
        self.writer = cv2.VideoWriter(path_to_save, self.fourcc, self.fps, self.resolution)

    def write_frame(self, frame):
        if self.writer:
            self.writer.write(frame)

    def stop(self):
        self.writer.release()

    def create_path_to_save_video(self, all_videos_folder):
        PWD = os.getcwd()
        path_to_save_video = os.path.join(PWD, all_videos_folder, str(datetime.datetime.now())[:-4])
        os.mkdir(path_to_save_video)
        return path_to_save_video


# Create a window and pass it to the Application object
App(tkinter.Tk(), "RealSense dataset creator")