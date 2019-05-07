import cv2
import datetime
import pyrealsense2 as rs
import numpy as np
import os
from time import sleep
from playsound import playsound

sleep_time = 60
max_session_counter = 1000


def check_dir(root_dir, dir_name):
    if not dir_name in os.listdir(root_dir):
        path = os.path.join(root_dir, dir_name)
        os.mkdir(path)


def create_photo_name(counter):
    photo_format = '.png'
    return str(counter) + photo_format


def get_aligned_frames(rs_frames):
    align = rs.align(rs.stream.color)
    frameset = rs_frames
    frameset = align.process(frameset)
    aligned_depth_frame = frameset.get_depth_frame()
    color_frame = frameset.get_color_frame()
    return color_frame, aligned_depth_frame


def rs_frame_to_cv_image(frame):
    cv_image = np.asanyarray(frame.get_data())
    return cv_image


def rechannel_depth(depth_img, alpha=0.05):
    depth = cv2.convertScaleAbs(depth_img, alpha=alpha)
    return depth


def create_counter(dir):
    f_names = os.listdir(dir)
    nums = list( int(num[:-4]) for num in f_names)
    if len(nums):
        return max(nums)
    else:
        return 0


photos_dir_name = 'autosaved_photos'
rgb_photos_dir_name = 'rgb_photos'
depth_photos_dir_name = 'depth_maps'

root_dir = os.getcwd()
photos_path = os.path.join(root_dir, photos_dir_name)
rgb_path = os.path.join(photos_path, rgb_photos_dir_name)
depth_path = os.path.join(photos_path, depth_photos_dir_name)

check_dir(root_dir, photos_dir_name)
check_dir(photos_path, rgb_photos_dir_name)
check_dir(photos_path, depth_photos_dir_name)

files_counter = create_counter(rgb_path)

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
pipeline.start(config)

RUN = True
cv2.namedWindow('img', cv2.WINDOW_NORMAL)
cv2.resizeWindow('img', 640, 720)

frames_counter = 0

sleep(30)
playsound('start.mp3')
session_counter = 0

while RUN and session_counter < max_session_counter:
    rs_frames = pipeline.wait_for_frames()
    color_frame, depth_frame = get_aligned_frames(rs_frames)
    img = rs_frame_to_cv_image(color_frame)
    depth = rs_frame_to_cv_image(depth_frame)
    depth = rechannel_depth(depth)
    depth_to_show = cv2.cvtColor(depth.copy(), cv2.COLOR_GRAY2BGR)
    frames_counter += 1
    result = np.vstack((img.copy(), depth_to_show))
    cv2.putText(result, str(frames_counter), (20, 35), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 4)
    cv2.imshow('img', result)
    if frames_counter >= 20:
        img_save_path = os.path.join(rgb_path, create_photo_name(files_counter))
        depth_save_path = os.path.join(depth_path, create_photo_name(files_counter))
        cv2.imwrite(img_save_path, img)
        cv2.imwrite(depth_save_path, depth)
        files_counter += 1
        frames_counter = 0
        session_counter += 1
    if cv2.waitKey(10) & 0xFF == 27:
        RUN = False

cv2.destroyAllWindows()
pipeline.stop()

playsound('bell.mp3')

