import cv2


def colorize_depth_cv_image(depth_img):
    depth_colormap = cv2.applyColorMap(depth_img, cv2.COLORMAP_JET)
    return depth_colormap

stream = cv2.VideoCapture('./depth_video.avi')

RUN = True

while RUN:
    ret, img = stream.read()
    cv2.imshow('i', colorize_depth_cv_image(img))
    if cv2.waitKey(30) & 0xFF == 27:
        RUN = False

stream.release()
cv2.destroyAllWindows()