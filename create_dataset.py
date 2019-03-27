import pyrealsense2 as rs
import numpy as np
import cv2
from copy import deepcopy as dcopy
import os
import datetime
from collections import namedtuple as ntuple
import json


def create_video_writer(video_name: str, resolution=(1280, 720)):
    fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
    out = cv2.VideoWriter(video_name, fourcc, 30.0, resolution)
    return out

# Configure depth and color streams
IMAGE_W, IMAGE_H = 1280, 720

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, IMAGE_W, IMAGE_H, rs.format.z16, 30)
config.enable_stream(rs.stream.color, IMAGE_W, IMAGE_H, rs.format.bgr8, 30)

# Start streaming
pipeline.start(config)

PWD = os.getcwd()
videos_folder = os.path.join(PWD, 'videos')
images_folder = os.path.join(PWD, 'images')


Cucumber = ntuple('Cucumber', ['HEIGHT', 'WIDTH', 'MASS',])

color_video_name = 'color_video'
depth_video_name = 'depth_video'
colored_depth_video_name = 'colored_depth_video'

color_video = None
depth_video = None
colored_depth_video = None

WRITE_VIDEO = False
REC = False

def n():
    pass

def write_video(*args):
    global WRITE_VIDEO, REC, color_video, depth_video, colored_depth_video
    switcher = cv2.getTrackbarPos('write_video','RealSense')
    if switcher == 0:
        WRITE_VIDEO = False
        if REC:
            streams = [color_video, depth_video, colored_depth_video]
            for s in streams:
                if s:
                    print(s, 'released!')
                    s.release()
            REC = False
    else:
        WRITE_VIDEO = True

def write_photos(*args):
    global image_folder_created, dir_name
    switcher = cv2.getTrackbarPos('write_photo', 'RealSense')
    if switcher == 1:
        if not image_folder_created:
            dir_name = str(datetime.datetime.now().time())[:-2]
            os.mkdir(dir_name)
            image_folder_created = True
        img_name = str(datetime.datetime.now().time())
        path_to_save = os.path.join(dir_name, img_name)
        color = '_color.png'
        depth = '_depth.png'
        colored_depth = '_colored_depth.png'
        cv2.imwrite(path_to_save + color, color_image)
        cv2.imwrite(path_to_save + depth, rgb_depth_img)
        cv2.imwrite(path_to_save + colored_depth, depth_colormap)
        print('{} saved!!!'.format(img_name))

        H = input('Enter HEIGHT: ')
        W = input('Enter WIDTH: ')
        M = input('Enter MASS: ')

        cucumbers_dict[img_name] = Cucumber(H, W, M)
        print("Cucumber's parameters are saved!")
        cv2.setTrackbarPos('write_photo', 'RealSense', 0)

cv2.namedWindow('RealSense', cv2.WINDOW_NORMAL)
cv2.createTrackbar('write_video', 'RealSense', 0, 1, write_video)
cv2.createTrackbar('write_photo', 'RealSense', 0, 1, write_photos)
cv2.createButton('b', n, 'RealSense')


cucumbers_dict = {}

image_folder_created = False
dir_name = None

try:
    while True:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue
        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        
        color_img_to_show = dcopy(color_image)
        depth_image_to_show = dcopy(depth_image)
        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        
        # Stack both images horizontally
        rgb_depth_img = cv2.cvtColor(cv2.convertScaleAbs(depth_image_to_show, alpha=0.03), cv2.COLOR_GRAY2BGR)
        
        images = np.vstack((color_img_to_show, depth_colormap))
        
        if WRITE_VIDEO:
            if not REC:
                video_folder = os.path.join(PWD, str(datetime.datetime.now().time())[:-4])
                os.mkdir(video_folder)
                color_video_name = os.path.join(PWD, video_folder, 'color_video.avi')
                depth_video_name = os.path.join(PWD, video_folder, 'depth_video.avi')
                colored_depth_video_name = os.path.join(PWD, video_folder, 'colored_depth_video.avi')

                color_video = create_video_writer(color_video_name, (IMAGE_W, IMAGE_H))
                depth_video = create_video_writer(depth_video_name, (IMAGE_W, IMAGE_H))
                colored_depth_video = create_video_writer(colored_depth_video_name, (IMAGE_W, IMAGE_H))
                REC = True
            else:
                cv2.circle(images, (50, 50), 15, (0, 0, 255), 30)
                cv2.putText(images, 'REC', (83, 70), 1, cv2.FONT_HERSHEY_COMPLEX, (0, 0, 255), 5)
                color_video.write(color_image)
                depth_video.write(rgb_depth_img)
                colored_depth_video.write(depth_colormap)
            
        
        cv2.imshow('RealSense', images)

        if cv2.waitKey(1) & 0xFF == 27:
            break

finally:
    if len(cucumbers_dict):
        with open(dir_name + '.json', 'w') as fp:
            json.dump(cucumbers_dict, fp)
    cv2.destroyAllWindows()
    streams = [color_video, depth_video, colored_depth_video]
    for s in streams:
        if s:
            s.release()
    pipeline.stop()
